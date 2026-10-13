# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/VehiclePrefabEffect.py
import CGF
from functools import partial
from shared_utils import nextTick
from script_component.DynamicScriptComponent import DynamicScriptComponent
from vehicle_systems.model_assembler import loadAppearancePrefab

class VehiclePrefabEffect(DynamicScriptComponent):

    def __init__(self):
        super(VehiclePrefabEffect, self).__init__()
        self.__go = None
        return

    def onDestroy(self):
        self.__removeGO(self.__go)
        self.__go = None
        super(VehiclePrefabEffect, self).onDestroy()
        return

    def _onAvatarReady(self):
        self.__activate()

    def __hasAppearance(self):
        return hasattr(self.entity, 'appearance') and hasattr(self.entity, 'onAppearanceReady')

    @nextTick
    def __activate(self):
        if self.entity.isDestroyed:
            return
        else:
            if self.__go is None and self.prefabPath:
                if self.isAppearanceLoad and self.__hasAppearance():
                    appearance = self.entity.appearance
                    if appearance is None or not appearance.isConstructed:
                        self.entity.onAppearanceReady += self.__loadInAppearance
                    else:
                        self.__loadInAppearance()
                else:
                    self.__loadIntoHierarchy()
            return

    def __loadInAppearance(self):
        if self.entity.isDestroyed:
            return
        elif not self.__hasAppearance():
            return
        else:
            appearance = self.entity.appearance
            self.entity.onAppearanceReady -= self.__loadInAppearance
            if appearance is None:
                return
            loadAppearancePrefab(self.prefabPath, appearance, partial(self.__onPrefabLoaded, keyName=self.keyName))
            return

    def __loadIntoHierarchy(self):
        CGF.loadGameObjectIntoHierarchy(self.prefabPath, self.entity.entityGameObject, self.position, partial(self.__onPrefabLoaded, keyName=self.keyName))

    def __onPrefabLoaded(self, go, keyName):
        if not self.entity.dynamicComponents.get(keyName):
            self.__removeGO(go)
            return
        self.__go = go

    def __removeGO(self, go):
        if go and go.isValid():
            CGF.removeGameObject(go)
