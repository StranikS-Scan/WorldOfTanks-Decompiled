# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NetworkVehicleHierarchy.py
from __future__ import absolute_import
from vehicle_hierarchy import createClientVehicleHierarchy, removeClientVehicleHierarchy
from vehicles.components.vehicle_component import VehicleDynamicComponent

class NetworkVehicleHierarchy(VehicleDynamicComponent):

    def __init__(self):
        super(NetworkVehicleHierarchy, self).__init__()
        self._initComponent()

    def onDestroy(self):
        gameObject = self.entity.entityGameObject
        if gameObject is not None:
            removeClientVehicleHierarchy(gameObject)
        super(NetworkVehicleHierarchy, self).onDestroy()
        return

    def _onAppearanceReady(self):
        super(NetworkVehicleHierarchy, self)._onAppearanceReady()
        self.__create()

    def __create(self):
        gameObject = self.entity.entityGameObject
        if gameObject is None:
            return
        else:
            createClientVehicleHierarchy(gameObject, self.hierarchyInfo, True)
            return
