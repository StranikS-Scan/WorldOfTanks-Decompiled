# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/events_debugger.py
from debug_utils import LOG_DEBUG_DEV

def _iterEventNames(events):
    return (name for name in dir(events) if name.startswith('on'))


class EventsDebugger(object):

    def __init__(self, events):
        for eventName in self._iterEventNames(events):
            event = getattr(events, eventName)
            processor = getattr(self, eventName)
            event += processor

    def _getDebugPrefix(self):
        pass

    def _buildDebugString(self, item):
        return '%s %s' % (self._getDebugPrefix(), item)

    def _iterEventNames(self, events):
        return (eventName for eventName in _iterEventNames(events) if self._shouldHandle(eventName))

    def _shouldHandle(self, eventName):
        return True

    def __getattr__(self, item):
        return lambda *args, **kwargs: LOG_DEBUG_DEV(self._buildDebugString(item), *args, **kwargs)
