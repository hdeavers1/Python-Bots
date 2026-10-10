import subprocess

remote_file = ''
local_file = r''

def transfer_file_from_raspberry_pi(transfer_file, destination_file):
    try:
        # Escaping quotes for PowerShell
        command = f'scp -i "C:\\Users\\Deave\\.ssh\\id_rsa" -P 22 "{transfer_file}" "{destination_file}"'
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"File transferred successfully: {transfer_file} -> {destination_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Command output: {e.output}")
        print(f"Command stderr: {e.stderr}")

transfer_file_from_raspberry_pi(local_file, remote_file)

