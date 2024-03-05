# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/CosmicLoot.py
import BigWorld
import CGF
import Math
import cosmic_prefabs
from cosmic_event_common.cosmic_constants import LOOT_TYPE

class CosmicLoot(BigWorld.Entity):
    LOOT_TYPE_ID_TO_PREFAB = {LOOT_TYPE.COSMIC_BLACK_HOLE: cosmic_prefabs.Loot.COSMIC_BLACK_HOLE,
     LOOT_TYPE.COSMIC_SHOOTING: cosmic_prefabs.Loot.COSMIC_SHOOTING,
     LOOT_TYPE.COSMIC_GRAVITY_FIELD: cosmic_prefabs.Loot.COSMIC_GRAVITY_FIELD,
     LOOT_TYPE.COSMIC_POWER_SHOT: cosmic_prefabs.Loot.COSMIC_POWER_SHOT}

    def onEnterWorld(self, *args):
        prefab = self.LOOT_TYPE_ID_TO_PREFAB.get(self.typeID)
        if prefab:
            CGF.loadGameObjectIntoHierarchy(prefab, self.entityGameObject, Math.Vector3())
