import paramiko
import tkinter as tk
from tkinter import messagebox

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

def main():
    try:
        hostname = '        pip uninstall discord.py'
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
        # playlist_commands = [
        #     'tmux new-session -d -s playlistbot_session',
        #     'tmux send-keys -t playlistbot_session "cd playlistbot" C-m',
        #     'tmux send-keys -t playlistbot_session "source playlistenvir/bin/activate" C-m', 
        #     'tmux send-keys -t playlistbot_session "python playlistbot.py" C-m'
        # ]

        weebbot_name = 'Weebbot'
        playlistbot_name = 'Playlistbot'
        kill_tmux_sessions(client)

        run_bots(weebbot_commands, client, weebbot_name)
        # run_bots(playlist_commands, client, playlistbot_name)

    except Exception as e:
        print(f'error: {e}')
    finally:
        client.close()

def create_gui():
    root = tk.Tk()
    root.title("Bot Manager")

    run_button = tk.Button(root, text="Run Bots", command=main)
    run_button.pack(pady=20)

    root.mainloop()


create_gui()
