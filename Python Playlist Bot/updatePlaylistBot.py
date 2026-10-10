import subprocess
import os

ADD_SONG = 'C:/Users/Deave/OneDrive/Desktop/Projects/Python Bots/Add Song Python/addSong.py'
remote_file = 'pi@192.168.1.188:/home/pi/playlistbot/playlistbot.py'
local_file = r'C:\Users\Deave\OneDrive\Desktop\Projects\Python Bots\Python Playlist Bot\playlistbot.py'

def transfer_file(transfer_file, destination_file):
    try:
        # Construct the scp command to copy from Raspberry Pi to local machine
        command = f'scp -i "C:\\Users\\Deave\\.ssh\\id_rsa" -P 22 "{transfer_file}" "{destination_file}"'
        
        # Run the command using subprocess
        subprocess.run(command, shell=True, check=True)
        
        print(f"File transferred successfully: {transfer_file} -> {destination_file}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")


transfer_file(local_file, remote_file)