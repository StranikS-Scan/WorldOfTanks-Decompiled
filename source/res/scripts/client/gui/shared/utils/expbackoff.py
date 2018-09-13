# Embedded file name: scripts/client/gui/shared/utils/ExpBackoff.py
import random

class ExpBackoff(object):

    def __init__(self, maxTime = 60, modifier = 1, randFactor = 0.5):
        self.__maxTime = maxTime
        self.__modifier = modifier
        self.__randFactor = randFactor
        self.__tries = 0

    def setModifier(self, modifier):
        self.__modifier = modifier

    def getModifier(self):
        return self.__modifier

    def setRandFactor(self, randFactor):
        self.__randFactor = randFactor

    def getRandFactor(self):
        return self.__randFactor

    def setMaxTime(self, maxTime):
        self.__maxTime = maxTime

    def getMaxTime(self):
        return self.__maxTime

    def reset(self):
        self.__tries = 0

    def next(self):
        basic = (1 << self.__tries) * self.__modifier
        delay = basic + random.randint(0, basic) * self.__randFactor
        self.__tries += 1
        return min(delay, self.__maxTime)

    def getTries(self):
        return self.__tries
