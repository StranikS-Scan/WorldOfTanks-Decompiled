# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/markers.py
import Event
import GUI
from vehicle_systems.tankStructure import TankNodeNames
from gun_rotation_shared import getLocalAimPoint

class Marker(object):

    def __init__(self, markerID, active=True):
        super(Marker, self).__init__()
        self._markerID = markerID
        self._active = active

    def getMarkerID(self):
        return self._markerID

    def isActive(self):
        return self._active

    def setActive(self, active):
        if self._active != active:
            self._active = active
            return True
        return False

    def destroy(self):
        pass


class VehicleMarker(Marker):

    def __init__(self, markerID, vehicleID, vProxy=None, active=True):
        super(VehicleMarker, self).__init__(markerID, active)
        self._vehicleID = vehicleID
        self._vProxy = vProxy
        self._speaking = False
        if self._vProxy is not None:
            self.attach(vProxy)
        self.onVehicleModelChanged = Event.Event()
        return

    def attach(self, vProxy):
        self.detach()
        self._vProxy = vProxy
        self._vProxy.appearance.onModelChanged += self.__onModelChanged

    def detach(self):
        if self._vProxy is not None:
            self._vProxy.appearance.onModelChanged -= self.__onModelChanged
            self._vProxy = None
        return

    def destroy(self):
        self.detach()
        self.onVehicleModelChanged.clear()

    def getVehicleID(self):
        return self._vehicleID

    def isAlive(self):
        return self._vProxy.isAlive() if self._vProxy is not None else 0

    def getHealth(self):
        return self._vProxy.health if self._vProxy is not None else 0

    @classmethod
    def fetchMatrixProvider(cls, vProxy):
        rootMP = vProxy.model.node(TankNodeNames.HULL_SWINGING)
        guiMP = vProxy.model.node(TankNodeNames.GUI)
        rootM = rootMP.localMatrix
        guiM = guiMP.localMatrix
        offset = guiM.translation - rootM.translation
        return GUI.WGVehicleMarkersMatrixProvider(rootMP, offset)

    def getMatrixProvider(self):
        return self.fetchMatrixProvider(self._vProxy) if self._vProxy is not None else None

    def isSpeaking(self):
        return self._speaking

    def setSpeaking(self, speaking):
        if self._speaking != speaking:
            self._speaking = speaking
            return True
        return False

    def __onModelChanged(self):
        self.onVehicleModelChanged(self._markerID, self.getMatrixProvider())


class VehicleTargetMarker(VehicleMarker):

    @classmethod
    def fetchMatrixProvider(cls, vProxy):
        pointOffset = getLocalAimPoint(vProxy.typeDescriptor)
        return GUI.WGVehicleMarkersMatrixProvider(vProxy.matrix, pointOffset)
