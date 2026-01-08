# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DynObstacleComponent.py
import CGF
import GenericComponents
import Physics
from script_component.DynamicScriptComponent import DynamicScriptComponent

class DynObstacleComponent(DynamicScriptComponent):

    def __init__(self):
        super(DynObstacleComponent, self).__init__()
        self._gameObject = None
        return

    def _onAvatarReady(self):
        if self.isHidden:
            return
        parentGO = self.entity.entityGameObject
        self._gameObject = gameObject = CGF.GameObject(self.spaceID)
        gameObject.createComponent(GenericComponents.HierarchyComponent, parentGO)
        gameObject.createComponent(GenericComponents.TransformComponent, self.localMatrix)
        gameObject.createComponent(Physics.CollidersComponent, [Physics.MeshColliderDesc(self.modelPath, '')])
        model = gameObject.createComponent(GenericComponents.DynamicModelComponent, self.modelPath)
        model.setOverlayEnabled(self.applyOverlay)

    def onDestroy(self):
        if self._gameObject is not None:
            CGF.removeGameObject(self._gameObject)
            self._gameObject = None
        super(DynObstacleComponent, self).onDestroy()
        return
