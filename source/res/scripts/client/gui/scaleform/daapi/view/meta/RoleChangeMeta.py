# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RoleChangeMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class RoleChangeMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def onVehicleSelected(self, vehicleId):
        """
        :param vehicleId:
        :return :
        """
        self._printOverrideError('onVehicleSelected')

    def changeRole(self, role, vehicleId):
        """
        :param role:
        :param vehicleId:
        :return :
        """
        self._printOverrideError('changeRole')

    def as_setCommonDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setCommonData(data) if self._isDAAPIInited() else None

    def as_setRolesS(self, roles):
        """
        :param roles:
        :return :
        """
        return self.flashObject.as_setRoles(roles) if self._isDAAPIInited() else None

    def as_setPriceS(self, priceString, enoughGold):
        """
        :param priceString:
        :param enoughGold:
        :return :
        """
        return self.flashObject.as_setPrice(priceString, enoughGold) if self._isDAAPIInited() else None
