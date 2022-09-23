import os.path
import sys
import threading
from socket import *
import timer

remoteHost = sys.argv[1]
serverPort = int(sys.argv[2])
fileName = sys.argv[3]
retryTimeout = int(sys.argv[4]) / 1000

BUFFER_SIZE = 1024

seqNumber = 0
endOfFile = 0

totalNumberOfRetransmissions = 0

clientSocket = socket(AF_INET, SOCK_DGRAM)

file = open(fileName, "rb")

fileSize = os.path.getsize(os.path.dirname(os.path.realpath(__file__)) + '/' + fileName) / 1000

content = file.read(BUFFER_SIZE)
nextContent = file.read(BUFFER_SIZE)


def sendingFunction(content, endOfFile, seqNumber):
    message = bytearray(seqNumber.to_bytes(2, 'big')) + bytearray(endOfFile.to_bytes(1, 'big')) + bytearray(content)
    clientSocket.sendto(message, (remoteHost, serverPort))



def threadingReceiver(seqNumber):
    while True:
        ack, address = clientSocket.recvfrom(2)
        ackSeqNumber = int.from_bytes(ack[0:2], 'big')
        if ackSeqNumber == seqNumber:
            break

totalTimer = timer.Timer()
totalTimer.startTimer()

timeoutTimer = timer.Timer()

while content:

    if not nextContent:
        endOfFile = 1

    acknowledged = False
    numberOfRetransmissions = -1  # This way when we first transmit we have retransmissions = 0

    receiverThread = threading.Thread(target=threadingReceiver, args=(seqNumber,))

    receiverThread.start()

    while not acknowledged:
        numberOfRetransmissions += 1

        sendingFunction(content, endOfFile, seqNumber)

        timeoutTimer.startTimer()

        while not timeoutTimer.hasTimeoutPassed(retryTimeout):
            if not receiverThread.is_alive() and not timeoutTimer.hasTimeoutPassed(retryTimeout):
                acknowledged = True
                break

    content = nextContent
    nextContent = file.read(BUFFER_SIZE)
    totalNumberOfRetransmissions += numberOfRetransmissions
    seqNumber += 1

totalTimeSpent = totalTimer.logTime()
throughput = int(fileSize / totalTimeSpent)

print(str(totalNumberOfRetransmissions) + ' ' + str(throughput))

file.close()
clientSocket.close()
