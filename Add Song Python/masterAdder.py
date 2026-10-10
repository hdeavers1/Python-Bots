import subprocess
import os

ADD_SONG = 'C:/Users/Deave/OneDrive/Desktop/Projects/Python Bots/Add Song Python/addSong.py'
remote_file = 'pi@192.168.1.188:/home/pi/playlistbot/Add to Playlist.txt'
local_file = r'C:\Users\Deave\OneDrive\Desktop\Projects\Python Bots\Add Song Python\Add to Playlist.txt'

def transfer_file(transfer_file, destination_file):
    try:
        # Construct the scp command to copy from Raspberry Pi to local machine
        command = f'scp -i "C:\\Users\\Deave\\.ssh\\id_rsa" -P 22 "{transfer_file}" "{destination_file}"'
        
        # Run the command using subprocess
        subprocess.run(command, shell=True, check=True)
        
        print(f"File transferred successfully: {transfer_file} -> {destination_file}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")


def filter_add_song(local_file):
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['notepad.exe', local_file], check=True)
        else:
            subprocess.run(['nano', local_file], check=True)

        print (f"File {local_file} opened and closed successfully")
    
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def run_add_song():
    try:
        command = f'python addSong.py'

        subprocess.run(command, shell=True, check=True)

        print(f"ran addSong.py")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

# Example usage

transfer_file(remote_file, local_file)
filter_add_song(local_file) 
run_add_song()
transfer_file(local_file, remote_file)




