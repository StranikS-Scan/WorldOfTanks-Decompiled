# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleBRRespawnEffectComponent.py
import CGF
from Math import Vector3
import Event
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider

class VehicleBRRespawnEffectComponent(DynamicScriptComponent):
    __dynObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    onRespawned = Event.Event()

    def _onAvatarReady(self):
        self.__playEffect()
        self.onRespawned(self.entity.id)

    def __playEffect(self):
        prefabPath = self.__dynObjectsCache.getConfig(self.__sessionProvider.arenaVisitor.getArenaGuiType()).getVehicleRespawnEffect().effectPrefabPath
        CGF.loadGameObjectIntoHierarchy(prefabPath, self.entity.entityGameObject, Vector3(0))
