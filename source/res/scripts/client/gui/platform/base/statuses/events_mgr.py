# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/base/statuses/events_mgr.py
import typing
import Event
from gui.platform.base.logger import getWithContext
from gui.platform.base.statuses.constants import StatusTypes, DEFAULT_CONTEXT
if typing.TYPE_CHECKING:
    from gui.platform.base.statuses.status import Status

class StatusEventsManager(object):

    def __init__(self):
        self._logger = getWithContext(instance=self)
        self._em = Event.EventManager()
        self._events = {}

    def subscribe(self, statusType, handler, context=DEFAULT_CONTEXT):
        events = self._events.setdefault(context, {})
        if statusType not in events:
            events[statusType] = Event.SafeEvent(self._em)
        events[statusType] += handler
        self._logger.debug('Subscribed to (%s|%s|%s).', context, statusType, handler)

    def unsubscribe(self, statusType, handler, context=DEFAULT_CONTEXT):
        event = self._get(context, statusType)
        if event:
            event -= handler
            self._logger.debug('Unsubscribed from (%s|%s|%s).', context, statusType, handler)

    def send(self, status, context=DEFAULT_CONTEXT):
        event = self._get(context, status.type)
        if event:
            self._logger.debug('Sending %s for (%s|%s).', status, context, event)
            event(status)

    def clear(self):
        self._em.clear()
        self._events.clear()
        self._logger.debug('All events cleared.')

    def _get(self, context, statusType):
        return self._events.get(context, {}).get(statusType)
