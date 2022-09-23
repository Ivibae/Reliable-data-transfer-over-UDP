import time


class Timer:

    def __init__(self):
        self.start = time.time()

    def startTimer(self):
        self.start = time.time()

    def logTime(self):
        return time.time() - self.start

    def hasTimeoutPassed(self, timeout):
        return timeout < (time.time() - self.start)
