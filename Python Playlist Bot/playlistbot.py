import os
import re
import discord
from discord.ext import commands

BOT_TOKEN = ""
PLAYLIST_FILE = "Current Playlist.txt"
ADD_FILE = "Add to Playlist.txt"

bot = commands.Bot(command_prefix="`", intents=discord.Intents.all())

@bot.event
async def on_message(message):
    # Check if the message starts with 'Playing: ' using regex
    match = re.match(r'^Playing:\s+(.+)', message.content)
    if match:
        song_title = match.group(1)
        # Check if the song title is already in the playlist file
        if not is_in_playlist(song_title):
            add_to_playlist(song_title)
            print(f'Added "{song_title}" to the playlist.')
        else:
            print(f'"{song_title}" is already in the playlist.')

    # Process commands if any
    await bot.process_commands(message)

def is_in_playlist(song_title):         
    if os.path.exists(PLAYLIST_FILE):
        with open(PLAYLIST_FILE, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
            return song_title in lines  
    return False


def add_to_playlist(song_title):
    def ensure_newline(filename):
        with open(filename, 'r+', encoding='utf-8') as file:
            file.seek(0, 2)  # Move the cursor to the end of the file
            if file.tell() > 0:  # Check if the file is not empty
                file.seek(file.tell() - 1)  # Move the cursor to the last character
                last_char = file.read(1)
                if last_char != '\n':
                    file.write('\n')  # Add a newline if the last character isn't one

    ensure_newline(PLAYLIST_FILE)
    ensure_newline(ADD_FILE)

    with open(PLAYLIST_FILE, 'a', encoding='utf-8') as file:
        file.write(f'{song_title}\n')

    with open(ADD_FILE, 'a', encoding='utf-8') as file:
        file.write(f'{song_title}\n')


bot.run(BOT_TOKEN)  
