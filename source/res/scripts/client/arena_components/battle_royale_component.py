# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/arena_components/battle_royale_component.py
from arena_component_system.client_arena_component_system import ClientArenaComponent
import Event
from debug_utils import LOG_DEBUG_DEV

class BattleRoyaleComponent(ClientArenaComponent):

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        self.__place = None
        self.onBattleRoyalePlaceUpdated = Event.Event(self._eventManager)
        return

    def setBattleRoyalePlace(self, place):
        LOG_DEBUG_DEV('__setBattleRoyalePlace', place)
        self.__place = place
        self.onBattleRoyalePlaceUpdated(place)

    @property
    def place(self):
        return self.__place
