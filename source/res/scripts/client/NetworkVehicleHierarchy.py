# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NetworkVehicleHierarchy.py
from BigWorld import DynamicScriptComponent
from vehicle_hierarchy import createClientVehicleHierarchy, removeClientVehicleHierarchy, updateClientVehicleHierarchy, onClientVehicleRespawn

class NetworkVehicleHierarchy(DynamicScriptComponent):

    def __init__(self):
        super(NetworkVehicleHierarchy, self).__init__()
        self.__create()

    def onEnterWorld(self, _):
        self.__create()

    def onLeaveWorld(self):
        gameObject = self.entity.entityGameObject
        if gameObject is None:
            return
        else:
            removeClientVehicleHierarchy(gameObject)
            return

    def setSlice_hierarchyInfo(self, changePath, prev):
        gameObject = self.entity.entityGameObject
        if gameObject is None:
            return
        else:
            begin, end = changePath[0]
            if begin == end:
                p = prev[0]
                updateClientVehicleHierarchy(gameObject, p['slotName'], p['networkID'])
            return

    def onRespawn(self):
        gameObject = self.entity.entityGameObject
        if gameObject is None:
            return
        else:
            onClientVehicleRespawn(gameObject)
            return

    def __create(self):
        ready = True
        typeDescriptor = self.entity.typeDescriptor
        if typeDescriptor is None:
            ready = False
        appearance = self.entity.appearance
        if appearance is None or not appearance.isConstructed or appearance.isDestroyed:
            ready = False
        gameObject = self.entity.entityGameObject
        if gameObject is None:
            return
        else:
            createClientVehicleHierarchy(gameObject, self.hierarchyInfo, ready)
            return
