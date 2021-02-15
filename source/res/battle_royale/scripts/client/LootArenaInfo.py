# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/LootArenaInfo.py
import BigWorld
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import AirDropEvent

class LootArenaInfo(BigWorld.DynamicScriptComponent):

    def set_lootPositions(self, prevLootPositions):
        for item in prevLootPositions:
            event = AirDropEvent(AirDropEvent.AIR_DROP_LOOP_LEFT, ctx=item)
            g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.BATTLE)

        for item in self.lootPositions:
            event = AirDropEvent(AirDropEvent.AIR_DROP_LOOP_ENTERED, ctx=item)
            g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.BATTLE)

    def setSlice_lootPositions(self, path, oldValue):
        addedItems = _getNewValue(self.lootPositions, path)
        removedItems = oldValue
        for item in addedItems:
            event = AirDropEvent(AirDropEvent.AIR_DROP_LOOP_ENTERED, ctx=item)
            g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.BATTLE)

        for item in removedItems:
            event = AirDropEvent(AirDropEvent.AIR_DROP_LOOP_LEFT, ctx=item)
            g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.BATTLE)


def _getNewValue(sequence, path):
    startIndex, endIndex = path[-1]
    return sequence[startIndex:endIndex]
