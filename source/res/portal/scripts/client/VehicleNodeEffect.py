# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/VehicleNodeEffect.py
from functools import partial
import BigWorld
import CGF
from GenericComponents import AnimatorComponent, RemoveGoDelayedComponent
from vehicle_systems.model_assembler import loadAppearancePrefab
from script_component.DynamicScriptComponent import DynamicScriptComponent
from shared_utils import nextTick

class VehicleNodeEffect(DynamicScriptComponent):

    def __init__(self):
        self.__go = None
        super(VehicleNodeEffect, self).__init__()
        return

    def set_nodeID(self, *args):
        if self.nodeID:
            self.__loadPrefab()

    def onDestroy(self):
        arena = BigWorld.player().arena
        if arena is not None:
            arena.onVehicleKilled -= self.__onArenaVehicleKilled
        self.__go = None
        super(VehicleNodeEffect, self).onDestroy()
        return

    def _onAvatarReady(self, *args):
        arena = BigWorld.player().arena
        if arena is not None:
            arena.onVehicleKilled += self.__onArenaVehicleKilled
        return

    def __onArenaVehicleKilled(self, *args):
        if self.__go is not None and self.__go.isValid():
            CGF.removeGameObject(self.__go)
            self.__go = None
        return

    def __loadPrefab(self):
        loadAppearancePrefab(self.prefabPath, self.entity.appearance, self.__onPrefabLoaded)

    def __onPrefabLoaded(self, go):
        self.__go = go
        if self.nodeID is not None:
            nextTick(partial(self.__startNodeEffect, self.nodeID))()
        return

    def __startNodeEffect(self, nodeID):
        if self.__go is None or not self.__go.isValid():
            return
        else:
            animators = self.__getNodeAnimators(nodeID)
            if not animators:
                return
            duration = max([ animator.getDuration() for animator in animators ])
            if self.__go.findComponentByType(RemoveGoDelayedComponent) is None:
                self.__go.createComponent(RemoveGoDelayedComponent, duration)
            return

    def __getNodeAnimators(self, nodeID):
        if self.entity.isDestroyed:
            return []
        hm = CGF.HierarchyManager(self.spaceID)
        animators = []
        for effectGO in hm.getChildren(self.__go):
            if nodeID in effectGO.name:
                animators.append(effectGO.findComponentByType(AnimatorComponent))

        return animators
