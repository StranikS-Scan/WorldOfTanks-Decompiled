# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/AvatarLoot.py
import BigWorld
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from debug_utils import LOG_DEBUG_DEV

class AvatarLoot(BigWorld.DynamicScriptComponent):

    def onLootAction(self, lootID, lootTypeID, action, serverTime):
        LOG_DEBUG_DEV('onLootAction', lootID, lootTypeID, action, serverTime)
        self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.LOOT, (lootID,
         lootTypeID,
         action,
         serverTime))
