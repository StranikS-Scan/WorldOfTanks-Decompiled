# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RoleChangeMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class RoleChangeMeta(AbstractWindowView):

    def onVehicleSelected(self, vehicleId):
        self._printOverrideError('onVehicleSelected')

    def changeRole(self, role, vehicleId):
        self._printOverrideError('changeRole')

    def as_setCommonDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setCommonData(data)

    def as_setRolesS(self, roles):
        if self._isDAAPIInited():
            return self.flashObject.as_setRoles(roles)

    def as_setPriceS(self, priceString, enoughGold):
        if self._isDAAPIInited():
            return self.flashObject.as_setPrice(priceString, enoughGold)
