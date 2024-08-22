# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/container_views/base/controllers.py
import typing
from Event import Event
from helpers import dependency
from gui.impl.lobby.container_views.base.events import ComponentEventsBase
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Callable, List, Tuple

class InteractionController(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, view=None):
        self.__eventsProvider = self._getEventsProvider()
        self.__view = view

    @property
    def context(self):
        return self.view.context

    @property
    def eventsProvider(self):
        return self.__eventsProvider

    @property
    def view(self):
        return self.__view

    def subscribe(self):
        for event, handler in self._getEvents():
            event += handler

    def unsubscribe(self):
        for event, handler in self._getEvents():
            event -= handler

    def refresh(self):
        self.view.refresh()

    def _getEventsProvider(self):
        raise NotImplementedError

    def _getEvents(self):
        return []
