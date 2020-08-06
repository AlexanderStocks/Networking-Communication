# creates the SSH server the SSH client connects to, client can have any os but needs

import socket
import paramiko
import threading
import sys

# using key from paramiko files for demonstration
rsa_key = paramiko.RSAKey(filename='test_rsa.key')

users = {'AlexStocks': 'JavaIsBetterThanPython', 'JohnSmith': 'Password'}


class Server (paramiko.ServerInterface):
    def _init_(self):
        self.event = threading.Event()

    def check_channel_request(self, type, channelId):
        if type == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username in users) and (password == users.get(username)):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    SSHServer = sys.argv[1]
    port = int(sys.argv[2])

    try:
        # Here we use the socket listener
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((SSHServer, port))
        sock.listen(100)
        print("[+] Listening for connection ...")
        client, addr = sock.accept()
    except OSError as e:
        print("[-] Listen failed: " + str(e))
        sys.exit(1)  # exit code 1 means there was some issue which caused the program to exit
    print("[+] Found a connection!")

    try:
        # authentication methods
        session = paramiko.Transport(client)
        session.add_server_key(rsa_key)
        try:
            session.start_server(server=SSHServer)
        except paramiko.SSHException as x:
            print("[-] SSH negotiation failed.")
        chan = session.accept(20)
        print("[+] Authenticated!")
        print(chan.recv(1024))
        chan.send("Welcome to SSHServer")
        while True:
            # command sent and executed on client and result returned to server
            try:
                command = input("Enter command: ").strip('\n')
                if command != "exit":
                    chan.send(command)
                    print(chan.recv(1024) + '\n')
                else:
                    chan.send("exit")
                    print("Exiting...")
                    session.close()
                    raise Exception("exit")
            except KeyboardInterrupt:
                session.close()
    except Exception as e:
        print("[-] Caught exception: " + str(e))
        try:
            session.close()
        except:
            pass
        sys.exit(1)


