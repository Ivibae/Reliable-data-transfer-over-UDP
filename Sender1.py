import sys
import time
from socket import *

remoteHost = sys.argv[1]

serverPort = int(sys.argv[2])
fileName = sys.argv[3]

seqNumber = 0
BUFFER_SIZE = 1024
endOfFile = 0

clientSocket = socket(AF_INET, SOCK_DGRAM)

file = open(fileName, "rb")


content = file.read(BUFFER_SIZE)
nextContent = file.read(BUFFER_SIZE)
if not nextContent:
    endOfFile = 1
    message = bytearray(seqNumber.to_bytes(2, 'big')) + bytearray(endOfFile.to_bytes(1, 'big')) + bytearray(content)
    clientSocket.sendto(message, (remoteHost, serverPort))
    content = file.read(BUFFER_SIZE) # Thus it would not enter the while loop

while content:
    message = bytearray(seqNumber.to_bytes(2, 'big')) + bytearray(endOfFile.to_bytes(1, 'big')) + bytearray(content)
    clientSocket.sendto(message, (remoteHost, serverPort))
    time.sleep(0.0001)
    content = file.read(BUFFER_SIZE)
    seqNumber += 1
    if not content:
        endOfFile = 1
        message = bytearray(seqNumber.to_bytes(2, 'big')) + bytearray(endOfFile.to_bytes(1, 'big')) + bytearray(nextContent)
        clientSocket.sendto(message, (remoteHost, serverPort))
    else:
        message = bytearray(seqNumber.to_bytes(2, 'big')) + bytearray(endOfFile.to_bytes(1, 'big')) + bytearray(nextContent)
        clientSocket.sendto(message, (remoteHost, serverPort))
        nextContent = file.read(BUFFER_SIZE)
    seqNumber += 1


clientSocket.close()
file.close()

