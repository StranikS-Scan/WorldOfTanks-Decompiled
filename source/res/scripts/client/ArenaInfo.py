# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ArenaInfo.py
import cPickle
import zlib
import BigWorld
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import AirDropEvent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class ArenaInfo(BigWorld.Entity):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
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
        BigWorld.player().arena.registerArenaInfo(self)
        self.__unpackBonusByQuestID()

    def onLeaveWorld(self):
        BigWorld.player().arena.unregisterArenaInfo(self)
        self._bonusByQuestID.clear()

    def getBonusByQuestID(self):
        return self._bonusByQuestID

    def __unpackBonusByQuestID(self):
        if self.bonusByQuestID:
            self._bonusByQuestID = cPickle.loads(zlib.decompress(self.bonusByQuestID))

    def __setAverageLevel(self):
        progressionCtrl = self.__sessionProvider.dynamic.progression
        if progressionCtrl is not None:
            progressionCtrl.setAverageBattleLevel(self.vehiclesAverageBattleLevel)
        return


def _getNewValue(sequence, path):
    startIndex, endIndex = path[-1]
    return sequence[startIndex:endIndex]
