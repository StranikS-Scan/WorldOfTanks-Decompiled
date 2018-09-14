# Embedded file name: scripts/client/gui/customization_2_0/elements/installed.py
import time
from helpers import time_utils

class Item(object):
    __slots__ = ('_rawData', '_spot')

    def __init__(self, rawData, spot):
        self._rawData = rawData
        self._spot = spot

    def getID(self):
        raise NotImplementedError

    @property
    def duration(self):
        raise NotImplementedError

    def timeOfApplication(self):
        raise NotImplementedError

    def getSpot(self):
        raise NotImplementedError

    def getNumberOfDaysLeft(self):
        timeLeft = (time.time() - self.timeOfApplication()) / time_utils.ONE_DAY
        term = self.duration
        return round(term - timeLeft)


class Emblem(Item):

    def __init__(self, rawData, spot):
        Item.__init__(self, rawData, spot)

    def getID(self):
        return self._rawData[0]

    @property
    def duration(self):
        return self._rawData[2]

    def timeOfApplication(self):
        return self._rawData[1]

    def getSpot(self):
        return self._spot


class Inscription(Item):

    def __init__(self, rawData, spot):
        Item.__init__(self, rawData, spot)

    def getID(self):
        return self._rawData[0]

    @property
    def duration(self):
        return self._rawData[2]

    def timeOfApplication(self):
        return self._rawData[1]

    def getSpot(self):
        return self._spot


class Camouflage(Item):

    def __init__(self, rawData, spot):
        Item.__init__(self, rawData, spot)

    def getID(self):
        return self._rawData[0]

    @property
    def duration(self):
        return self._rawData[2]

    def timeOfApplication(self):
        return self._rawData[1]

    def getSpot(self):
        return self._spot
