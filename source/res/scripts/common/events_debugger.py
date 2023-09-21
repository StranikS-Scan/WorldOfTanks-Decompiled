# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/events_debugger.py
from debug_utils import LOG_DEBUG_DEV

def _iterEventNames(events):
    return (name for name in dir(events) if name.startswith('on'))


class EventsDebugger(object):

    def __init__(self, events):
        for eventName in _iterEventNames(events):
            self.attachTo(events, eventName)

    def attachTo(self, events, eventName):
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
