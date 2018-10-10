# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/CallbackDelayer.py
import functools
import BigWorld

class CallbackDelayer(object):

    def __init__(self):
        self.__callbacks = {}

    def destroy(self):
        self.clearCallbacks()

    def clearCallbacks(self):
        for _, callbackId in self.__callbacks.iteritems():
            if callbackId is not None:
                BigWorld.cancelCallback(callbackId)

        self.__callbacks = {}
        return

    def __funcWrapper(self, func, *args, **kwargs):
        del self.__callbacks[func]
        desiredDelay = func(*args, **kwargs)
        if desiredDelay is not None and desiredDelay >= 0:
            curId = BigWorld.callback(desiredDelay, functools.partial(self.__funcWrapper, func, *args, **kwargs))
            self.__callbacks[func] = curId
        return

    def delayCallback(self, seconds, func, *args, **kwargs):
        curId = self.__callbacks.get(func)
        if curId is not None:
            BigWorld.cancelCallback(curId)
            del self.__callbacks[func]
        curId = BigWorld.callback(seconds, functools.partial(self.__funcWrapper, func, *args, **kwargs))
        self.__callbacks[func] = curId
        return

    def stopCallback(self, func):
        curId = self.__callbacks.get(func)
        if curId is not None:
            BigWorld.cancelCallback(curId)
            del self.__callbacks[func]
        return

    def hasDelayedCallback(self, func):
        return func in self.__callbacks


class CallbacksSetByID(object):
    __slots__ = ('__callbackIDs',)

    def __init__(self):
        super(CallbacksSetByID, self).__init__()
        self.__callbackIDs = {}

    def clear(self):
        while self.__callbackIDs:
            _, callbackID = self.__callbackIDs.popitem()
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        return

    def delayCallback(self, uniqueID, seconds, function):
        self.stopCallback(uniqueID)
        self.__callbackIDs[uniqueID] = BigWorld.callback(seconds, functools.partial(self.__handleCallback, uniqueID, function))

    def stopCallback(self, uniqueID):
        callbackID = self.__callbackIDs.pop(uniqueID, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        return

    def __handleCallback(self, uniqueID, function):
        self.__callbackIDs[uniqueID] = None
        function(uniqueID)
        return


class TimeDeltaMeter(object):

    def __init__(self, timeFunc=BigWorld.time):
        self.__timeFunc = timeFunc
        self.__prevTime = timeFunc()

    def measureDeltaTime(self):
        time = self.__timeFunc()
        deltaTime = time - self.__prevTime
        self.__prevTime = time
        return deltaTime
