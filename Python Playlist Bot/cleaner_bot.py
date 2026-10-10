import discord#type: ignore
from discord.ext import commands, tasks #type: ignore
import asyncio
import os

BOT_TOKEN = "MTM4Nzg5MzY3MTA0NjY3NjY3MQ.G4IzBm.Mmwr358MIX1ImddsIHnp3N18h8pmQcSBEy7XNE"
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

WEEBOT_ID = 1178769455958995064

bot = commands.Bot(command_prefix="!", intents=intents)

# Example: Delete bot messages containing certain keywords after a delay
auto_delete_keywords = [
    "Added to queue:",
    "Skipping current song...",
    "Queue Cleared.",
    "Weebbot has been stopped.",
    "Not connected to voice. Cannot play audio.",
    "Failed to connect to voice channel. Please try again later.",
    "Sorry, I couldn't find a song matching",
    "No song is currently playing.",
    "The queue is already empty.",
    "The Playlist is empty.",
    "The playlist file does not exist",
    "The Country Playlist is empty.",
    "The country playlist file does not exist",
    "The Rap Playlist is empty.",
    "The rap playlist file does not exist",
    "The Rock Playlist is empty.",
    "The rock playlist file does not exist",
    "The Metal  Playlist is empty.",
    "The metal  playlist file does not exist",
    "The Pop Playlist is empty.",
    "The pop playlist file does not exist",
    "The Eighties Playlist is empty.",
    "The eighties playlist file does not exist",
    "The Nineties Playlist is empty.",
    "The Nineties playlist file does not exist",
    "The 2000s Playlist is empty.",
    "The 2000s playlist file does not exist",
    "The 2010s Playlist is empty.",
    "The 2010s playlist file does not exist",
    "The Creed Playlist is empty.",
    "The Creed Playlist file does not exist",
    "Invalid Number. Please use 1-3",
    "The list is less than 3 songs long.",
    "Removed song:",
    "Last three songs added:",
    "Type 3 for Top, 2 for Middle, and 1 for Last Song Added",
    "The Playlist file does not exist",
    "The Current Genre Commands are:",
    "Playlist Shuffled!",
    "Playlist is empty.",
    "Playlist file does not exist.",
    "All Playlists Have Been Shuffled!",
    "An error occurred:",
    "?play",
    "!cleanerbot",
    "?clear",
    "?skip",
    "?creed",
    "Playing:",
    "!clean",
    "?stop",
    "Available regions:",
    "Failed regions:",
    "?test",
    "You must be in a voice channel to play music!",
    "User not in voice channel",
    "Stopped",
    "Queue Cleared",
    "Skipped.",
    "Nothing is playing.",
    "Disconnected.",
    "YouTube lookup timed out after 20 seconds",
    "Skipped",
    "Autoplay enabled",
    "Autoplay disabled",
    "Usage: ?autoplay on/off",
    "Autoplay added:",
    "Youtube multi search error",
    "?autoplay on",
    "?autoplay off",
    "Playlist mode enabled",
    "Playlist mode disabled",
    "Playlist error: ",
    "Queued: ",
    "Failed to load playlist.",
    "Loading playlist... ",
    "?playlist"
]

@bot.event
async def on_ready():
    print(f"Cleaner bot logged in as {bot.user}")
    scheduled_clean.start()

def is_admin():
    async def predicate(ctx):
        perms = ctx.author.guild_permissions
        return perms.manage_messages or perms.administrator
    return commands.check(predicate)

@bot.command()
async def clean(ctx, limit: int = 50):
    deleted = await run_clean(ctx.channel, limit)
    await ctx.send(
        f"CleanerBot: Deleted {deleted} messages.",
        delete_after=5
    )

async def run_clean(channel, limit=100):
    deleted = 0
    async for message in channel.history(limit=limit):
        if any(kw in message.content for kw in auto_delete_keywords):
            try:
                await message.delete()
                deleted += 1
            except Exception:
                pass
    return deleted

@tasks.loop(hours=6)
async def scheduled_clean():
    channel_ids = [1092276399991169138]

    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel_ids and channel.id not in channel_ids:
                continue

            try:
                deleted = await run_clean(channel, limit=100)
                if deleted:
                    print(f"[Scheduled clean] #{channel.name}: {deleted} messages deleted")
            except Exception as e:
                print(f"[Scheduled clean error] #{channel.name}: {e}")
                
@scheduled_clean.before_loop
async def before_scheduled_clean():
    await bot.wait_until_ready()
    print("Scheduled cleaner started")

@bot.event
async def on_ready():
    print(f"Cleaner bot logged in as {bot.user}")
    scheduled_clean.start()

if __name__ == "__main__":
    bot.run(BOT_TOKEN)
