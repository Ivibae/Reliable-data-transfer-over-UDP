# Reliable-data-transfer-over-UDP

This project is my implementation in Python of three different sliding window protocols – [Stop-and-Wait](https://en.wikipedia.org/wiki/Stop-and-wait_ARQ), [Go Back N](https://en.wikipedia.org/wiki/Go-Back-N_ARQ) and Selective Repeat. The sender and receiver processes for each of the three protocols run within the same VM and communicate with each other over a link emulated using Linux Traffic Control. Receiver1 and Sender1 are simple implementations for the sender and the receiver (i.e. a server receiving a file) in ideal conditions, so no need to check for packet loss. Receiver2 and Sender2 are for the Stop-and-Wait protocol, and Go Back N and Selective Repeat are represented by the files ending in 3 and 4 respectively. Timer is a helper python program for time functionality.
