import sys
import socket
import getopt
import threading
import subprocess

# Subprocess gives process-creation interface that enables us to start and interact with client programs


# 4096 used commonly as a buffer size
from TCPServer import client_handler

listening = False
cmd = False
send = False
execute = ""
target = ""
send_destination = ""
port = 0


#####################Functions for cmd line arguments and calling others#################################

def main():
    global listening
    global port
    global execute
    global cmd
    global send_destination
    global target

    # if there are no arguments
    if not len(sys.argv[1:]):
        howToUse()

    # read the cmd line options
    try:
        maybeVal, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
                                     ["help", "listening", "execute", "target", "port", "cmd", "upload"])
    except getopt.GetoptError as e:
        print(str(e))
        howToUse()

    for o, a in maybeVal:
        if o in ("-h", "--help"):
            howToUse()
        elif o in ("-l", "--listening"):
            listening = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-u", "--upload"):
            send_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unsupported Option"

    if not listening and len(target) and port > 0:
        # read into buffer from cmdline
        # if not sending input use CTRL-D because will block
        buffer = sys.stdin.read()

        # send data
        client_sender(buffer)

    if listening:
        # setup a listening socket and process cmds (send a file, execute a cmd, start a cmd shell)
        server_loop()


main()


# repeats until user kills script
def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to the target host
        client.connect((target, port))

        if len(buffer):
            client.send(buffer)

        while True:

            # wait for data back
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

            print(response)

            # wait for next input
            buffer = input("")

            # new line used so client compatible with cmd shell
            buffer += "\n"

            client.send(buffer)

    except:

        print("[*] General Exception Triggered! Exiting.")

        client.close()


def server_loop():
    global target
    # if no target given, listening on all interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listening(5)

    while True:
        client_socket, addr = server.accept()

        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


def run_cmd(cmd):
    cmd = cmd.rstrip()
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute commmand. \r\n"

    # send the output back to the client
    return output

def howToUse():
    print("howToUse: NetworkClientNServer.py -t target_host -p port")
    print("-h --help                   - bring up manual ")
    print("-l --listening              - listening on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run    - execute the given file upon receiving a connection")
    print("-c --command                - initialise a cmd shell")
    print("-u --upload=destination     - upon receiving connection upload a file and write to [destination]")
    print()
    print("E.g. ")
    print("NetworkClientNServer.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("ehco 'ABCDEFGHI' | ./NetworkClientNServer.py -t 192.168.0.1 -p 5555")
    sys.exit(0)

######################################Logic for file sends, cmd execution and shell###############################

def client_handler(client_socket):
    global send
    global execute
    global cmd

    # check if theres an send
    if len(send_destination):

        # read in the bytes adn write to the destination
        file_buffer = ""

        #read till no more data
        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        # write out the bytes
        try:
            file_descriptor = open(send_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # send acknowledgement
            client_socket.send("Successfully saved file to %s\r\n" % send_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % send_destination)

    # check for cmd execution
    if len(execute):
        # run cmd
        output = run_cmd(execute)

        client_socket.send(output)

    # if cmd shell requested go into another loop
    # If writing python client to speak to this functions, remember newline character
    if cmd:
        while True:
            # show a prompt
            client_socket.send("<BHP:#> ")
            # receive until newline char
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            response = run_cmd(cmd_buffer)
            client_socket.send(response)

