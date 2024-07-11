# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/RacesLoot.py
import BigWorld
import CGF
import Math
import races_prefabs
from races_common.races_constants import LOOT_TYPE

class RacesLoot(BigWorld.Entity):
    LOOT_TYPE_ID_TO_PREFAB = {LOOT_TYPE.RACES_RAPIDSHELLING: races_prefabs.Loot.RACES_RAPIDSHELLING,
     LOOT_TYPE.RACES_SHIELD: races_prefabs.Loot.RACES_SHIELD,
     LOOT_TYPE.RACES_ROCKET_BOOSTER: races_prefabs.Loot.RACES_ROCKET_BOOSTER,
     LOOT_TYPE.RACES_POWER_IMPULSE: races_prefabs.Loot.RACES_POWER_IMPULSE}

    def onEnterWorld(self, *args):
        prefab = self.LOOT_TYPE_ID_TO_PREFAB.get(self.typeID)
        if prefab:
            CGF.loadGameObjectIntoHierarchy(prefab, self.entityGameObject, Math.Vector3())
