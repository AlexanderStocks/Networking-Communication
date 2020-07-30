# Use proxy to help understand unknown protocols, modify traffic being sent tp an application, and create test cases
# for fuzzers

import sys
import socket
import threading


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except:
        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print("[*] Listening on %s:%d" % (local_host, local_port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # print out the local connection information
        print("[-->] Recieved incoming connection from %s:%d" % (addr[0], addr[1]))

        # start a thread to talk to the remote host
        proxy_thread = threading.Thread(target=proxy_handler,
                                        args=(client_socket, remote_host, remote_port, receive_first))

        proxy_thread.start()


def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./TCPProxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
        print("Example ./TCPProxy.py 127.0.0.1 135 8.8.8.8 443 True")
        sys.exit(0)

    # local listening parameters
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    # remote target parameters
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    # tells proxy to connect and receive data
    receive_first = sys.argv[5] == "True"

    # start up listening socket
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


main()


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    # connect to remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    # check dont need to initiate a connection to remote side and request data before going into main loop
    if receive_first:
        # takes a connected socket object and performs a receive
        remote_buffer = receive_from(remote_socket)
        # dump contents of the packet for inspection
        hexdump(remote_buffer)

        remote_buffer = response_handler(remote_buffer)

        if len(remote_buffer):
            print("[<--] Sending %d bytes to localhost." % len(remote_buffer))
            client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)

        if len(local_buffer):
            print("[-->] Received %d bytes from localhost." % len(local_buffer))
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)

            remote_socket.send(local_buffer)
            print("[-->] Sent to remote.")

            remote_buffer = receive_from(remote_socket)

            if len(remote_buffer):
                print("[<--] Received %d bytes from remote." % len(remote_buffer))
                hexdump(remote_buffer)

                remote_buffer = response_handler(remote_buffer)

                client_socket.send(remote_buffer)

                print("[<--] Sent to localhost.")

            if not len(local_buffer) or not len(remote_buffer):
                client_socket.close()
                remote_socket.close()
                print("[*] No more data. Closing connections.")

                break


# output packet details in hex and ascii
def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in range(0, len(src), length):
        s = src[i:i + length]
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b' '.join([x if 0x20 <= ord(x) < 0x7f else b'.' for x in s])
        result.append(b"%04X %-*s %s" % (i, length * (digits + 1), hexa, text))

    print(b'\n'.join(result))


# increase timeout when recieving from lossy networks
def receive_from(connection):
    buffer = " "
    connection.settimeout(2)

    try:
        while True:
            data = connection.recv(4096)

            if not data:
                break
            buffer += data
    except:
        pass

    return buffer


def request_handler(buffer):
    # Perform any changes here
    return buffer


def response_handler(buffer):
    # Perform any changes here
    return buffer