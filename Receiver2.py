import sys
from socket import *

HEADER_SIZE = 3
BUFFER_SIZE = 1024 + HEADER_SIZE

serverPort = int(sys.argv[1])
fileName = sys.argv[2]

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

ackNumber = 0

file = open(fileName, 'wb')

while True:
    message, address = serverSocket.recvfrom(BUFFER_SIZE)
    seqNumber = int.from_bytes(message[0:2], 'big')
    endOfFile = message[2]
    content = message[3:]

    # Sending the acknowledgement packet consisting of the sequence number
    serverSocket.sendto(seqNumber.to_bytes(2, 'big'), address)

    if seqNumber == ackNumber:
        file.write(content)
        ackNumber += 1

    if endOfFile:
        # When we receive the last packet, we send 25 confirmations so that we are all but certain that the sender has
        # received the acknowledgement.
        for i in range(25):
            serverSocket.sendto(seqNumber.to_bytes(2, 'big'), address)
        file.close()
        serverSocket.close()
        break
