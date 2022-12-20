# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/events_handler.py
import typing
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared import g_eventBus
if typing.TYPE_CHECKING:
    from typing import Callable, Optional, Sequence, Tuple
    from Event import Event

class EventsHandler(object):
    __slots__ = ()

    def _getCallbacks(self):
        pass

    def _getListeners(self):
        pass

    def _getEvents(self):
        pass

    def _subscribe(self):
        g_clientUpdateManager.addCallbacks(dict(self._getCallbacks()))
        for eventBusArgs in self._getListeners():
            g_eventBus.addListener(*eventBusArgs)

        for event, handler in self._getEvents():
            event += handler

    def _unsubscribe(self):
        for event, handler in reversed(self._getEvents()):
            event -= handler

        for eventBusArgs in reversed(self._getListeners()):
            g_eventBus.removeListener(*eventBusArgs[:3])

        g_clientUpdateManager.removeObjectCallbacks(self)
