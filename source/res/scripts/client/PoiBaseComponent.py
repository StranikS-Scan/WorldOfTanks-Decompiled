# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PoiBaseComponent.py
import CGF
import GenericComponents
from script_component.DynamicScriptComponent import DynamicScriptComponent

class PoiBaseComponent(DynamicScriptComponent):
    _POI_GO_NAME = 'PointOfInterest{id}'

    def __init__(self):
        super(PoiBaseComponent, self).__init__()
        self._poiGameObject = self.__getPoiGameObject()

    def onLeaveWorld(self):
        self._poiGameObject = None
        return

    def __getPoiGameObject(self):
        name = self._POI_GO_NAME.format(id=self.pointID)
        parent = self.entity.entityGameObject
        poiGameObject = CGF.HierarchyManager(self.spaceID).findFirstNode(parent, name)
        if not poiGameObject.isValid():
            poiGameObject = CGF.GameObject(self.spaceID, name)
            poiGameObject.createComponent(GenericComponents.HierarchyComponent, parent)
            poiGameObject.activate()
        return poiGameObject
