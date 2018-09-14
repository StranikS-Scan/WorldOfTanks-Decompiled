# Embedded file name: scripts/client/FX/Effects/_EventTimer.py
import BigWorld

class EventTimer:

    def __init__(self):
        self.semaphore = 0
        self.callbackFn = None
        return

    def going(self):
        return self.semaphore != 0

    def reserve(self):
        self.semaphore += 1

    def release(self):
        self.semaphore -= 1

    def begin(self, duration, callbackFn):
        self.callbackFn = callbackFn
        self.semaphore += 1
        BigWorld.callback(duration, self.end)

    def extend(self, duration):
        self.semaphore += 1
        BigWorld.callback(duration, self.end)

    def end(self):
        self.semaphore -= 1
        if self.semaphore == 0:
            if self.callbackFn:
                self.callbackFn()
                self.callbackFn = None
        return
