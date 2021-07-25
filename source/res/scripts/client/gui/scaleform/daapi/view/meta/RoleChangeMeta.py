# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RoleChangeMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class RoleChangeMeta(AbstractWindowView):

    def submit(self):
        self._printOverrideError('submit')

    def changeRetrainType(self, retrainTypeIndex):
        self._printOverrideError('changeRetrainType')

    def as_setCommonDataS(self, data):
        return self.flashObject.as_setCommonData(data) if self._isDAAPIInited() else None

    def as_setRoleS(self, role, infoText):
        return self.flashObject.as_setRole(role, infoText) if self._isDAAPIInited() else None

    def as_setPriceS(self, priceString, actionChangeRole, enableSubmitButton, tooltip):
        return self.flashObject.as_setPrice(priceString, actionChangeRole, enableSubmitButton, tooltip) if self._isDAAPIInited() else None

    def as_setVehicleDataS(self, data):
        return self.flashObject.as_setVehicleData(data) if self._isDAAPIInited() else None

    def as_setCrewOperationDataS(self, data):
        return self.flashObject.as_setCrewOperationData(data) if self._isDAAPIInited() else None
