# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/PrefabComponent.py
import CGF
import GenericComponents
from script_component.DynamicScriptComponent import DynamicScriptComponent
from vehicle_systems.model_assembler import loadAppearancePrefab

class PrefabComponent(DynamicScriptComponent):

    def __init__(self):
        self.__gameObject = None
        self.__isDestroyed = False
        super(PrefabComponent, self).__init__()
        return

    def _onAvatarReady(self):
        self._activate()

    def onAppearanceReady(self):
        self._activate()

    def onDestroy(self):
        if self.__gameObject and self.__gameObject.isValid():
            CGF.removeGameObject(self.__gameObject)
        self.__gameObject = None
        self.__isDestroyed = True
        super(PrefabComponent, self).onDestroy()
        return

    def _activate(self):
        if self.__gameObject is None:
            if hasattr(self.entity, 'appearance'):
                self._loadInAppearance()
            else:
                self._loadInHierarchy()
        return

    def _loadInAppearance(self):
        appearance = self.entity.appearance
        if appearance and appearance.isConstructed:
            loadAppearancePrefab(self.prefab, appearance, self.__onGameObjectLoaded)

    def _loadInHierarchy(self):
        parent = self.entity.entityGameObject
        if parent:
            CGF.loadGameObjectIntoHierarchy(self.prefab, parent, self.matrix, self.__onGameObjectLoaded)

    def __onGameObjectLoaded(self, go):
        if self.__isDestroyed:
            CGF.removeGameObject(go)
            return
        self.__gameObject = go
        if not hasattr(self.entity, 'appearance'):
            go.createComponent(GenericComponents.RedirectorComponent, self.entity.entityGameObject)
