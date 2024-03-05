# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event_dyn_objects_cache.py
import BigWorld
import CGF
import cosmic_prefabs
from dyn_objects_cache import DynObjectsBase, _PointsOfInterestConfig
from vehicle_systems.stricted_loading import makeCallbackWeak

class CosmicEventDynObjects(DynObjectsBase):

    def __init__(self):
        super(CosmicEventDynObjects, self).__init__()
        self.__pointsOfInterestConfig = None
        self.__cosmicShields = None
        self.__cachedPrefabs = set()
        self.__resourcesCache = None
        self.lootPrefabs = {}
        return

    def init(self, dataSection):
        super(CosmicEventDynObjects, self).init(dataSection)
        self.__pointsOfInterestConfig = _PointsOfInterestConfig({(10, 13): cosmic_prefabs.Artifact.SMALL_HINT,
         (17, 22): cosmic_prefabs.Artifact.BIG_HINT})
        self.__cachedPrefabs.update(set(self.__pointsOfInterestConfig.getPrefabs()))
        self._collectLootPrefabs()
        self._collectVehiclePrefabs()
        self._collectArtifactPrefabs()
        self._collectOtherPrefabs()
        BigWorld.loadResourceListBG(list(self.__cachedPrefabs), makeCallbackWeak(self.__onResourcesLoaded))
        CGF.cacheGameObjects(list(self.__cachedPrefabs), False)

    def clear(self):
        self.__pointsOfInterestConfig = None
        if self.__cachedPrefabs:
            CGF.clearGameObjectsCache(list(self.__cachedPrefabs))
            self.__cachedPrefabs.clear()
        super(CosmicEventDynObjects, self).clear()
        return

    def destroy(self):
        self.__resourcesCache = None
        super(CosmicEventDynObjects, self).destroy()
        return

    def getPointOfInterestConfig(self):
        return self.__pointsOfInterestConfig

    def __onResourcesLoaded(self, resourceRefs):
        self.__resourcesCache = resourceRefs

    def _collectLootPrefabs(self):
        prefabs = cosmic_prefabs.Loot.RANGE_LOOT
        self.__cachedPrefabs.update(prefabs)

    def _collectVehiclePrefabs(self):
        prefabs = cosmic_prefabs.Vehicle.RANGE
        self.__cachedPrefabs.update(prefabs)

    def _collectArtifactPrefabs(self):
        prefabs = cosmic_prefabs.Artifact.RANGE
        self.__cachedPrefabs.update(prefabs)

    def _collectOtherPrefabs(self):
        prefabs = ('content/CGFPrefabs/cosmic_event/cosmic_event_ability_pickup_end.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_event_ability_pickup_start.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_event_artifact_gathering.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_event_artifact_idle.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_event_artifact_spawn_abilities.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_event_artifact_spawn_s_zone_01.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_event_overcharge.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_event_passive_shield_shockwave.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_event_power_shot_mode.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_event_respawn_protection.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_event_rocket_booster.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_event_shield.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_event_sniper_mode.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_event_supernova.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_event_supernova_hint.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_event_teleport_in.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_event_teleport_out.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_event_zone_s.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_vehicle_emissive.prefab', 'content/CGFPrefabs/cosmic_event/cosmic_vehicle_shot_anim.prefab')
        self.__cachedPrefabs.update(prefabs)
