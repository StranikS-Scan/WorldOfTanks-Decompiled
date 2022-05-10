# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/ArenaInfoDeathZonesComponent.py
import CGF
import Math
from death_zones_helpers import ZONE_STATE, DEATH_ZONE_IDS
from script_component.DynamicScriptComponent import DynamicScriptComponent

class ArenaInfoDeathZonesComponent(DynamicScriptComponent):

    def __init__(self):
        super(ArenaInfoDeathZonesComponent, self).__init__()
        prefab = 'content/CGFPrefabs/steel_hunter/death_zones_rules.prefab'
        CGF.loadGameObject(prefab, self.entity.spaceID, Math.Vector3(0, 0, 0))
        self.visibilityMskZones = [ 0 for _ in enumerate(DEATH_ZONE_IDS) ]
        self.updatedZones = []

    def _onAvatarReady(self):
        self.updatedZones = [ idx for idx, value in enumerate(self.activeZones) if value != ZONE_STATE.SAVE ]

    def setNested_activeZones(self, changePath, oldValue):
        self.updatedZones.extend(range(changePath[0], changePath[0] + 1))

    def setSlice_activeZones(self, path, oldValue):
        startIdx, stopIdx = path[-1]
        self.updatedZones.extend(range(startIdx, stopIdx))
