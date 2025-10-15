# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/VehicleNodeEffect.py
from functools import partial
import BigWorld
import CGF
from GenericComponents import AnimatorComponent
from vehicle_systems.model_assembler import loadAppearancePrefab
from script_component.DynamicScriptComponent import DynamicScriptComponent
from shared_utils import nextTick

class VehicleNodeEffect(DynamicScriptComponent):

    def __init__(self):
        super(VehicleNodeEffect, self).__init__()
        self.__go = None
        self.__delayedNodeID = None
        return

    def onDestroy(self):
        self.entity.onAppearanceReady -= self.__onAppearanceReady
        self.__go = None
        super(VehicleNodeEffect, self).onDestroy()
        return

    def set_nodeID(self, _):
        if self.nodeID:
            self.__startNodeEffect(self.nodeID)

    def _onAvatarReady(self):
        self.entity.onAppearanceReady += self.__onAppearanceReady
        if self.entity.appearance and self.entity.appearance.isConstructed:
            self.__loadPrefab()

    def __onAppearanceReady(self):
        self.__loadPrefab()

    def __loadPrefab(self):
        loadAppearancePrefab(self.prefabPath, self.entity.appearance, self.__onPrefabLoaded)

    def __onPrefabLoaded(self, go):
        self.__go = go
        if self.__delayedNodeID:
            nextTick(partial(self.__startNodeEffect, self.__delayedNodeID))()
            self.__delayedNodeID = None
        return

    def __getNodeAnimators(self, nodeID):
        if not self.__go or not self.__go.isValid():
            return []
        hm = CGF.HierarchyManager(self.spaceID)
        animators = []
        for effectGO in hm.getChildren(self.__go):
            if nodeID in effectGO.name:
                animators.append(effectGO.findComponentByType(AnimatorComponent))

        return animators

    def __startNodeEffect(self, nodeID):
        if not self.__go:
            self.__delayedNodeID = nodeID
            return
        animators = self.__getNodeAnimators(nodeID)
        for animator in animators:
            if animator:
                animator.start()
                BigWorld.callback(animator.getDuration(), partial(self.__stopNodeEffect, nodeID))

    def __stopNodeEffect(self, nodeID):
        animators = self.__getNodeAnimators(nodeID)
        for animator in animators:
            if animator:
                animator.stop()
