import discord  # type: ignore
from discord.ext import commands  # type: ignore
import yt_dlp  # type: ignore
import spotipy  # type: ignore
from spotipy.oauth2 import SpotifyClientCredentials  # type: ignore
import asyncio
import re
import os
import random as rand


BOT_TOKEN = ""
SPOTIPY_CLIENT_ID = ""
SPOTIPY_CLIENT_SECRET = ""
CREED_FILE = "Creed Playlist.txt"

playlists = [
    "Creed Playlist.txt"
]

YTDLP_OPTS = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "cookiefile": "/home/pi/youtube_cookies.txt",
    "extractor_args": {
        "youtube": {
            "player_client": ["default", "web_safari"],
        }
    },
}

YOUTUBE_SEARCH_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "extractor_args": {
        "youtube": {
            "player_client": ["default", "web_safari"],
        }
    },
}

class GuildVoiceState:
    def __init__(self):
        self.vc: discord.VoiceClient | None = None
        self.lock = asyncio.Lock()
        self.play_lock = asyncio.Lock()
        self.queue = []
        self.is_playing = False
        self.last_song = None
        self.autoplay = False
        self.history = []
        self.playlist_mode = False

guild_states: dict[int, GuildVoiceState] = {}

def get_state(guild: discord.Guild) -> GuildVoiceState:
    if guild.id not in guild_states:
        guild_states[guild.id] = GuildVoiceState()
    return guild_states[guild.id]

async def ensure_voice(ctx_or_interaction) -> discord.VoiceClient:
    guild = ctx_or_interaction.guild
    state = get_state(guild)

    user = (
        ctx_or_interaction.author
        if hasattr(ctx_or_interaction, "author")
        else ctx_or_interaction.user
    )

    if not user or not user.voice or not user.voice.channel:
        raise RuntimeError("User not in voice channel")
    
    channel = user.voice.channel
    
    async with state.lock:
        if state.vc and state.vc.is_connected():
            if state.vc.channel != channel:
                await state.vc.move_to(channel)
        else:
            state.vc = await channel.connect(
                timeout=60,
                reconnect=True
            )
    return state.vc

bot = commands.Bot(command_prefix="?", intents=discord.Intents.all())

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

last_controls_message = None

async def extract_with_timeout(extract_func, timeout=20.0):
    loop = asyncio.get_event_loop()
    return await asyncio.wait_for(
        loop.run_in_executor(None, extract_func),
        timeout=timeout
    )

async def skip_track(guild):
    state = get_state(guild)
    if state.vc and state.vc.is_playing():
        state.vc.stop()
        return True
    return False

async def stop_playback(guild):
    state = get_state(guild)
    state.queue.clear()
    state.is_playing = False

    if state.vc:
        await state.vc.disconnect()
        state.vc = None

async def clear_queue(guild):
    state = get_state(guild)
    state.queue.clear()

async def search_youtube(query):
    def extract():
        with yt_dlp.YoutubeDL({
            **YTDLP_OPTS,
            'default_search': 'ytsearch1'
        }) as ydl:
            return ydl.extract_info(query, download=False)

    try:
        result = await extract_with_timeout(extract, timeout=20.0)
        entry = result["entries"][0]

        return {
            "title": entry.get("title"),
            "url": entry["url"],
        }

    except asyncio.TimeoutError:
        return {"error": "timeout"}

    except Exception as e:
        print(f"YouTube search error: {e}")
        return None

async def search_youtube_multi(query, limit=5):

    def extract():
        with yt_dlp.YoutubeDL({
            **YTDLP_OPTS,
            'default_search': f'ytsearch{limit}'
        }) as ydl:
            return ydl.extract_info(query, download=False)
    try:
        result = await extract_with_timeout(extract, timeout=25.0)

        if not result or "entries" not in result:
            return None

        videos = []
        for entry in result["entries"]:
            if not entry:
                continue
                
            video_id = entry.get("id")
            title = entry.get("title", "Unknown")
            
            if not video_id:
                continue
            
            videos.append({
                "title": title,
                "url": f"https://www.youtube.com/watch?v={video_id}"
            })

        return videos if videos else None
    
    except asyncio.TimeoutError:
        return {"error": "timeout"}
    
    except Exception as e:
        print(f"Youtube multi search error: {e}")
        import traceback
        traceback.print_exc()
        return None
    
async def get_recommended_song(state):

    search_query = f"{state.last_song} music"

    results = await search_youtube_multi(search_query, 5)

    if not results or isinstance(results, dict):
        return None

    # remove recently played songs
    filtered = [r for r in results if r["title"] not in state.history]

    if not filtered:
        filtered = results

    return rand.choice(filtered)

async def ensure_autoplay_queue(state):

    if not state.autoplay:
        return
    
    if len(state.queue) > 0:
        return
    
    if not state.last_song:
        return
    
    rec = await get_recommended_song(state)

    if rec:
        print("Prefetched autoplay:", rec["title"])
        state.queue.append(rec)

async def slowly_add_playlist(ctx, playlist, delay=60):
    state = get_state(ctx.guild)

    for video in playlist:
        # stop if playlist mode gets turned off
        if not state.playlist_mode:
            break

        state.queue.append(video)

        try:
            await ctx.send(f"Queued: {video['title']}")
        except:
            pass

        await asyncio.sleep(delay)
    
async def play_next(ctx_or_interaction):

    global last_controls_message

    guild = ctx_or_interaction.guild
    state = get_state(guild)

    async with state.play_lock:

        if not state.queue:

            await ensure_autoplay_queue(state)

            if not state.queue:
                state.is_playing = False

                if state.vc:
                    await state.vc.disconnect()
                    state.vc = None

                return

        state.is_playing = True
        video = state.queue.pop(0)

        # Connect to voice FIRST
        vc = await ensure_voice(ctx_or_interaction)

        if not vc or not vc.is_connected():
            print("Voice connection failed — aborting play.")

            state.is_playing = False

            if state.vc:
                await state.vc.disconnect()
                state.vc = None

            return

        # Resolve YouTube page URL AFTER voice connection
        if "youtube.com/watch" in video["url"]:

            resolved = await handle_youtube_url(video["url"])

            if not resolved:
                # Skip broken video and move to next
                state.is_playing = False
                await play_next(ctx_or_interaction)
                return

            video = resolved

        state.last_song = video["title"]

        state.history.append(video["title"])

        if len(state.history) > 10:
            state.history.pop(0)

        await ensure_autoplay_queue(state)

        ffmpeg_options = {
            "before_options": (
                "-reconnect 1 "
                "-reconnect_streamed 1 "
                "-reconnect_at_eof 1 "
                "-reconnect_delay_max 5 "
                "-rw_timeout 15000000 "
                "-nostdin"
            ),
            "options": "-vn -bufsize 512k",
        }

        try:

            vc.play(
                discord.FFmpegPCMAudio(
                    video["url"],
                    **ffmpeg_options
                ),
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    play_next(ctx_or_interaction),
                    bot.loop,
                ),
            )

        except discord.ClientException as e:

            print(f"Play failed: {e}")
            state.is_playing = False
            return

        if last_controls_message:

            try:
                await last_controls_message.delete()

            except Exception:
                pass

        last_controls_message = await ctx_or_interaction.send(
            f"Now Playing: {video['title']}",
            view=MusicControls()
        )

async def handle_spotify_track(url):
    track_info = sp.track(url)
    track_name = track_info['name']
    artist_name = track_info['artists'][0]['name']
    return f"{track_name} by {artist_name}"

async def handle_youtube_url(url):
    def extract():
        with yt_dlp.YoutubeDL(YTDLP_OPTS) as ydl:
            return ydl.extract_info(url, download=False)

    try:
        result = await extract_with_timeout(extract, timeout=20.0)

        return {
            "title": result.get("title"),
            "url": result["url"],  # direct audio stream
        }

    except asyncio.TimeoutError:
        return {"error": "timeout"}

    except Exception as e:
        print(f"YouTube URL error: {e}")
        return None
    
async def handle_youtube_playlist(url):

    if "list=" in url:
        url = url.split("&")[0] + "&list=" + url.split("list=")[1]

    def extract():
      with yt_dlp.YoutubeDL({
        'format': 'bestaudio/best',
        'quiet': True,
        'extract_flat': 'in_playlist',  # ✅ better than True
        'ignoreerrors': True,           # ✅ prevents crashes on bad vids
        'noplaylist': False,            # ✅ force playlist ON
        'playlistend': None,            # ✅ no limit  
        }) as ydl:
            return ydl.extract_info(url, download=False)

    try:
        result = await extract_with_timeout(extract, timeout=30.0)

        if not result or "entries" not in result:
            return None

        videos = []
        for entry in result["entries"]:
            if not entry:
                continue

            videos.append({
                "title": entry.get("title"),
                # turn ID into a normal YouTube URL
                "url": f"https://www.youtube.com/watch?v={entry.get('id')}"
            })

        return videos

    except asyncio.TimeoutError:
        return {"error": "timeout"}

    except Exception as e:
        print(f"Playlist error: {e}")
        return None
    
async def add_to_queue(ctx_or_interaction, video):
    state = get_state(ctx_or_interaction.guild)
    state.queue.append(video)

    if not state.is_playing:
        await play_next(ctx_or_interaction)

async def do_skip(ctx):
    state = get_state(ctx.guild)
    if state.vc and state.vc.is_playing():
        state.vc.stop()
        await ctx.send("Skipped.")
    else:
        await ctx.send("Nothing is playing.")

class PlayModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Play a Song")
        self.song_input = discord.ui.TextInput(
            label="Song name or URL",
            placeholder="Enter a song name or YouTube/Spotify URL...",
            required=True,
            max_length=200
        )
        self.add_item(self.song_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Acknowledge the interaction
        # Use interaction directly instead of ctx
        await play(interaction, x=self.song_input.value)

class MusicControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="▶️ Play", style=discord.ButtonStyle.success)
    async def play_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PlayModal())

    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.primary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if await skip_track(interaction.guild):
            await interaction.followup.send("Skipped.", ephemeral=True)
        else:
            await interaction.followup.send("Nothing is playing.", ephemeral=True)

    @discord.ui.button(label="🚫 Disconnect", style=discord.ButtonStyle.red)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await stop_playback(interaction.guild)

    @discord.ui.button(label="🧹 Clear", style=discord.ButtonStyle.green)
    async def clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await clear_queue(interaction.guild)

    @discord.ui.button(label="🎸 Creed", style=discord.ButtonStyle.secondary)
    async def creed(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await ensure_voice(interaction)

        ctx = await bot.get_context(interaction.message)
        await ctx.invoke(bot.get_command("creed"), num_songs=1)

@bot.command()
async def playlist(ctx):
    state = get_state(ctx.guild)

    state.playlist_mode = not state.playlist_mode

    status = "enabled" if state.playlist_mode else "disabled"
    await ctx.send(f"Playlist mode {status}")

@bot.command()
async def play(ctx, *, x):

    if not ctx.author.voice: 
        await ctx.send("You must be in a voice channel to play music!")
        return
    
    spotify_track_pattern = re.compile(r'https://open\.spotify\.com/track/')
    youtube_url_pattern = re.compile(r'(https?://)?(www\.)?(youtube|youtu)\.(com|be)/')

    video = None

    # Spotify URL → search
    if spotify_track_pattern.match(x):
        query = await handle_spotify_track(x)
        video = await search_youtube(query)

    # YouTube URL → direct resolve
    elif youtube_url_pattern.match(x):
        state = get_state(ctx.guild)

    # 🎵 PLAYLIST MODE ON → slow loading
        if state.playlist_mode and "list=" in x:
            playlist = await handle_youtube_playlist(x)

        # timeout handling
            if isinstance(playlist, dict) and playlist.get("error") == "timeout":
                await ctx.send("⏱️ Playlist took too long to load.")
                return

            if not playlist:
                await ctx.send("Failed to load playlist.")
                return

            await ctx.send(f"Loading playlist... ({len(playlist)} songs)")

        # ✅ Add first few instantly
            initial = playlist[:3]
            rest = playlist[3:]

            for vid in initial:
                state.queue.append(vid)

            if not state.is_playing:
                await play_next(ctx)

        # ✅ Slowly add the rest
            bot.loop.create_task(slowly_add_playlist(ctx, rest, delay=30))

            return

    # 🎵 NORMAL VIDEO
        else:
            video = await handle_youtube_url(x)

    # Plain text → search
    else:
        video = await search_youtube(x)

    # Timeout handling
    if isinstance(video, dict) and video.get("error") == "timeout":
        await ctx.send("⏱️ YouTube took too long to respond. Try again.")
        return

    if not video:
        await ctx.send(f"Sorry, I couldn't find a song matching '{x}'.")
        return

    await add_to_queue(ctx, video)
    await ctx.send(f"Added to queue: {video['title']}")

@bot.command()
async def skip(ctx):
    if await skip_track(ctx.guild):
        await ctx.send("Skipped")
    else:
        await ctx.send("Nothing is playing.")

@bot.command()
async def stop(ctx):
    await stop_playback(ctx.guild)
    await ctx.send("Stopped")

@bot.command()
async def clear(ctx): 
    await clear_queue(ctx.guild)
    await ctx.send("Queue Cleared")


@bot.command()
async def creed(ctx, num_songs: int = 1):
    if os.path.exists(CREED_FILE):
        with open(CREED_FILE, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
            if lines:
                num_songs = min(num_songs, len(lines))
                for _ in range(num_songs):
                    random_song = rand.choice(lines)
                    await play(ctx, x=random_song)
            else:
                await ctx.send("The Creed Playlist is empty.")
    else:
        await ctx.send("The Creed Playlist file does not exist")
    
try:
    print("about to run the bot...")
    bot.run(BOT_TOKEN)
except Exception as e:
    print("Exception occurred before bot.run:", e)


