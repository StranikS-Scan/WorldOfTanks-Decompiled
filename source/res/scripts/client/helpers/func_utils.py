# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/func_utils.py
from functools import partial, wraps
from time import sleep, time
import BigWorld
from constants import IS_DEVELOPMENT
from debug_utils import LOG_DEBUG
FLASH_IMG_PREFIX = 'img://'

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


def replaceImgPrefix(path):
    return path.replace(FLASH_IMG_PREFIX, '')


def isDeveloperFunc(func):

    @wraps(func)
    def decorator(*args, **kwargs):
        return None if not IS_DEVELOPMENT else func(*args, **kwargs)

    return decorator
