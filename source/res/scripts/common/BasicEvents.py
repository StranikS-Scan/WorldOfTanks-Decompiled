# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/BasicEvents.py
import Event
from debug_utils import LOG_DEBUG_DEV

def _iterEventNames(events):
    return (name for name in dir(events) if name.startswith('on'))


class BasicEvents(object):

    def __init__(self):
        self._eventsDebugger = None
        self._eventManager = Event.EventManager()
        return

    def destroy(self):
        if self._eventsDebugger is not None:
            self._eventsDebugger.clear()
        self._eventManager.clear()
        return

    def debugEvents(self):
        pass


class EventsDebugger(object):

    def __init__(self, events):
        for eventName in _iterEventNames(events):
            event = getattr(events, eventName)
            processor = getattr(self, eventName)
            event += processor

    def _shouldHandle(self, eventName):
        return True

    def _getDebugPrefix(self):
        pass

    def _buildDebugString(self, item):
        return '%s %s' % (self._getDebugPrefix(), item)

    def __getattr__(self, item):
        if self._shouldHandle(item):
            return lambda *args, **kwargs: LOG_DEBUG_DEV(self._buildDebugString(item), *args, **kwargs)
        else:
            return lambda *args, **kwargs: None
