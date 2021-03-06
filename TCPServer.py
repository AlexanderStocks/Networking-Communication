# Generally use own TCP server when writing command shells or making a proxy
# Multi-threaded TCP server

import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9999  # Port 9999 uses the datagram protocol


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Pass server port and ip to listen on
server.bind((bind_ip, bind_port))

# Tell server to start listening with max backlog of 5 connections
server.listen(5)

print("[*] Listening on %s:%d" % (bind_ip, bind_port))


# Client handling thread
def clientHandler(client_socket):
    # print data client sends
    request = client_socket.recv(1024)

    print("[*] Received: %s" % request)

    # send back a packet
    client_socket.send(bytes("ACK!", "UTF-8"))

    client_socket.close()


while True:
    # client socket and remote connection details
    client, addr = server.accept()

    print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))

    # Create a thread that points to handle client function, pass client socket
    client_handler = threading.Thread(target=clientHandler, args=(client,))
    client_handler.start()
