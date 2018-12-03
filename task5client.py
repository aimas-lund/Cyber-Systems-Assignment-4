import socket
# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# get local machine name
host = "192.168.4.1"
port = 80
# connection to hostname on the port.
s.connect((host, port))

while True:
    msg = str(input()).encode('utf-8')
    # receive no more than 1024 bytes
    msgb = bytearray(msg)
    s.send(msgb)

    if msg.decode('utf-8').lower() == 'exit':
        break

    response = s.recv(1024)
    response = response.decode('ascii')
    print(response)

    msg = None