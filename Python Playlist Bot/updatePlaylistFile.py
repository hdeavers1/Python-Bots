import tkinter as tk
from tkinter import messagebox
import subprocess
import paramiko  # type: ignore
import time

hostname = ''
pi_destination = ''
pi_weebbot = ''
rock_file = r''
rap_file = r''
metal_file = r''
pop_file = r''
country_file = r''
eighties_file = r'
nineties_file = r''
twothousands_file = r''
twentytens_file = r''
creed_file = r''
weebbot_file = r''
cleaner_file = r''
desktop_path = r''

ssh_key_path = r'C:/Users/Deave/.ssh/id_rsa'
ssh_port = 22

def transfer_file(transfer_file, destination_file):
    try:
        command = f'scp -i "{ssh_key_path}" -P {ssh_port} "{transfer_file}" "{destination_file}"'
        subprocess.run(command, shell=True, check=True)
        messagebox.showinfo("Success", f"File transferred successfully: {transfer_file}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error transferring file: {e}")

def transfer_all():
    files = [rock_file, rap_file, metal_file, pop_file, country_file, eighties_file, nineties_file, twothousands_file, twentytens_file, creed_file]
    for file in files:
        transfer_file(file, pi_destination)

def kill_tmux_sessions(client):
    try:
        command = 'tmux kill-server'
        stdin, stdout, stderr = client.exec_command(command)
        stdout.channel.recv_exit_status()
        print("All tmux sessions terminated")
    except Exception as e:
        print(f'Error Killing tmux sessions {e}')

def run_bots(commands, client, botname):

    try:
        for command in commands:
            stdin, stdout, stderr = client.exec_command(command)
            stdout.channel.recv_exit_status()

        print(f"{botname} is up")
    except Exception as e:
        print(f'error in {botname} {e}')

def update():
    try:
        hostname = ''
        port = 22
        username = ''
        key_path = 'C:\\Users\\Deave\\.ssh\\id_rsa'

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port, username, key_filename=key_path)

        command = '/home/pi/botenvir/bin/pip install --upgrade discord.py yt-dlp spotipy'

        stdin, stdout, stderr = client.exec_command(command)
        stdout.channel.recv_exit_status()

        output = stdout.read().decode()
        error = stderr.read().decode()

        print(output)
        if error:
            print("ERROR:", error)

        print("Dependencies Updated")

    except Exception as e:
        print(f'error in update {e}')
    finally:
        client.close()
        
def commands():
    try:
        hostname = ''
        port = 22
        username = ''
        key_path = 'C:\\Users\\Deave\\.ssh\\id_rsa'

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(hostname, port, username, key_filename=key_path)

        weebbot_commands = [
            'tmux new-session -d -s weebbot_session',
            'tmux send-keys -t weebbot_session "cd botenvir" C-m',
            'tmux send-keys -t weebbot_session "source bin/activate" C-m',
            'tmux send-keys -t weebbot_session "cd .." C-m',
            'tmux send-keys -t weebbot_session "cd playlistbot" C-m',
            'tmux send-keys -t weebbot_session "python weebbot.py" C-m'
        ]
        cleaner_commands = [
            'tmux new-session -d -s cleaner_session',
            'tmux send-keys -t cleaner_session "cd playlistbot" C-m',
            'tmux send-keys -t cleaner_session "source playlistenvir/bin/activate" C-m', 
            'tmux send-keys -t cleaner_session "python cleaner_bot.py" C-m'
        ]
        pot_server_commands = [
            'tmux new-session -d -s potserver_session',
            'tmux send-keys -t potserver_session "cd ~/bgutil-ytdlp-pot-provider/server" C-m',
            'tmux send-keys -t potserver_session "/usr/bin/node build/main.js" C-m'
        ]

        update_dependencies_commands = [
            'tmux send-keys "cd botenvir" C-m',
            'tmux send-keys "source bin/activate" C-m',
            'tmux send-keys "pip install --upgrade discord.py" C-m',
            'tmux send-keys "pip install --upgrade yt-dlp" C-m',
            'tmux send-keys "pip install --upgrade spotipy" C-m'
        ]
        weebbot_name = 'Weebbot'
        cleaner_name = 'Cleaner'
        kill_tmux_sessions(client)

        run_bots(pot_server_commands, client, "PO Token Server")

        time.sleep(10)

        # update(update_dependencies_commands, client)
        run_bots(weebbot_commands, client, weebbot_name)
        run_bots(cleaner_commands, client, cleaner_name)

    except Exception as e:
        print(f'error: {e}')
    finally:
        client.close()

root = tk.Tk()
root.title("Python Bot Manager")

tk.Button(root, text="Run Bots", command=lambda: commands()).pack(pady=5)
tk.Button(root, text="Update Depend", command=lambda: update()).pack(pady=5)
tk.Button(root, text="Update Weebbot", command=lambda: transfer_file(weebbot_file, pi_destination)).pack(pady=5)
tk.Button(root, text="Update Cleaner", command=lambda: transfer_file(cleaner_file, pi_destination)).pack(pady=5)
tk.Button(root, text="Recover Weebbot", command=lambda: transfer_file(pi_weebbot, desktop_path)).pack(pady=5)
tk.Button(root, text="Transfer Rock Playlist", command=lambda: transfer_file(rock_file, pi_destination)).pack(pady=5)
tk.Button(root, text="Transfer Rap Playlist", command=lambda: transfer_file(rap_file, pi_destination)).pack(pady=5)
tk.Button(root, text="Transfer Metal Playlist", command=lambda: transfer_file(metal_file, pi_destination)).pack(pady=5)
tk.Button(root, text="Transfer Pop Playlist", command=lambda: transfer_file(pop_file, pi_destination)).pack(pady=5)
tk.Button(root, text="Transfer Country Playlist", command=lambda: transfer_file(country_file, pi_destination)).pack(pady=5)
tk.Button(root, text="Transfer 80s Playlist", command=lambda: transfer_file(eighties_file, pi_destination)).pack(pady=5)
tk.Button(root, text="Transfer 90s Playlist", command=lambda: transfer_file(nineties_file, pi_destination)).pack(pady=5)
tk.Button(root, text="Transfer 2000s Playlist", command=lambda: transfer_file(twothousands_file, pi_destination)).pack(pady=5)
tk.Button(root, text="Transfer 2010s Playlist", command=lambda: transfer_file(twentytens_file, pi_destination)).pack(pady=5)

# Create a button to transfer all files
tk.Button(root, text="Transfer All Playlists", command=transfer_all).pack(pady=20)

root.mainloop()




