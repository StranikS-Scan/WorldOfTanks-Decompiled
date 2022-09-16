# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/func_utils.py
from collections import namedtuple
from functools import partial
from time import sleep, time
import typing
import BigWorld
from BWUtil import AsyncReturn
from PlayerEvents import g_playerEvents
from wg_async import wg_async, wg_await, AsyncScope, AsyncEvent, BrokenPromiseError
from debug_utils import LOG_DEBUG

def callback(delay, obj, methodName, *args):
    return BigWorld.callback(delay, partial(callMethod, obj, methodName, *args))


def callMethod(obj, methodName, *args):
    if hasattr(obj, methodName):
        getattr(obj, methodName)(*args)


def debugDelay(timeLag):

    def delayCallDecorator(func):

        def delayCall(*args, **kwargs):
            BigWorld.callback(timeLag, partial(func, *args, **kwargs))

        return delayCall

    return delayCallDecorator


def logFunc(func):

    def wrapped(*args, **kwargs):
        LOG_DEBUG('|||||||||||||||||| %s(%s, %s) |||||||||||' % (func.func_name, args, kwargs))
        func(*args, **kwargs)

    return wrapped


def makeFlashPath(s):
    return '..' + s[3:] if s else None


def freeze(seconds, nextFrame=True):
    if nextFrame:
        LOG_DEBUG('Freeze call at', BigWorld.time())
        BigWorld.callback(0, partial(freeze, seconds, False))
        return
    LOG_DEBUG('Actual Freezing at', BigWorld.time())
    sleep(seconds)


def oncePerPeriod(period):
    timeHolder = {intern('lastRequest'): 0.0}

    def wrapper(func):

        def caller(*args, **kwargs):
            currTime = time()
            if currTime - timeHolder['lastRequest'] > period:
                timeHolder['lastRequest'] = currTime
                func(*args, **kwargs)

        return caller

    return wrapper


CallParams = namedtuple('CallParams', ('args', 'kwargs'))
CallParams.__new__.__defaults__ = ((), {})

class CooldownCaller(object):
    __slots__ = ('__call', '__cooldown', '__paramsMerger', '__lock', '__delayedCalls')

    class _Lock(object):
        __slots__ = ('__locked',)

        def __init__(self):
            self.__locked = False

        def __enter__(self):
            self.__locked = True

        def __exit__(self, *_, **__):
            self.__locked = False

        @property
        def locked(self):
            return self.__locked

    def __init__(self, func, cooldown, paramsMerger):
        self.__call = func
        self.__cooldown = cooldown
        self.__paramsMerger = paramsMerger
        self.__lock = self._Lock()
        self.__delayedCalls = []

    def __call__(self, *args, **kwargs):
        if self.__lock.locked:
            self.__delayCall(*args, **kwargs)
        else:
            self.__doCall(*args, **kwargs)

    def __delayCall(self, *args, **kwargs):
        callParams = CallParams(args=args, kwargs=kwargs)
        self.__delayedCalls.append(callParams)

    @wg_async
    def __doCall(self, *args, **kwargs):
        with self.__lock:
            self.__call(*args, **kwargs)
            result = yield wg_await(self.__waitForCooldown())
            if not result:
                self.__delayedCalls = []
        if self.__delayedCalls:
            callParams = self.__mergeDelayedCalls()
            self(*callParams.args, **callParams.kwargs)

    @wg_async
    def __waitForCooldown(self):
        scope = AsyncScope()
        event = AsyncEvent(scope=scope)
        callbackId = BigWorld.callback(self.__cooldown, event.set)
        try:
            try:
                g_playerEvents.onDisconnected += scope.destroy
                yield wg_await(event.wait())
                result = True
            except BrokenPromiseError:
                BigWorld.cancelCallback(callbackId)
                result = False

        finally:
            g_playerEvents.onDisconnected -= scope.destroy

        raise AsyncReturn(result)

    def __mergeDelayedCalls(self):
        merged = CallParams()
        while self.__delayedCalls:
            callParams = self.__delayedCalls.pop(0)
            merged = self.__paramsMerger(merged, callParams)

        return merged


def cooldownCallerDecorator(cooldown, paramsMerger):

    def decorator(func):
        return CooldownCaller(func, cooldown, paramsMerger)

    return decorator
