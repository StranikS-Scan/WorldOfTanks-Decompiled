# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ArenaInfo.py
import cPickle
import zlib
import BigWorld
from arena_info_components.vehicles_area_marker_info import VehiclesAreaMarkerInfo
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import AirDropEvent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
ARENA_INFO_COMPONENTS = {VehiclesAreaMarkerInfo}

class ArenaInfo(BigWorld.Entity, VehiclesAreaMarkerInfo):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        for comp in ARENA_INFO_COMPONENTS:
            comp.__init__(self)

        self._bonusByQuestID = {}
        self.__setAverageLevel()

    def set_vehiclesAverageBattleLevel(self, _):
        self.__setAverageLevel()

    def setSlice_lootPositions(self, path, oldValue):
        addedItems = _getNewValue(self.lootPositions, path)
        removedItems = oldValue
        for item in addedItems:
            event = AirDropEvent(AirDropEvent.AIR_DROP_LOOP_ENTERED, ctx=item)
            g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.BATTLE)

        for item in removedItems:
            event = AirDropEvent(AirDropEvent.AIR_DROP_LOOP_LEFT, ctx=item)
            g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.BATTLE)

    def set_lootPositions(self, prevLootPositions):
        for item in prevLootPositions:
            event = AirDropEvent(AirDropEvent.AIR_DROP_LOOP_LEFT, ctx=item)
            g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.BATTLE)

        for item in self.lootPositions:
            event = AirDropEvent(AirDropEvent.AIR_DROP_LOOP_ENTERED, ctx=item)
            g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.BATTLE)

    def set_bonusByQuestID(self, _):
        self.__unpackBonusByQuestID()

    def onEnterWorld(self, prereqs):
        for comp in ARENA_INFO_COMPONENTS:
            comp.onEnterWorld(self)

        BigWorld.player().arena.registerArenaInfo(self)
        self.__unpackBonusByQuestID()

    def onLeaveWorld(self):
        for comp in ARENA_INFO_COMPONENTS:
            comp.onLeaveWorld(self)

        BigWorld.player().arena.unregisterArenaInfo(self)
        self._bonusByQuestID.clear()

    def getBonusByQuestID(self):
        return self._bonusByQuestID

    def __unpackBonusByQuestID(self):
        if self.bonusByQuestID:
            self._bonusByQuestID = cPickle.loads(zlib.decompress(self.bonusByQuestID))

    def __setAverageLevel(self):
        progressionCtrl = self.sessionProvider.dynamic.progression
        if progressionCtrl is not None:
            progressionCtrl.setAverageBattleLevel(self.vehiclesAverageBattleLevel)
        return


def _getNewValue(sequence, path):
    startIndex, endIndex = path[-1]
    return sequence[startIndex:endIndex]
