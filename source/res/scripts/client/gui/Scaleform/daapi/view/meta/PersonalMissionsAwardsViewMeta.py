# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PersonalMissionsAwardsViewMeta.py
from gui.Scaleform.framework.entities.View import View

class PersonalMissionsAwardsViewMeta(View):

    def showVehiclePreview(self):
        self._printOverrideError('showVehiclePreview')

    def closeView(self):
        self._printOverrideError('closeView')

    def showMissionByVehicleType(self, vehicleType):
        self._printOverrideError('showMissionByVehicleType')

    def buyMissionsByVehicleType(self, vehicleType):
        self._printOverrideError('buyMissionsByVehicleType')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setHeaderDataS(self, data):
        return self.flashObject.as_setHeaderData(data) if self._isDAAPIInited() else None
