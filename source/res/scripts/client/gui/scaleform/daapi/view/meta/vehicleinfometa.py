# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleInfoMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class VehicleInfoMeta(AbstractWindowView):

    def getVehicleInfo(self):
        self._printOverrideError('getVehicleInfo')

    def onCancelClick(self):
        self._printOverrideError('onCancelClick')

    def as_setVehicleInfoS(self, vehicleInfo):
        if self._isDAAPIInited():
            return self.flashObject.as_setVehicleInfo(vehicleInfo)
