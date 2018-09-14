# Embedded file name: scripts/client/gui/shared/utils/backoff.py
import random

class AbstractBackoff(object):

    def __init__(self, minTime = 1, maxTime = 65536, modifier = 1, randFactor = 0.5):
        self._minTime = minTime
        self._maxTime = maxTime
        self._modifier = modifier
        self._randFactor = randFactor
        self._tries = 0

    def setModifier(self, modifier):
        self._modifier = modifier

    def getModifier(self):
        return self._modifier

    def setRandFactor(self, randFactor):
        self._randFactor = randFactor

    def getRandFactor(self):
        return self._randFactor

    def setMinTime(self, minTime):
        self._minTime = minTime

    def getMinTime(self):
        return self._minTime

    def setMaxTime(self, maxTime):
        self._maxTime = maxTime

    def getMaxTime(self):
        return self._maxTime

    def reset(self):
        self._tries = 0

    def shift(self, value):
        self._tries += value

    def next(self):
        delay = self.addRandom(self.calcDelay())
        self._tries += 1
        return self.normalize(delay)

    def getTries(self):
        return self._tries

    def calcDelay(self):
        raise NotImplementedError

    def addRandom(self, delay):
        raise NotImplementedError

    def normalize(self, delay):
        return max(self._minTime, min(delay, self._maxTime))


class ExpBackoff(AbstractBackoff):

    def calcDelay(self):
        return (1 << self._tries) * self._modifier

    def addRandom(self, delay):
        return delay + random.randint(0, delay) * self._randFactor


class RandomBackoff(AbstractBackoff):

    def calcDelay(self):
        return 0

    def addRandom(self, delay):
        return random.uniform(self._minTime, self._maxTime)

    def normalize(self, delay):
        return delay


class ModBackoff(AbstractBackoff):

    def calcDelay(self):
        return (1 << self._tries % self._modifier) * self._modifier

    def addRandom(self, delay):
        return delay * random.uniform(1, self._randFactor)
