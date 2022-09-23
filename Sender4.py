import os.path
import socket
import sys
import threading
import time
from socket import *
import timer

BUFFER_SIZE = 1024

remoteHost = sys.argv[1]
serverPort = int(sys.argv[2])
fileName = sys.argv[3]
retryTimeout = int(sys.argv[4]) / 1000
windowSize = int(sys.argv[5])

base = 1
actualWindowSize = 0
nextSeqNum = 1
lastIndexSent = 0

enabledTimer = True

timeoutTimer = timer.Timer()

clientSocket = socket(AF_INET, SOCK_DGRAM)

lock = threading.Lock()

packets_ack = set()
all_packets_received = False

messages_array = []
seqNumber = 1
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

packetsSent = []

def threadingReceiverFunction(messages_array):
    global base
    global lock
    global timeoutTimer
    global actualWindowSize
    global nextSeqNum
    global all_packets_received
    global packets_ack
    global enabledTimer

    while True:
        ack, address = clientSocket.recvfrom(2)
        ackSeqNumber = int.from_bytes(ack[0:2], 'big')
        packets_ack.add(ackSeqNumber)

        if ackSeqNumber == 65535:   # The receiver has thus received all the packages
            all_packets_received = True
            break
        with lock:
            if ackSeqNumber == base:
                areAllPacketsAck = True
                for packet in range(base, nextSeqNum):
                    if packet not in packets_ack:
                        base = packet
                        areAllPacketsAck = False
                        break
                if areAllPacketsAck:
                    base = nextSeqNum
                    enabledTimer = False
                else:
                    enabledTimer = True
                    timeoutTimer.startTimer()


def timerThreadFunction():
    global base
    global packets_ack
    global nextSeqNum
    global all_packets_received
    global enabledTimer
    global lock
    global timeoutTimer
    global messages_array
    global packetsSent

    localTimer = timer.Timer()
    localTimer.startTimer()
    while True:
        with lock:
            if all_packets_received:
                break

            if not localTimer.hasTimeoutPassed(retryTimeout):
                continue
            else:
                localTimer.startTimer()

            if not enabledTimer:
                continue

            if len(messages_array) == len(packets_ack):
                break
            i = 0
            while base + i < nextSeqNum:
                if (base + i) >= len(packetsSent):
                    break
                if (base + i) not in packets_ack:
                    clientSocket.sendto(messages_array[base + i - 1], (remoteHost, serverPort))
                i += 1



def sendingFunction(windowSize):
    global timeoutTimer
    global base
    global lock
    global actualWindowSize
    global messages_array
    global packetsSent
    global enabledTimer
    global nextSeqNum

    lock = threading.Lock()

    packetsSent = [0] * (len(messages_array) + 1)
    totalNumberOfMessages = len(messages_array)

    with lock:
        if nextSeqNum < (base + windowSize):
            clientSocket.sendto(messages_array[nextSeqNum-1], (remoteHost, serverPort))
            packetsSent[nextSeqNum] = 1

            if nextSeqNum == base:
                enabledTimer = True
                timeoutTimer.startTimer()
            nextSeqNum += 1

            return True

        else:

            return False


receiverThread = threading.Thread(target=threadingReceiverFunction, args=(messages_array,))
receiverThread.start()

timerThread = threading.Thread(target=timerThreadFunction)
timerThread.start()


fileSize = os.path.getsize(os.path.dirname(os.path.realpath(__file__)) + '/' + fileName) / 1000

totalTimer = timer.Timer()
totalTimer.startTimer()

breaking = False

while not breaking:
    if len(messages_array) == len(packetsSent):
        breaking = True

    if lastIndexSent == len(messages_array):
        break
    next_message = messages_array[lastIndexSent]
    if sendingFunction(windowSize):
        lastIndexSent += 1


totalTimeSpent = totalTimer.logTime()
throughput = fileSize / totalTimeSpent
time.sleep(1)
print(str(int(throughput)))
clientSocket.close()
