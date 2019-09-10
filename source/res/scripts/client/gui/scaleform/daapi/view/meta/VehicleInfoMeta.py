# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleInfoMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class VehicleInfoMeta(AbstractWindowView):

    def getVehicleInfo(self):
        self._printOverrideError('getVehicleInfo')

    def onCancelClick(self):
        self._printOverrideError('onCancelClick')

    def addToCompare(self):
        self._printOverrideError('addToCompare')

    def changeNation(self):
        self._printOverrideError('changeNation')

    def as_setVehicleInfoS(self, data):
        return self.flashObject.as_setVehicleInfo(data) if self._isDAAPIInited() else None

    def as_setCompareButtonDataS(self, data):
        return self.flashObject.as_setCompareButtonData(data) if self._isDAAPIInited() else None

    def as_setChangeNationButtonDataS(self, data):
        return self.flashObject.as_setChangeNationButtonData(data) if self._isDAAPIInited() else None
