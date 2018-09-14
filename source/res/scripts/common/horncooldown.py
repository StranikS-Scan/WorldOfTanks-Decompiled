# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/HornCooldown.py
import BigWorld
import Event

class HornCooldown:

    def __init__(self, windowSize, maxSignals, state=None):
        self.__windowSize = windowSize
        self.__maxSignals = maxSignals
        if state is not None:
            self.__signals = state
            self.__reduce(BigWorld.time())
            del self.__signals[:-maxSignals]
        else:
            self.__signals = []
        self.__banEvent = Event.Event()
        self.__banStartTime = 0.0
        self.__banPeriod = 0.0
        return

    @property
    def banEvent(self):
        return self.__banEvent

    def ask(self):
        curTime = BigWorld.time()
        if self.__banPeriod > 0.0:
            if curTime - self.__banStartTime < self.__banPeriod:
                return False
            self.__banPeriod = 0.0
        self.__reduce(curTime)
        if len(self.__signals) < self.__maxSignals:
            self.__signals.append(curTime)
            bt = self.banTime()
            if bt > 0.0:
                self.__banEvent(bt)
            return True
        else:
            return False

    def banTime(self):
        curTime = BigWorld.time()
        if self.__banPeriod > 0.0:
            past = curTime - self.__banStartTime
            if past < self.__banPeriod:
                return self.__banPeriod - past
            self.__banPeriod = 0.0
        return 0.0 if len(self.__signals) < self.__maxSignals else max(0.0, self.__signals[0] + self.__windowSize - curTime)

    def ban(self, period):
        if self.banTime() < period:
            self.__banStartTime = BigWorld.time()
            self.__banPeriod = period
            self.__banEvent(period)

    def __reduce(self, curTime):
        if len(self.__signals) == 0:
            return
        cutTime = curTime - self.__windowSize
        if cutTime > self.__signals[-1]:
            del self.__signals[:]
            return
        for i, time in enumerate(self.__signals):
            if time > cutTime:
                del self.__signals[:i]
                return
