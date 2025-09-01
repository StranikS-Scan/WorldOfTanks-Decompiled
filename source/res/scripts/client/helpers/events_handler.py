# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/events_handler.py
from typing import TYPE_CHECKING
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared import g_eventBus
if TYPE_CHECKING:
    from typing import Callable, Optional, Tuple
    from Event import Event

class EventsHandler(object):
    __slots__ = ()

    def _getCallbacks(self):
        return tuple()

    def _getListeners(self):
        return tuple()

    def _getEvents(self):
        return tuple()

    def _getRestrictions(self):
        return tuple()

    def _subscribe(self):
        g_clientUpdateManager.addCallbacks(dict(self._getCallbacks()))
        for eventBusArgs in self._getListeners():
            g_eventBus.addListener(*eventBusArgs)

        for eventBusRestrictionArgs in self._getRestrictions():
            g_eventBus.addRestriction(*eventBusRestrictionArgs)

        for event, handler in self._getEvents():
            event += handler

    def _unsubscribe(self):
        for event, handler in self._getEvents():
            event -= handler

        for eventBusRestrictionArgs in self._getRestrictions():
            g_eventBus.removeRestriction(*eventBusRestrictionArgs)

        for eventBusArgs in self._getListeners():
            g_eventBus.removeListener(*eventBusArgs[:3])

        g_clientUpdateManager.removeObjectCallbacks(self)
