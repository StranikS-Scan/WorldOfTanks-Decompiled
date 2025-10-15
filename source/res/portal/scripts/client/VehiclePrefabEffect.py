# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/VehiclePrefabEffect.py
import CGF
from functools import partial
from shared_utils import nextTick
from script_component.DynamicScriptComponent import DynamicScriptComponent

class VehiclePrefabEffect(DynamicScriptComponent):

    def __init__(self):
        super(VehiclePrefabEffect, self).__init__()
        self.__go = None
        return

    def onDestroy(self):
        if self.__go and self.__go.isValid():
            CGF.removeGameObject(self.__go)
        self.__go = None
        super(VehiclePrefabEffect, self).onDestroy()
        return

    def _onAvatarReady(self):
        if self.prefabPath:
            self.__loadPrefab()

    @nextTick
    def __loadPrefab(self):
        CGF.loadGameObjectIntoHierarchy(self.prefabPath, self.entity.entityGameObject, self.position, partial(self.__onPrefabLoaded, keyName=self.keyName))

    def __onPrefabLoaded(self, go, keyName):
        if not self.entity.dynamicComponents.get(keyName):
            CGF.removeGameObject(go)
            return
        self.__go = go
