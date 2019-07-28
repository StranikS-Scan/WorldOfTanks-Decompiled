# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/game_event_getter.py
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class GameEventGetterMixin(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.__gameEventStorage = None
        return

    @property
    def storage(self):
        storage = self.__gameEventStorage
        if not storage:
            componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
            self.__gameEventStorage = storage = getattr(componentSystem, 'gameEventComponent', None)
        return storage

    @property
    def generals(self):
        return self.storage.getGeneralsInBattle()

    @property
    def checkpoints(self):
        return self.storage.getCheckpoints()

    @property
    def lineOfFront(self):
        return self.storage.getLineOfFront()
