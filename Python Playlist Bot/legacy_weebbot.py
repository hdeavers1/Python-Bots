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
PLAYLIST_FILE = "Current Playlist.txt"
COUNTRY_FILE = "Country Playlist.txt"
RAP_FILE = "Rap Playlist.txt"
ROCK_FILE = "Rock Playlist.txt"
METAL_FILE = "Metal Playlist.txt"
POP_FILE = "Pop Playlist.txt"
EIGHTYs_FILE = "80s Playlist.txt"
NINETYs_FILE = "90s Playlist.txt"
TWOTHOUSANDs_FILE = "2000s Playlist.txt"
TWENTYTENs_FILE = "2010s Playlist.txt"
CREED_FILE = "Creed Playlist.txt"

playlists = [
    "Current Playlist.txt",
    "Country Playlist.txt",
    "Rap Playlist.txt",
    "Rock Playlist.txt",
    "Metal Playlist.txt",
    "Pop Playlist.txt",
    "80s Playlist.txt",
    "90s Playlist.txt",
    "2000s Playlist.txt",
    "2010s Playlist.txt",
    "Creed Playlist.txt"
]

bot = commands.Bot(command_prefix="?", intents=discord.Intents.all())

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

queue = []
is_playing = False
vc = None
last_controls_message = None

async def search_youtube(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'default_search': 'ytsearch1',
        'quiet': True,
    }
    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=False))
            return result['entries'][0]
        except Exception as e:
            print(f"Error occurred: {e}")
            return None

async def play_next(ctx_or_interaction):
    global is_playing, vc, last_controls_message
    if len(queue) > 0:
        is_playing = True
        video_info = queue.pop(0)
        video_url = video_info['url']
        video_title = video_info['title']

        # Get user/voice channel from context or interaction
        voice_channel = None
        user = None
        if hasattr(ctx_or_interaction, 'author') and ctx_or_interaction.author:
            user = ctx_or_interaction.author
        elif hasattr(ctx_or_interaction, 'user') and ctx_or_interaction.user:
            user = ctx_or_interaction.user
        if user and hasattr(user, 'voice') and user.voice:
            voice_channel = user.voice.channel

        if not vc or not vc.is_connected():
            if not voice_channel:
                if hasattr(ctx_or_interaction, 'send'):
                    await ctx_or_interaction.send("You must be in a voice channel to play music!")
                elif hasattr(ctx_or_interaction, 'response'):
                    await ctx_or_interaction.response.send_message("You must be in a voice channel to play music!", ephemeral=True)
                is_playing = False
                return
            try:
                vc = await voice_channel.connect()
            except Exception as e:
                print(f"Voice connect failed: {e}")
                if hasattr(ctx_or_interaction, 'send'):
                    await ctx_or_interaction.send("Failed to connect to voice channel. Please try again later.")
                elif hasattr(ctx_or_interaction, 'response'):
                    await ctx_or_interaction.response.send_message("Failed to connect to voice channel. Please try again later.", ephemeral=True)
                is_playing = False
                return

        if not vc or not vc.is_connected():
            if hasattr(ctx_or_interaction, 'send'):
                await ctx_or_interaction.send("Not connected to voice. Cannot play audio.")
            elif hasattr(ctx_or_interaction, 'response'):
                await ctx_or_interaction.response.send_message("Not connected to voice. Cannot play audio.", ephemeral=True)
            is_playing = False
            return

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
            'options': '-vn'
        }
        try:
            vc.play(discord.FFmpegPCMAudio(video_url, **ffmpeg_options), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx_or_interaction), bot.loop))
        except discord.ClientException as e:
            print(f"ClientException: {e}")
            if hasattr(ctx_or_interaction, 'send'):
                await ctx_or_interaction.send("Not connected to voice. Cannot play audio.")
            elif hasattr(ctx_or_interaction, 'response'):
                await ctx_or_interaction.response.send_message("Not connected to voice. Cannot play audio.", ephemeral=True)
            is_playing = False
            return

        # Delete previous controls message if it exists
        if last_controls_message:
            try:
                await last_controls_message.delete()
            except Exception:
                pass
        # Send new playing message with controls
        if hasattr(ctx_or_interaction, 'send'):
            last_controls_message = await ctx_or_interaction.send(f"Playing: {video_title}", view=MusicControls())
        elif hasattr(ctx_or_interaction, 'channel'):
            last_controls_message = await ctx_or_interaction.channel.send(f"Playing: {video_title}", view=MusicControls())
        print(f"Playing: {video_title}")
    else:
        is_playing = False
        if vc:
            try:
                await vc.disconnect()
            except Exception as e:
                print(f"Error disconnecting: {e}")
            vc = None

async def handle_spotify_track(url):
    track_info = sp.track(url)
    track_name = track_info['name']
    artist_name = track_info['artists'][0]['name']
    return f"{track_name} by {artist_name}"

async def handle_youtube_url(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
    }
    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            video_title = result['title']
            return {"title": video_title, "url": url}
        except Exception as e:
            print(f"Error occurred: {e}")
            return None

async def add_to_queue(ctx_or_interaction, video_info):
    global is_playing
    # Check if user is in a voice channel before adding to queue
    voice_channel = None
    user = None
    # Accept both Context and Interaction
    if hasattr(ctx_or_interaction, 'author') and ctx_or_interaction.author:
        user = ctx_or_interaction.author
    elif hasattr(ctx_or_interaction, 'user') and ctx_or_interaction.user:
        user = ctx_or_interaction.user
    if user and hasattr(user, 'voice') and user.voice:
        voice_channel = user.voice.channel
    if not voice_channel:
        if hasattr(ctx_or_interaction, 'send'):
            await ctx_or_interaction.send("You must be in a voice channel to play music!")
        elif hasattr(ctx_or_interaction, 'response'):
            await ctx_or_interaction.response.send_message("You must be in a voice channel to play music!", ephemeral=True)
        return
    queue.append(video_info)
    if not is_playing:
        await play_next(ctx_or_interaction)

async def do_skip(ctx):
    global vc
    if vc and vc.is_playing():
        vc.stop()
        # Send message depending on context type
        if hasattr(ctx, 'send'):
            await ctx.send("Skipping current song...")
        elif hasattr(ctx, 'response'):
            await ctx.response.send_message("Skipping current song...", ephemeral=True)
    else:
        if hasattr(ctx, 'send'):
            await ctx.send("No song is currently playing.")
        elif hasattr(ctx, 'response'):
            await ctx.response.send_message("No song is currently playing.", ephemeral=True)

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
        await do_skip(interaction)

    @discord.ui.button(label="🚫 Disconnect", style=discord.ButtonStyle.red)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await stop(interaction)

    @discord.ui.button(label="🧹 Clear", style=discord.ButtonStyle.green)
    async def clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await clear(interaction)

    @discord.ui.button(label="🎸 Creed", style=discord.ButtonStyle.secondary)
    async def creed(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        global vc
        if not vc or not vc.is_connected():
            if interaction.user.voice and interaction.user.voice.channel:
                vc = await interaction.user.voice.channel.connect()
            else:
                await interaction.response.send_message("You must be in a voice channel to use this button!", ephemeral=True)
                return
        ctx = await bot.get_context(interaction.message)
        await ctx.invoke(bot.get_command("creed"), num_songs=1)
@bot.command()
async def play(ctx, *, x):
    # Regular expressions to match Spotify and YouTube URLs
    spotify_track_pattern = re.compile(r'https://open\.spotify\.com/track/(\w+)')
    youtube_url_pattern = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+')

    if spotify_track_pattern.match(x):
        # Handle Spotify URL
        query = await handle_spotify_track(x)
    elif youtube_url_pattern.match(x):
        # Extract title from YouTube URL and use it as a query
        video_info = await handle_youtube_url(x)
        if video_info:
            query = video_info['title']
    else:
        # Handle a general search query
        query = x

    # Perform a search on YouTube using the query
    video_info = await search_youtube(query)

    if video_info:
        await add_to_queue(ctx, video_info)
        await ctx.send(f"Added to queue: {video_info['title']}")
        print(f"Added to queue: {video_info['title']}")
    else:
        await ctx.send(f"Sorry, I couldn't find a song matching '{x}'.")

@bot.command()
async def skip(ctx):
    await do_skip(ctx)

@bot.command()
async def clear(ctx): 
    global queue
    if queue:
        queue.clear()
        await ctx.send("Queue Cleared.")
        print("Queue Cleared.")
    else:
        await ctx.send("The queue is already empty.")

@bot.command()
async def shuffle(ctx, playlist: str):

    if playlist == "rock":
        playlist_shuffled = ROCK_FILE 
    elif playlist == "metal":
        playlist_shuffled = METAL_FILE
    elif playlist == "country":
        playlist_shuffled = COUNTRY_FILE
        playlist_shuffled = POP_FILE 
    elif playlist == "rap":
        playlist_shuffled = RAP_FILE
    elif playlist == "eighties":
        playlist_shuffled = EIGHTYs_FILE
    elif playlist == "nineties":
        playlist_shuffled = NINETYs_FILE
    elif playlist == "twothousands":
        playlist_shuffled = TWOTHOUSANDs_FILE
    elif playlist == "twentytens":
        playlist_shuffled = TWENTYTENs_FILE
    elif playlist == "random":
        playlist_shuffled = PLAYLIST_FILE
    elif playlist == "creed":
        playlist_shuffled = CREED_FILE


    if os.path.exists(playlist_shuffled):
        with open(playlist_shuffled, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()

        if lines:
            rand.shuffle(lines)
            with open(playlist_shuffled, 'w', encoding='utf-8') as file:
                file.write('\n'.join(lines) + '\n')
            await ctx.send(f"{playlist.capitalize()} Playlist Shuffled!")
        else:
            await ctx.send(f"The {playlist.capitalize()} Playlist is empty.")
    else:
        await ctx.send(f"The {playlist.capitalize()} Playlist file does not exist.")

@bot.command()
async def shuffle_all(ctx):
    try:
        for playlist in playlists:
            shuffle_playlist(playlist)
        await ctx.send("All Playlists Have Been Shuffled!")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

def shuffle_playlist(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()

        if lines:
            rand.shuffle(lines)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write('\n'.join(lines) + '\n')

@bot.command()
async def stop(ctx):
    global vc
    global queue
    queue.clear()
    if vc:
        try:
            if vc.is_playing():
                vc.stop()
            await vc.disconnect()
        except Exception as e:
            print(f"Error disconnecting in stop: {e}")
        vc = None
    await ctx.send("Weebbot has been stopped.")

@bot.command()
async def random(ctx, num_songs: int = 1):
    if os.path.exists(PLAYLIST_FILE):
        with open(PLAYLIST_FILE, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
            if lines:
                num_songs = min(num_songs, len(lines))
                for _ in range(num_songs):
                    random_song = rand.choice(lines)
                    await play(ctx, x=random_song)
            else:
                await ctx.send("The Playlist is empty.")
    else:
        await ctx.send("The playlist file does not exist")

@bot.command()
async def country(ctx, num_songs: int = 1):
    if os.path.exists(COUNTRY_FILE):
        with open(COUNTRY_FILE, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
            if lines:
                num_songs = min(num_songs, len(lines))
                for _ in range(num_songs):
                    random_song = rand.choice(lines)
                    await play(ctx, x=random_song)
            else:
                await ctx.send("The Country Playlist is empty.")
    else:
        await ctx.send("The country playlist file does not exist")

@bot.command()
async def rap(ctx, num_songs: int = 1):
    if os.path.exists(RAP_FILE):
        with open(RAP_FILE, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
            if lines:
                num_songs = min(num_songs, len(lines))
                for _ in range(num_songs):
                    random_song = rand.choice(lines)
                    await play(ctx, x=random_song)
            else:
                await ctx.send("The Rap Playlist is empty.")
    else:
        await ctx.send("The rap playlist file does not exist")

@bot.command()
async def rock(ctx, num_songs: int = 1):
    if os.path.exists(ROCK_FILE):
        with open(ROCK_FILE, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
            if lines:
                num_songs = min(num_songs, len(lines))
                for _ in range(num_songs):
                    random_song = rand.choice(lines)
                    await play(ctx, x=random_song)
            else:
                await ctx.send("The Rock Playlist is empty.")
    else:
        await ctx.send("The rock playlist file does not exist")

@bot.command()
async def metal(ctx, num_songs: int = 1):
    if os.path.exists(METAL_FILE):
        with open(METAL_FILE, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
            if lines:
                num_songs = min(num_songs, len(lines))
                for _ in range(num_songs):
                    random_song = rand.choice(lines)
                    await play(ctx, x=random_song)
            else:
                await ctx.send("The Metal  Playlist is empty.")
    else:
        await ctx.send("The metal  playlist file does not exist")

@bot.command()
async def pop(ctx, num_songs: int = 1):
    if os.path.exists(POP_FILE):
        with open(POP_FILE, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
            if lines:
                num_songs = min(num_songs, len(lines))
                for _ in range(num_songs):
                    random_song = rand.choice(lines)
                    await play(ctx, x=random_song)
            else:
                await ctx.send("The Pop Playlist is empty.")
    else:
        await ctx.send("The pop playlist file does not exist")

@bot.command()
async def eighties(ctx, num_songs: int = 1):
    if os.path.exists(EIGHTYs_FILE):
        with open(EIGHTYs_FILE, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
            if lines:
                num_songs = min(num_songs, len(lines))
                for _ in range(num_songs):
                    random_song = rand.choice(lines)
                    await play(ctx, x=random_song)
            else:
                await ctx.send("The Eighties Playlist is empty.")
    else:
        await ctx.send("The eighties playlist file does not exist")

@bot.command()
async def nineties(ctx, num_songs: int = 1):
    if os.path.exists(NINETYs_FILE):
        with open(NINETYs_FILE, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
            if lines:
                num_songs = min(num_songs, len(lines))
                for _ in range(num_songs):
                    random_song = rand.choice(lines)
                    await play(ctx, x=random_song)
            else:
                await ctx.send("The Nineties Playlist is empty.")
    else:
        await ctx.send("The Nineties playlist file does not exist")

@bot.command()
async def twothousands(ctx, num_songs: int = 1):
    if os.path.exists(TWOTHOUSANDs_FILE):
        with open(TWOTHOUSANDs_FILE, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
            if lines:
                num_songs = min(num_songs, len(lines))
                for _ in range(num_songs):
                    random_song = rand.choice(lines)
                    await play(ctx, x=random_song)
            else:
                await ctx.send("The 2000s Playlist is empty.")
    else:
        await ctx.send("The 2000s playlist file does not exist")

@bot.command()
async def twentytens(ctx, num_songs: int = 1):
    if os.path.exists(TWENTYTENs_FILE):
        with open(TWENTYTENs_FILE, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
            if lines:
                num_songs = min(num_songs, len(lines))
                for _ in range(num_songs):
                    random_song = rand.choice(lines)
                    await play(ctx, x=random_song)
            else:
                await ctx.send("The 2010s Playlist is empty.")
    else:
        await ctx.send("The 2010s playlist file does not exist")

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

@bot.command()
async def edit(ctx):
    if os.path.exists(PLAYLIST_FILE):
        with open(PLAYLIST_FILE, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
            if lines:
                last_three_songs = lines[-3:]
                numbered_songs = (last_three_songs)

                response = "\n".join(numbered_songs)
                await ctx.send(f"Last three songs added:\n{response}")
                await ctx.send("Type 3 for Top, 2 for Middle, and 1 for Last Song Added")
            else:
                await ctx.send("The Playlist is empty")
    else:
        await ctx.send("The Playlist file does not exist")

@bot.command()
async def genre(ctx):
    await ctx.send("The Current Genre Commands are:")
    await ctx.send("random\ncountry\nrock\nrap\nmetal\npop\neighties\nnineties\ntwothousands\ntwentytens\ncreed")

VOICE_REGIONS = {
    "Brazil": "brazil",
    "Hong Kong": "hongkong",
    "India": "india",
    "Japan": "japan",
    "Rotterdam": "rotterdam",
    "Singapore": "singapore",
    "South Africa": "southafrica",
    "Sydney": "sydney",
    "US Central": "us-central",
    "US East": "us-east",
    "US South": "us-south",
    "US West": "us-west"
}

@bot.command()
async def test(ctx):
    import asyncio
    import discord

    available = []
    failed = []

    # Try to get the "test" category
    test_category = discord.utils.get(ctx.guild.categories, name="Test")
    if not test_category:
        await ctx.send("⚠️ 'test' category not found. Creating channels at top level.")

    for name, region in VOICE_REGIONS.items():
        print(f"Testing region: {name} ({region})")

        vc = None
        channel = None

        try:
            # Disconnect existing connection if present
            if ctx.voice_client and ctx.voice_client.is_connected():
                await ctx.voice_client.disconnect(force=True)

            # Create temp voice channel under "test" category if it exists
            channel = await ctx.guild.create_voice_channel(
                name=f"Test-{name}",
                rtc_region=region,
                category=test_category  # Category can be None, and that's fine
            )

            try:
                # Strict: If this fails at all, treat as a failed region
                vc = await asyncio.wait_for(channel.connect(), timeout=5)
            except Exception as e:
                print(f"❌ Immediate failure for {name} ({region}): {e}")
                failed.append(name)
                raise e  # Skip the rest of the try block

            # Optional short wait to confirm connection is alive
            await asyncio.sleep(2)

            if vc.is_connected():
                available.append(name)
                print(f"✅ Connected to {name} ({region})")
                await vc.disconnect(force=True)
            else:
                print(f"❌ {name} ({region}) did not stay connected")
                failed.append(name)

        except Exception:
            # Already logged above, just make sure cleanup happens
            pass

        finally:
            if ctx.voice_client:
                try:
                    await ctx.voice_client.disconnect(force=True)
                except:
                    pass

            if channel:
                await channel.delete()

            # Delay between region tests
            await asyncio.sleep(5)

    await ctx.send(f"✅ Available regions: {available}")
    await ctx.send(f"❌ Failed regions: {failed}")


    
@bot.command()
async def remove(ctx, number: int):
    if os.path.exists(PLAYLIST_FILE):
        with open(PLAYLIST_FILE, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()

        if not 1 <= number <= 3:
            await ctx.send("Invalid Number. Please use 1-3")
            return

        if len(lines) < 3:
            await ctx.send("The list is less than 3 songs long.")
            return
        
        index_to_remove = -number
        removed_song = lines.pop(index_to_remove)

        with open(PLAYLIST_FILE, 'w', encoding='utf-8') as file:
            file.write("\n".join(lines))

        await ctx.send(f"Removed song: {removed_song}")
    else:
        await ctx.send("The playlist file does not exist")
try:
    print("about to run the bot...")
    bot.run(BOT_TOKEN)
except Exception as e:
    print("Exception occurred before bot.run:", e)

