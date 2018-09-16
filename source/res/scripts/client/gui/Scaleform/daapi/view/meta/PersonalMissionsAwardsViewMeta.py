# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PersonalMissionsAwardsViewMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.View import View

class PersonalMissionsAwardsViewMeta(View):

    def showVehiclePreview(self):
        self._printOverrideError('showVehiclePreview')

    def changeOperation(self, operationID):
        self._printOverrideError('changeOperation')

    def closeView(self):
        self._printOverrideError('closeView')

    def showMissionByVehicleType(self, vehicleType):
        self._printOverrideError('showMissionByVehicleType')

    def buyMissionsByVehicleType(self, vehicleType):
        self._printOverrideError('buyMissionsByVehicleType')

    def as_setDataS(self, data):
        """
        :param data: Represented by PersonalMissionsAwardsViewVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setHeaderDataS(self, data):
        """
        :param data: Represented by OperationsHeaderVO (AS)
        """
        return self.flashObject.as_setHeaderData(data) if self._isDAAPIInited() else None
