# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/markers.py
import Event

class Marker(object):
    """Base class which holds info for a Marker."""

    def __init__(self, markerID, active=True):
        super(Marker, self).__init__()
        self._markerID = markerID
        self._active = active

    def getMarkerID(self):
        return self._markerID

    def isActive(self):
        return self._active

    def setActive(self, active):
        """Sets marker is shown/hidden on the scene.
        :param active: bool.
        :return: True if property is changed, otherwise - False.
        """
        if self._active != active:
            self._active = active
            return True
        else:
            return False

    def destroy(self):
        pass


class VehicleMarker(Marker):
    """ The main purpose of this class is to correct handle situations when model, for which marker was
    attached, changes its model. When that happens we replace the old marker's matrix with a new one.
    """

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
        if self._vProxy is not None:
            return self._vProxy.isAlive()
        else:
            return 0
            return

    def getHealth(self):
        if self._vProxy is not None:
            return self._vProxy.health
        else:
            return 0
            return

    @classmethod
    def fetchMatrixProvider(cls, vProxy):
        return vProxy.model.node('HP_gui')

    def getMatrixProvider(self):
        if self._vProxy is not None:
            return self.fetchMatrixProvider(self._vProxy)
        else:
            return
            return

    def isSpeaking(self):
        return self._speaking

    def setSpeaking(self, speaking):
        if self._speaking != speaking:
            self._speaking = speaking
            return True
        else:
            return False

    def __onModelChanged(self):
        self.onVehicleModelChanged(self._markerID, self.getMatrixProvider())
