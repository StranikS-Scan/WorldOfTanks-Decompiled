# Embedded file name: scripts/client/gui/shared/utils/TimeInterval.py
import weakref
import BigWorld
from debug_utils import LOG_ERROR

class TimeInterval(object):
    __slots__ = ('__callbackID', '__interval', '__obj', '__name')

    def __init__(self, interval, obj, name):
        self.__callbackID = None
        self.__interval = interval
        self.__obj = weakref.ref(obj)
        self.__name = name
        return

    def start(self):
        if self.__callbackID is not None:
            LOG_ERROR('To start a new time interval You should before stop already the running time interval.')
            return
        else:
            self.__callbackID = BigWorld.callback(self.__interval, self.__invoke)
            return

    def stop(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __invoke(self):
        self.__callbackID = None
        self.__callbackID = BigWorld.callback(self.__interval, self.__invoke)
        obj = self.__obj()
        if obj is not None:
            func = getattr(obj, self.__name, None)
            if func and callable(func):
                func()
        return
