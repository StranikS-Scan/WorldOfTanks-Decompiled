# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsSeasonAwardsWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class QuestsSeasonAwardsWindowMeta(AbstractWindowView):

    def showVehicleInfo(self, vehicleId):
        self._printOverrideError('showVehicleInfo')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
