# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/arena_components/battle_royale_component.py
from arena_component_system.client_arena_component_system import ClientArenaComponent
import Event
from debug_utils import LOG_DEBUG_DEV

class BattleRoyaleComponent(ClientArenaComponent):

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        self.__place = None
        self.__defeatedTeams = []
        self.__isRespawnFinished = False
        self.onBattleRoyalePlaceUpdated = Event.Event(self._eventManager)
        self.onBattleRoyaleDefeatedTeamsUpdate = Event.Event(self._eventManager)
        self.onRespawnTimeFinished = Event.Event(self._eventManager)
        return

    def setBattleRoyalePlace(self, place):
        LOG_DEBUG_DEV('setBattleRoyalePlace', place)
        self.__place = place
        self.onBattleRoyalePlaceUpdated(place)

    def setDefeatedTeams(self, defeatedTeams):
        LOG_DEBUG_DEV('setDefeatedTeams', defeatedTeams)
        self.__defeatedTeams = defeatedTeams
        self.onBattleRoyaleDefeatedTeamsUpdate(defeatedTeams)

    def setOnRespawnTimeFinished(self):
        self.__isRespawnFinished = True
        self.onRespawnTimeFinished()

    @property
    def place(self):
        return self.__place

    @property
    def defeatedTeams(self):
        return self.__defeatedTeams

    @property
    def isRespawnFinished(self):
        return self.__isRespawnFinished
