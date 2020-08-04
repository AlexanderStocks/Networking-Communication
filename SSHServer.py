import socket
import paramiko
import threading
import sys

# using key from paramiko files for demonstration
rsa_key = paramiko.RSAKey(filename='test_rsa.key')

class Server (paramiko.ServerInterface):
    def _init_(self):
        self.event = threading.Event()