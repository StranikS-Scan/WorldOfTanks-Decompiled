# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/markers2d/markers.py
import GUI
from gui.Scaleform.daapi.view.battle.shared.markers2d.markers import Marker, VehicleMarker
from vehicle_systems.tankStructure import TankNodeNames
from RTSShared import RTSSupply

class SupplyMarker(VehicleMarker):

    def __init__(self, markerID, supplyID, supplyTag, vProxy=None, active=True, isPlayerTeam=False):
        super(SupplyMarker, self).__init__(markerID=markerID, vehicleID=supplyID, vProxy=vProxy, active=active, isPlayerTeam=isPlayerTeam)
        self._supplyTag = supplyTag
        self._supplyType = RTSSupply.TAG_TO_SUPPLY[supplyTag]
        self._state = 'default'

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def getSupplyTag(self):
        return self._supplyTag

    def getSupplyType(self):
        return self._supplyType

    def getMatrixProvider(self):
        matrixProvider = None
        if self._vProxy is not None:
            if self._state == 'dead' and self._supplyType == RTSSupply.WATCH_TOWER:
                matrixProvider = self.fetchDeadMatrixProvider(self._vProxy)
            else:
                matrixProvider = self.fetchMatrixProvider(self._vProxy)
        return matrixProvider

    def fetchDeadMatrixProvider(self, vProxy):
        rootMP = vProxy.model.node(TankNodeNames.HULL_SWINGING)
        guiMP = vProxy.model.node(TankNodeNames.GUI)
        rootM = rootMP.localMatrix
        guiM = guiMP.localMatrix
        offset = guiM.translation - rootM.translation
        rootCalculator = vProxy.model.getWorldMatrixCalculator(TankNodeNames.HULL_SWINGING)
        return GUI.WGVehicleMarkersMatrixProvider(rootCalculator, offset)


class OrderMarker(Marker):

    def __init__(self, markerID, vID, orderType):
        super(OrderMarker, self).__init__(markerID)
        self.__markerID = markerID
        self.__vID = vID
        self.__orderType = orderType

    def getMarkerID(self):
        return self.__markerID

    def getOrderType(self):
        return self.__orderType

    def getVehicleID(self):
        return self.__vID
