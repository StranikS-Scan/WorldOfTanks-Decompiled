# Embedded file name: scripts/client/gui/shared/utils/decorators.py
import time
import adisp
from debug_utils import LOG_DEBUG
from gui.Scaleform.Waiting import Waiting

class process(object):

    def __init__(self, *kargs):
        self.__currentMessage = None
        self.__messages = kargs
        self.__messages2Show = list(self.__messages)
        return

    def __hideWaiting(self):
        if self.__currentMessage is not None:
            Waiting.hide(self.__currentMessage)
            self.__currentMessage = None
        return

    def __nextWaiting(self):
        if len(self.__messages2Show):
            self.__hideWaiting()
            self.__currentMessage = self.__messages2Show.pop(0)
            Waiting.show(self.__currentMessage)

    def __stepCallback(self, isStop):
        if not isStop:
            return self.__nextWaiting()
        self.__hideWaiting()
        self.__messages2Show = list(self.__messages)

    def __call__(self, func):

        def wrapper(*kargs, **kwargs):
            self.__nextWaiting()
            return adisp.process(func, self.__stepCallback)(*kargs, **kwargs)

        return wrapper


def async(func, cbname = 'callback', cbwrapper = lambda x: x):

    def wrapper(*kargs, **kwargs):
        if cbname in func.func_code.co_varnames:
            idx = func.func_code.co_varnames.index(cbname)
            if idx >= len(kargs) and cbname not in kwargs:
                return adisp.async(func, cbname, cbwrapper)(*kargs, **kwargs)
        return func(*kargs, **kwargs)

    return wrapper


def dialog(func):

    def wrapper(*kargs, **kwargs):
        Waiting.suspend()

        def cbwrapper(cb):

            def callback(result):
                Waiting.resume()
                cb(result)

            return callback

        return async(func, 'callback', cbwrapper)(*kargs, **kwargs)

    return wrapper


def debugTime(func):

    def wrapper(*args, **kwargs):
        startTime = time.time()
        func(*args, **kwargs)
        LOG_DEBUG("Method '%s' measuring time: %.5f" % (func.__name__, time.time() - startTime))

    return wrapper
