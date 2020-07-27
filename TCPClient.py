import socket

target_host = "192.168.0.39"  # address of machine from ipconfig
target_port = 9999

# AF_INET declares we are using IPv4 address or hostname, SOCK_STREAM declares this as a TCP client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Ass: connection will always succeed
client.connect((target_host, target_port))

# Ass: the server always expects us to send data first
client.send(bytes("HELLO", 'UTF-8'))

response = client.recv(4096)

print(response)
