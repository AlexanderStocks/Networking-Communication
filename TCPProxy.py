# Use proxy to help understand unknown protocols, modify traffic being sent tp an application, and create test cases
# for fuzzers

import sys
import socket
import threading


def listen(local_host, local_port, otherHost, otherPort, receiving):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.bind((local_host, local_port))
    except OSError:
        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print("[*] Listening on %s:%d" % (local_host, local_port))

    sock.listen(5)

    while True:
        clientSock, addr = sock.accept()

        # print out the local connection information
        print("[-->] Recieved incoming connection from %s:%d" % (addr[0], addr[1]))

        # start a thread to talk to the remote host
        thread = threading.Thread(target=proxy,
                                  args=(clientSock, otherHost, otherPort, receiving))

        thread.start()


def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./TCPProxy.py [localhost] [localport] [remotehost] [remoteport] [receiving]")
        print("Example ./TCPProxy.py 127.0.0.1 135 8.8.8.8 443 True")
        sys.exit(0)

    # local listening parameters
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    # remote target parameters
    otherHost = sys.argv[3]
    otherPort = int(sys.argv[4])

    # tells proxy to connect and receive data
    receiving = "True" in sys.argv[5]

    # start up listening socket
    listen(local_host, local_port, otherHost, otherPort, receiving)


main()


def proxy(clientSock, otherHost, otherPort, receiving):
    # connect to remote host
    otherSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    otherSock.connect((otherHost, otherPort))

    # check dont need to initiate a connection to remote side and request data before going into main loop
    if receiving:
        # takes a connected socket object and performs a receive
        otherBuffer = getData(otherSock)
        # dump contents of the packet for inspection
        hexDump(otherBuffer)

        otherBuffer = response_handler(otherBuffer)

        if len(otherBuffer):
            print("[<--] Sending %d bytes to localhost." % len(otherBuffer))
            clientSock.send(otherBuffer)

    while True:
        thisBuffer = getData(clientSock)

        if len(thisBuffer):
            print("[-->] Received %d bytes from localhost." % len(thisBuffer))
            hexDump(thisBuffer)

            thisBuffer = request_handler(thisBuffer)

            otherSock.send(thisBuffer)
            print("[-->] Sent to remote.")

            otherBuffer = getData(otherSock)

            if len(otherBuffer):
                print("[<--] Received %d bytes from remote." % len(otherBuffer))
                hexDump(otherBuffer)

                otherBuffer = response_handler(otherBuffer)

                clientSock.send(otherBuffer)

                print("[<--] Sent to localhost.")

            if not len(thisBuffer) or not len(otherBuffer):
                clientSock.close()
                otherSock.close()
                print("[*] No more data. Closing connections.")

                break


# output packet details in hex and ascii
def hexDump(src, length=16):
    result = []
    digits = 4 if isinstance(src, str) else 2
    for i in range(0, len(src), length):
        s = src[i:i + length]
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b' '.join([x if 0x20 <= ord(x) < 0x7f else b'.' for x in s])
        result.append(b"%04X %-*s %s" % (i, length * (digits + 1), hexa, text))

    print(b'\n'.join(result))


# increase timeout when receiving from lossy networks
# Used to receive local and remote data, pass in socket object
# Two second timeout to be increased if proxying traffic over long distances or over lossy networks
# Handles receiving data until more data is sent from other end of connection
def getData(connection):
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


# These two
def request_handler(buffer):
    # Perform any changes here
    return buffer


def response_handler(buffer):
    # Perform any changes here
    return buffer
