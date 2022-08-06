# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/__init__.py
from gui.server_events.EventsCache import EventsCache as _EventsCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.battle_matters import IBattleMattersController
__all__ = ('getServerEventsConfig', 'getLinkedSetController')

def getServerEventsConfig(manager):
    cache = _EventsCache()
    cache.init()
    manager.addInstance(IEventsCache, cache, finalizer='fini')


def getLinkedSetController(manager):
    from gui.game_control.battle_matters_controller import BattleMattersController as _LinkedSetController
    controller = _LinkedSetController()
    controller.init()
    manager.addInstance(IBattleMattersController, controller, finalizer='fini')
