# Make a connection and run a command on an ssh system
# Configure SSH server/client to run remote commands on a windowed machine

# Need to install paramiko

import threading
import paramiko
import subprocess


# makes a connection to SSH server and runs a command
def ssh_command(ipAddr, username, password, command):
    client = paramiko.SSHClient()
    client.load_host_keys('/home/AlexStocks/.ssh/known_hosts')
    # Set policy to accept SSH key for the SSH server we are connecting to
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect()
    # uses username and password, can also use key authentication
    client.connect(ipAddr, username=username, password=password)
    session = client.get_transport().open_session()
    if session.active:
        session.exec_command(command)
        print(session.recv(1024))
    return
