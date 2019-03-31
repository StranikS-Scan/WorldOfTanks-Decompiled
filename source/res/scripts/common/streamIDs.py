# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/streamIDs.py
# Compiled at: 2010-03-26 18:04:47
STREAM_ID_CHAT_MIN = 1
STREAM_ID_CHAT_MAX = 99
CHAT_INITIALIZATION_ID = 50
STREAM_ID_ACCOUNT_CMDS_MIN = 100
STREAM_ID_ACCOUNT_CMDS_MAX = 30000

class RangeStreamIDCallbacks(object):

    def __init__(self, rangeFactor=100):
        self.__callbacks = dict()
        self.__rangeFactor = int(rangeFactor)

    def addRangeCallback(self, range, callback):
        for key in self.__getKeySequence(range):
            self.__callbacks[key] = callback

    def delRangeCallback(self, range):
        for key in self.__getKeySequence(range):
            if key in self.__callbacks:
                del self.__callbacks[key]

    def clear(self):
        self.__callbacks.clear()

    def getCallbackForStreamID(self, streamID):
        key = streamID / self.__rangeFactor
        return self.__callbacks.get(key, None)

    def __getKeySequence(self, range):
        lowBound, highBound = int(range[0]), range[1]
        if highBound < lowBound:
            highBound, lowBound = lowBound, highBound
        lowKeyCandidate = lowBound / self.__rangeFactor
        highKeyCandidate = highBound / self.__rangeFactor
        return xrange(lowKeyCandidate, highKeyCandidate + 1)


if __name__ == '__main__':
    rangeCBs = RangeStreamIDCallbacks()
    rangeCBs.addRangeCallback((1, 99), lambda streamID: (streamID, (1, 99)))
    rangeCBs.addRangeCallback((100, 300), lambda streamID: (streamID, (100, 300)))
    rangeCBs.addRangeCallback((301, 399), lambda streamID: (streamID, (301, 399)))
    rangeCBs.addRangeCallback((101, 200), lambda streamID: (streamID, (101, 200)))
    rangeCBs.addRangeCallback((400, 599), lambda streamID: (streamID, (400, 599)))

    def outStreamIdCB(streamID):
        cb = rangeCBs.getCallbackForStreamID(streamID)
        print 'Callback for streamID:%s is :%s' % (streamID, str(cb(streamID)) if cb else 'None')


    outStreamIdCB(50)
    outStreamIdCB(100)
    outStreamIdCB(150)
    outStreamIdCB(300)
    outStreamIdCB(301)
    outStreamIdCB(399)
    outStreamIdCB(400)
    outStreamIdCB(401)
    rangeCBs.delRangeCallback((101, 199))
    outStreamIdCB(100)
    outStreamIdCB(101)
    outStreamIdCB(150)
    outStreamIdCB(199)
    outStreamIdCB(200)
    rangeCBs.delRangeCallback((101, 200))
    outStreamIdCB(199)
    outStreamIdCB(200)
    outStreamIdCB(201)
    outStreamIdCB(299)
    outStreamIdCB(300)
