import sys
import socket
import getopt
import threading
import subprocess

# Subprocess gives proccess-creation interface that enables us to start and interact with client programs


# 4096 used commonly as a buffer size
from TCPServer import client_handler

listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0


#####################Functions for command line arguments and calling others#################################
def usage():
    print("BHP Net Tool")
    print()
    print("Usage: bhpnet.py -t target_host -p port")
    print("-l --listen              - listen on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run - execute the given file upon receiving a connection")
    print("-c --comand              - initialise a command shell")
    print("-u --upload=destination  - upon recieving connection upload a file and write to [destination]")
    print()
    print()
    print("Examples: ")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("ehco 'ABCDEFGHI' | ./bhpnet.py -t 192.168.11.12 -p 135")
    sys.exit(0)


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target
    # if there are no arguments
    if not len(sys.argv[1:]):
        usage()

    # read the command line options
    try:
        optval, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
                                     ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in optval:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unsupported Option"

    if not listen and len(target) and port > 0:
        # read into buffer from commandline
        # if not sending input use CTRL-D because will block
        buffer = sys.stdin.read()

        # send data
        client_sender(buffer)

    if listen:
        # setup a listening socket and process commands (upload a file, execute a command, start a command shell)
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

            # new line used so client compatible with command shell
            buffer += "\n"

            client.send(buffer)

    except:

        print("[*] General Exception Triggered! Exiting.")

        client.close()


def server_loop():
    global target
    # if no target given, listen on all interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


def run_command(command):
    command = command.rstrip()
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute commmand. \r\n"

    # send the output back to the client
    return output

######################################Logic for file uploads, command execution and shell###############################

def client_handler(client_socket):
    global upload
    global execute
    global command

    # check if theres an upload
    if len(upload_destination):

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
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # send acknowledgement
            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)

    # check for command execution
    if len(execute):
        # run command
        output = run_command(execute)

        client_socket.send(output)

    # if command shell requested go into another loop
    if command:
        while True:
            # show a prompt
            client_socket.send("<BHP:#> ")
            # recieve until newline char
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            response = run_command(cmd_buffer)
            client_socket.send(response)