# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/func_utils.py
from functools import partial
from time import sleep
import BigWorld
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
