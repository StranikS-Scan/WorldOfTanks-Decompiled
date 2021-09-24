# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PrefabComponent.py
import CGF
import GenericComponents
from script_component.DynamicScriptComponent import DynamicScriptComponent

class PrefabComponent(DynamicScriptComponent):

    def __init__(self):
        self.__gameObject = None
        super(PrefabComponent, self).__init__()
        return

    def onAvatarReady(self):
        parent = self.entity.entityGameObject
        if parent is not None:
            CGF.loadGameObjectIntoHierarchy(self.prefab, parent, self.matrix, self.__onGameObjectLoaded)
        return

    def onAppearanceReady(self):
        if self.__gameObject is not None:
            appearance = self.entity.appearance
            self.__gameObject.removeComponentByType(GenericComponents.DynamicModelComponent)
            self.__gameObject.createComponent(GenericComponents.DynamicModelComponent, appearance.compoundModel)
        return

    def onDestroy(self):
        if self.__gameObject is not None:
            CGF.removeGameObject(self.__gameObject)
        self.__gameObject = None
        super(PrefabComponent, self).onDestroy()
        return

    def __onGameObjectLoaded(self, gameObject):
        self.__gameObject = gameObject
        if hasattr(self.entity, 'appearance') and self.entity.appearance is not None:
            appearance = self.entity.appearance
            gameObject.createComponent(GenericComponents.RedirectorComponent, appearance.gameObject)
            gameObject.createComponent(GenericComponents.DynamicModelComponent, appearance.compoundModel)
        else:
            gameObject.createComponent(GenericComponents.RedirectorComponent, self.entity.entityGameObject)
        return
