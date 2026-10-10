import subprocess
import os

ADD_SONG = ''
remote_file = ''
local_file = r''

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
