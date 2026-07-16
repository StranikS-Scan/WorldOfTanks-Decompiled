# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ids_generators.py
from __future__ import absolute_import
import time

class Int32IDGenerator(object):

    def __init__(self):
        self.__nextID = 0
        self.__currID = 0

    def __next__(self):
        self.__nextID += 1
        if self.__nextID > 65535:
            self.__nextID = 0
        currTime = int(time.time())
        self.__currID = ((currTime & 32767) << 16) + self.__nextID
        return self.__currID

    next = __next__
    currSequenceID = property(lambda self: self.__currID)


class SequenceIDGenerator(object):

    def __init__(self, lowBound=0, highBound=32767):
        self.__lowBound = lowBound
        self.__highBound = highBound
        self.__sequenceID = lowBound

    def __next__(self):
        self.__sequenceID += 1
        if self.__sequenceID >= self.__highBound:
            self.__sequenceID = self.__lowBound
        return self.__sequenceID

    next = __next__

    def max(self):
        return self.__highBound

    def clear(self):
        self.__sequenceID = self.__lowBound

    currSequenceID = property(lambda self: self.__sequenceID)
    nextSequenceID = property(__next__)
