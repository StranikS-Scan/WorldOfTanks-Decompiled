# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/TimeInterval.py
import logging
import typing
import weakref
import BigWorld
from Event import SafeEvent
if typing.TYPE_CHECKING:
    from Event import EventManager
_logger = logging.getLogger(__name__)

class TimeInterval(object):
    __slots__ = ('__callbackID', '__interval', '__obj', '__name')

    def __init__(self, interval, obj, name):
        self.__callbackID = None
        self.__interval = interval
        self.__obj = weakref.ref(obj)
        self.__name = name
        return

    def restart(self):
        self.stop()
        self.start()

    def start(self):
        if self.__callbackID is not None:
            _logger.error('To start a new time interval You should before stop already the running time interval.')
            return
        else:
            self.__callbackID = BigWorld.callback(self.__interval, self.__invoke)
            return

    def stop(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def isStarted(self):
        return self.__callbackID is not None

    def __invoke(self):
        self.__callbackID = None
        self.__callbackID = BigWorld.callback(self.__interval, self.__invoke)
        obj = self.__obj()
        if obj is not None:
            func = getattr(obj, self.__name, None)
            if func and callable(func):
                func()
        return


class TimeIntervalEvent(SafeEvent):
    __slots__ = ('_timeCallback', '__timeInterval')

    def __init__(self, interval, timeCallback=None, manager=None):
        super(TimeIntervalEvent, self).__init__(manager)
        self._timeCallback = timeCallback or self.__call__
        self.__timeInterval = TimeInterval(interval, self, '_timeCallback')

    def __iadd__(self, delegate):
        result = super(TimeIntervalEvent, self).__iadd__(delegate)
        if self.hasListeners() and not self.__timeInterval.isStarted():
            self.__timeInterval.start()
        return result

    def __isub__(self, delegate):
        result = super(TimeIntervalEvent, self).__isub__(delegate)
        if not self.hasListeners() and self.__timeInterval.isStarted():
            self.__timeInterval.stop()
        return result

    def hasListeners(self):
        return len(self) > 0

    def clear(self):
        self._timeCallback = None
        self.__timeInterval.stop()
        super(TimeIntervalEvent, self).clear()
        return
