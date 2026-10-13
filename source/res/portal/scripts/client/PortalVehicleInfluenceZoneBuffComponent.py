# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/PortalVehicleInfluenceZoneBuffComponent.py
import CGF
import Math
from items import vehicles
from PortalVehicleInfluenceZoneBaseComponent import PortalVehicleInfluenceZoneBaseComponent

class PortalVehicleInfluenceZoneBuffComponent(PortalVehicleInfluenceZoneBaseComponent):

    def __init__(self):
        self.__prefab = None
        super(PortalVehicleInfluenceZoneBuffComponent, self).__init__()
        return

    def set_isActive(self, prev):
        if prev == self.isActive:
            return
        else:
            if self.isActive:
                self.__processActivation()
            elif self.__prefab is not None and self.__prefab.isValid():
                CGF.removeGameObject(self.__prefab)
                self.__prefab = None
            return

    def onAppearanceReady(self):
        if self.isActive:
            self.__processActivation()

    def __onPrefabLoaded(self, prefab):
        if not self.isActive:
            CGF.removeGameObject(prefab)
            return
        self.__prefab = prefab

    def __processActivation(self):
        equipment = vehicles.g_cache.equipments()[self.equipmentID]
        usagePrefab = equipment.params['usagePrefab']
        CGF.loadGameObjectIntoHierarchy(usagePrefab, self.entity.entityGameObject, Math.Vector3(), self.__onPrefabLoaded)
