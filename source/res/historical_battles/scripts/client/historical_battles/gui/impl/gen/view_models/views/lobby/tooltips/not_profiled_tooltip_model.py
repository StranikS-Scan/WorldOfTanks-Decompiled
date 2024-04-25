# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/tooltips/not_profiled_tooltip_model.py
from frameworks.wulf import ViewModel

class NotProfiledTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(NotProfiledTooltipModel, self).__init__(properties=properties, commands=commands)

    def getRoleName(self):
        return self._getString(0)

    def setRoleName(self, value):
        self._setString(0, value)

    def getRoleAbilityName(self):
        return self._getString(1)

    def setRoleAbilityName(self, value):
        self._setString(1, value)

    def getFrontmanID(self):
        return self._getNumber(2)

    def setFrontmanID(self, value):
        self._setNumber(2, value)

    def getVehicleName(self):
        return self._getString(3)

    def setVehicleName(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(NotProfiledTooltipModel, self)._initialize()
        self._addStringProperty('roleName', '')
        self._addStringProperty('roleAbilityName', '')
        self._addNumberProperty('frontmanID', 0)
        self._addStringProperty('vehicleName', '')
