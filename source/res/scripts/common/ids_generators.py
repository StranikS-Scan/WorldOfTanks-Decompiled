# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ids_generators.py
# Compiled at: 2011-11-02 18:32:17
import time

class Int32IDGenerator(object):

    def __init__(self):
        self.__nextID = 0

    def next(self):
        self.__nextID += 1
        if self.__nextID > 65535:
            self.__nextID = 0
        currTime = int(time.time())
        return ((currTime & 32767) << 16) + self.__nextID


class SequenceIDGenerator(object):

    def __init__(self, lowBound=0, highBound=32767):
        self.__lowBound = lowBound
        self.__highBound = highBound
        self.__sequenceID = lowBound

    def next(self):
        self.__sequenceID += 1
        if self.__sequenceID >= self.__highBound:
            self.__sequenceID = self.__lowBound
        return self.__sequenceID

    currSequenceID = property(lambda self: self.__sequenceID)
    nextSequenceID = property(lambda self: self.next())
