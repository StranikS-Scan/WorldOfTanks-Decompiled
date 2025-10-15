# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/PortalVehicleInfluenceZoneComponent.py
import BigWorld
import CGF
import Math
import Sound
from helpers import dependency
from portal.sounds.sound_constants import PortalAbilitySound
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from items import vehicles

class PortalVehicleInfluenceZoneComponent(BigWorld.DynamicScriptComponent):
    __dynamicObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)

    def set_isActive(self, prev):
        if prev != self.isActive:
            if self.isActive:
                effectSettings = self.__getEffectSettings()
                if effectSettings is not None:
                    equipment = vehicles.g_cache.equipments()[self.equipmentID]
                    self.entity.appearance.showTerrainCircle(equipment.params['radius'], effectSettings)
                    go = self.entity.entityGameObject
                    soundName = PortalAbilitySound.RELOAD_AURA_START
                    sentinelOnSound3D = go.findComponentByType(Sound.Sound3DComponent)
                    if sentinelOnSound3D:
                        go.removeComponent(sentinelOnSound3D)
                    go.createComponent(Sound.Sound3DComponent, soundName, soundName, True)
            else:
                compoundAppearance = self.entity.appearance
                if compoundAppearance.activated:
                    compoundAppearance.hideTerrainCircle()
                go = self.entity.entityGameObject
                sound3D = go.findComponentByType(Sound.Sound3DComponent)
                if sound3D:
                    go.removeComponent(sound3D)
                prefabPath = 'content/CGFPrefabs/portal/reload_aura_stop.prefab'
                CGF.loadGameObjectIntoHierarchy(prefabPath, go, Math.Vector3(0, 0, 0))
        return

    def __getEffectSettings(self):
        dynamicObjects = self.__dynamicObjectsCache.getConfig(BigWorld.player().arenaGuiType)
        return None if dynamicObjects is None else dynamicObjects.getInfluenceZoneCircleEffect().get('ally')
