import sys
from socket import *

HEADER_SIZE = 3
BUFFER_SIZE = 1024 + HEADER_SIZE

serverPort = int(sys.argv[1])
fileName = sys.argv[2]


serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

file = open(fileName, 'wb')

while True:
    message, address = serverSocket.recvfrom(BUFFER_SIZE)
    endOfFile = message[2]
    content = message[3:]

    file.write(content)

    if endOfFile:
        serverSocket.close()
        file.close()
        break




