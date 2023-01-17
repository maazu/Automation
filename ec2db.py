import paramiko
from scp import SCPClient
import datetime
import os
import sys

# current date
now = datetime.datetime.now()
timestamp = now.strftime("%d-%m-%Y")

HOST_USERNAME = 'ubuntu'
EC2_HOST = 'EC2-HOST'
KEY_FILE = 'ssh-key'
DB_NAME = 'db-name'
DB_PASS = 'postgres'
DB_FILE_NAME = f'db-snapshot-latest.sql'
DB_SEVER_SAVE_PATH = f"/home/ubuntu/{DB_FILE_NAME}"
BACKUP_COMMAND = f'PGPASSWORD="{DB_PASS}" pg_dump -U postgres -h localhost -d {DB_NAME} > ' + DB_SEVER_SAVE_PATH


# Connect to the EC2 instance
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


def progress(filename: str, size: int, sent: int):
    sys.stdout.write(f"{filename}'s progress: {float(sent)/float(size)*100:.2f}% \r")


try:
    ssh.connect(hostname=EC2_HOST, username=HOST_USERNAME, key_filename=KEY_FILE)
    print('Connected to EC2 instance sucessfully')

    # Run a command to create a database dump
    print(BACKUP_COMMAND)
    stdin, stdout, stderr = ssh.exec_command(BACKUP_COMMAND)

    # Check for errors
    error = stderr.read()
    if error:
        print(error)
        ssh.close()
        exit()

    # Create an SCP client

    scp = SCPClient(ssh.get_transport(), progress=progress)

    print('Initiating download from ' + EC2_HOST)

    # Download the file
    scp.get(DB_SEVER_SAVE_PATH, os.getcwd())

    print('Database Backup downloaded from ' + EC2_HOST + 'sucessfully')

    # Close the connection
    scp.close()
    ssh.close()
    print('Connection closed has been terminated from ' + EC2_HOST + 'sucessfully')

except paramiko.ssh_exception.NoValidConnectionsError as e:
    print("Error connecting to the EC2 instance:", e)
    exit()
except paramiko.ssh_exception.AuthenticationException as e:
    print("Authentication error:", e)
    exit()
except paramiko.ssh_exception.SSHException as e:
    print("Error establishing SSH connection:", e)
    exit()
