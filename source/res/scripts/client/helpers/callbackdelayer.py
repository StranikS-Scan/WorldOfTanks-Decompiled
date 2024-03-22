# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/CallbackDelayer.py
import functools
from typing import Callable, Dict
import BigWorld
from collections import namedtuple

class ICallbackDelayer(object):

    def clearCallbacks(self):
        pass

    def delayCallback(self, seconds, func, *args, **kwargs):
        pass

    def stopCallback(self, func):
        pass

    def hasDelayedCallback(self, func):
        pass


class CallbackDelayer(ICallbackDelayer):

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

    def delayCallback(self, uniqueID, seconds, function, *args, **kwargs):
        self.stopCallback(uniqueID)
        self.__callbackIDs[uniqueID] = BigWorld.callback(seconds, functools.partial(self.__funcWrapper, uniqueID, function, *args, **kwargs))

    def stopCallback(self, uniqueID):
        callbackID = self.__callbackIDs.pop(uniqueID, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        return

    def hasDelayedCallbackID(self, uniqueID):
        return uniqueID in self.__callbackIDs

    def __funcWrapper(self, uniqueID, func, *args, **kwargs):
        self.__callbackIDs[uniqueID] = None
        func(*args, **kwargs)
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


class CallbackPauseManager(ICallbackDelayer):

    def __init__(self):
        self.__callbacks = {}
        self.__isPaused = False
        self.__pauseTime = 0.0
        self.__timeFunc = BigWorld.time

    def destroy(self):
        self.clearCallbacks()

    def clearCallbacks(self):
        self.__isPaused = False
        for callbackRequest in self.__callbacks.itervalues():
            if self.hasDelayedCallback(callbackRequest.func) and callbackRequest.ID is not None:
                BigWorld.cancelCallback(callbackRequest.ID)

        self.__callbacks.clear()
        return

    def delayCallback(self, delay, func, *args, **kwargs):
        if self.__isPaused:
            request = DelayedRequest(None, self.__timeFunc(), delay, func, args, kwargs)
            self.__callbacks[func] = request
            return
        else:
            callbackRequest = self.__callbacks.get(func)
            if callbackRequest and callbackRequest.ID is not None:
                BigWorld.cancelCallback(callbackRequest.ID)
                del self.__callbacks[func]
            self.__addDelayedCallback(delay, func, *args, **kwargs)
            return

    def stopCallback(self, func):
        request = self.__callbacks.pop(func, None)
        if request:
            BigWorld.cancelCallback(request.ID)
        return

    def pauseCallbacks(self):
        if self.__isPaused:
            return
        else:
            self.__isPaused = True
            self.__pauseTime = self.__timeFunc()
            for callbackRequest in self.__callbacks.itervalues():
                if self.hasDelayedCallback(callbackRequest.func):
                    BigWorld.cancelCallback(callbackRequest.ID)
                    self.__callbacks[callbackRequest.func] = DelayedRequest(None, callbackRequest.queuedTime, callbackRequest.delay, callbackRequest.func, callbackRequest.args, callbackRequest.kwargs)

            return

    def resumeCallbacks(self):
        if not self.__isPaused:
            return
        self.__isPaused = False
        for callbackRequest in self.__callbacks.itervalues():
            delaySetback = max(0, self.__pauseTime - callbackRequest.queuedTime)
            self.delayCallback((callbackRequest.delay - delaySetback), callbackRequest.func, *callbackRequest.args, **callbackRequest.kwargs)

    def hasDelayedCallback(self, func):
        return func in self.__callbacks

    def __funcWrapper(self, func, *args, **kwargs):
        self.__callbacks.pop(func, None)
        desiredDelay = func(*args, **kwargs)
        if desiredDelay is not None and desiredDelay >= 0:
            self.__addDelayedCallback(desiredDelay, func, *args, **kwargs)
        return

    def __addDelayedCallback(self, delay, func, *args, **kwargs):
        curId = BigWorld.callback(delay, functools.partial(self.__funcWrapper, func, *args, **kwargs))
        request = DelayedRequest(curId, self.__timeFunc(), delay, func, args, kwargs)
        self.__callbacks[func] = request


DelayedRequest = namedtuple('DelayedRequest', ['ID',
 'queuedTime',
 'delay',
 'func',
 'args',
 'kwargs'])
