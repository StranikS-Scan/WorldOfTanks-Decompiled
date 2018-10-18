# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/__init__.py
from gui.server_events.EventsCache import EventsCache as _EventsCache
from gui.server_events.linkedset_controller import LinkedSetController as _LinkedSetController
from gui.server_events.halloween_controller import HalloweenController as _HalloweenController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.linkedset import ILinkedSetController
from skeletons.gui.halloween_controller import IHalloweenController
__all__ = ('getServerEventsConfig', 'getLinkedSetController', 'getHalloweenController')

def getServerEventsConfig(manager):
    _getStandartController(manager, IEventsCache, _EventsCache)


def getLinkedSetController(manager):
    _getStandartController(manager, ILinkedSetController, _LinkedSetController)


def getHalloweenController(manager):
    _getStandartController(manager, IHalloweenController, _HalloweenController)


def _getStandartController(manager, interfaceType, implType):
    controller = implType()
    controller.init()
    manager.addInstance(interfaceType, controller, finalizer='fini')
