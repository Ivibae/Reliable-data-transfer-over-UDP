import sys
from socket import *

HEADER_SIZE = 3
BUFFER_SIZE = 1024 + HEADER_SIZE

serverPort = int(sys.argv[1])
fileName = sys.argv[2]
windowSize = int(sys.argv[3])

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

expectedSeqNumber = 1
base = 1

messages_dictionary = dict()
total_content = bytearray()

lastSeqNumber = 65535

while True:
    if base > lastSeqNumber:
        break

    message, address = serverSocket.recvfrom(BUFFER_SIZE)
    seqNumber = int.from_bytes(message[0:2], 'big')
    endOfFile = message[2]
    content = message[3:]

    if endOfFile:
        lastSeqNumber = seqNumber

    if seqNumber in range(base - windowSize, base):
        serverSocket.sendto(seqNumber.to_bytes(2, 'big'), address)

    if base <= seqNumber < base + windowSize:
        serverSocket.sendto(seqNumber.to_bytes(2, 'big'), address)
        messages_dictionary[seqNumber] = content

    if seqNumber == base:
        areAllPacketsAck = True
        for index in range(base, base + windowSize):
            if not index in messages_dictionary:
                areAllPacketsAck = False
                base = index
                break
            else:
                total_content += messages_dictionary[index]
        if areAllPacketsAck:
            base += windowSize


# This is a number that indicates that the file has been received correctly so that the sender knows
# it can stop
fileReceivedNumber = 65535
for i in range (25):
    serverSocket.sendto(fileReceivedNumber.to_bytes(2, 'big'), address)

file = open(fileName, 'wb')
file.write(total_content)
file.close()

serverSocket.close()
