# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/timers.py
import BigWorld

class EachFrameTickTimer(object):
    __slots__ = ('__duration', '__callbackToTick', '__callbackID', '__startTime')

    def __init__(self, callbackToTick):
        assert callbackToTick is not None
        self.__duration = None
        self.__callbackToTick = callbackToTick
        self.__callbackID = None
        self.__startTime = 0.0
        return

    def destroy(self):
        self.stop()
        self.__callbackToTick = None
        return

    def start(self, duration):
        self.__duration = duration
        self.__startTime = BigWorld.time()
        self.__callbackID = BigWorld.callback(0.0, self.__tick)

    def stop(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    @property
    def isActive(self):
        return self.__callbackID is not None

    def __tick(self):
        self.__callbackID = None
        self.__callbackToTick()
        dt = BigWorld.time() - self.__startTime
        if dt <= self.__duration:
            self.__callbackID = BigWorld.callback(0.0, self.__tick)
        return
