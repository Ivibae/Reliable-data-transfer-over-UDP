import os.path
import sys
import threading
from socket import *
import timer

BUFFER_SIZE = 1024

remoteHost = sys.argv[1]
serverPort = int(sys.argv[2])
fileName = sys.argv[3]
retryTimeout = int(sys.argv[4]) / 1000
windowSize = int(sys.argv[5])

base = 0
actualWindowSize = 0

timeoutTimer = timer.Timer()

clientSocket = socket(AF_INET, SOCK_DGRAM)

lock = threading.Lock()


def threadingReceiverFunction(messages_array, totalNumberOfMessages):
    global base
    global lock
    global timeoutTimer
    global actualWindowSize

    while True:
        ack, address = clientSocket.recvfrom(2)
        ackSeqNumber = int.from_bytes(ack[0:2], 'big')
        if ackSeqNumber == 65535:
            clientSocket.sendto(messages_array[0], (remoteHost, serverPort))
            continue
        if ackSeqNumber >= base:
            lock.acquire()
            timeoutTimer.startTimer()
            base = ackSeqNumber + 1
            actualWindowSize = min(windowSize, totalNumberOfMessages - base)
            clientSocket.sendto(messages_array[base + (actualWindowSize - 1)], (remoteHost, serverPort))
            lock.release()

        if ackSeqNumber == (totalNumberOfMessages - 1):
            break


def sendingFunction(windowSize):
    global timeoutTimer
    global base
    global lock
    global actualWindowSize

    lock = threading.Lock()

    messages_array = fillMessagesArray()
    totalNumberOfMessages = len(messages_array)

    receiverThread = threading.Thread(target=threadingReceiverFunction, args=(messages_array, totalNumberOfMessages,))
    receiverThread.start()

    sendWindowPackets(messages_array, totalNumberOfMessages)


# Helper function that is responsible to sending the packages in a window
def sendWindowPackets(messages_array, totalNumberOfMessages):
    global timeoutTimer
    global base
    global lock
    global actualWindowSize

    nextSeqNum = 0
    actualWindowSize = min(totalNumberOfMessages - base, windowSize)

    while base < totalNumberOfMessages:
        lock.acquire()
        while nextSeqNum < base + actualWindowSize:
            clientSocket.sendto(messages_array[nextSeqNum], (remoteHost, serverPort))
            nextSeqNum += 1

        timeoutTimer.startTimer()

        while not timeoutTimer.hasTimeoutPassed(retryTimeout):
            lock.release()
            lock.acquire()

        if timeoutTimer.hasTimeoutPassed(retryTimeout):
            nextSeqNum = base
        actualWindowSize = min(totalNumberOfMessages - base, windowSize)
        lock.release()


# Helper function that helps to store all the packets in an array which will be later sent
def fillMessagesArray():
    messages_array = []
    seqNumber = 0
    endOfFile = 0
    file = open(fileName, "rb")
    content = file.read(BUFFER_SIZE)
    nextContent = file.read(BUFFER_SIZE)
    while content:
        if not nextContent:
            endOfFile = 1

        message = bytearray(seqNumber.to_bytes(2, 'big')) + bytearray(endOfFile.to_bytes(1, 'big')) + bytearray(content)
        messages_array.append(message)

        content = nextContent
        nextContent = file.read(BUFFER_SIZE)
        seqNumber += 1
    file.close()
    return messages_array


fileSize = os.path.getsize(os.path.dirname(os.path.realpath(__file__)) + '/' + fileName) / 1000

totalTimer = timer.Timer()
totalTimer.startTimer()

sendingFunction(windowSize)

totalTimeSpent = totalTimer.logTime()
throughput = fileSize / totalTimeSpent

print(str(int(throughput)))
clientSocket.close()
