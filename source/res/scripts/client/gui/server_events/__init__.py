# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/__init__.py
from gui.server_events.EventsCache import EventsCache as _EventsCache
from gui.server_events.linkedset_controller import LinkedSetController as _LinkedSetController
from gui.server_events.game_event.game_event_controller import GameEventController as _GameEventController
from gui.server_events.game_event.afk_controller import AFKController as _AFKController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.linkedset import ILinkedSetController
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.afk_controller import IAFKController
__all__ = ('getServerEventsConfig', 'getLinkedSetController', 'getGameEventController', 'getAFKController')

def getServerEventsConfig(manager):
    _getStandartController(manager, IEventsCache, _EventsCache)


def getLinkedSetController(manager):
    _getStandartController(manager, ILinkedSetController, _LinkedSetController)


def getGameEventController(manager):
    _getStandartController(manager, IGameEventController, _GameEventController)


def getAFKController(manager):
    _getStandartController(manager, IAFKController, _AFKController)


def _getStandartController(manager, interfaceType, implType):
    controller = implType()
    controller.init()
    manager.addInstance(interfaceType, controller, finalizer='fini')
