# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/CosmicLoot.py
import BigWorld
import CGF
import Math
import cosmic_prefabs
from cosmic_event_common.cosmic_constants import LOOT_TYPE
from cosmic_sound import CosmicBattleSounds

class CosmicLoot(BigWorld.Entity):
    LOOT_TYPE_ID_TO_PREFAB = {LOOT_TYPE.COSMIC_BLACK_HOLE: cosmic_prefabs.Loot.COSMIC_BLACK_HOLE,
     LOOT_TYPE.COSMIC_SHOOTING: cosmic_prefabs.Loot.COSMIC_SHOOTING,
     LOOT_TYPE.COSMIC_GRAVITY_FIELD: cosmic_prefabs.Loot.COSMIC_GRAVITY_FIELD,
     LOOT_TYPE.COSMIC_POWER_SHOT: cosmic_prefabs.Loot.COSMIC_POWER_SHOT}

    def __init__(self):
        super(CosmicLoot, self).__init__()
        self.__go = None
        return

    def onEnterWorld(self, *args):
        prefab = self.LOOT_TYPE_ID_TO_PREFAB.get(self.typeID)
        if prefab:
            CGF.loadGameObjectIntoHierarchy(prefab, self.entityGameObject, Math.Vector3(), self.__onPrefabLoaded)
        CosmicBattleSounds.playDronAppear(self.position)

    def onLeaveWorld(self):
        CosmicBattleSounds.playDronDisappear(self.position)
        self.__removeGO()

    def __onPrefabLoaded(self, go):
        self.__go = go

    def __removeGO(self):
        if self.__go is not None:
            CGF.removeGameObject(self.__go)
        self.__go = None
        return
