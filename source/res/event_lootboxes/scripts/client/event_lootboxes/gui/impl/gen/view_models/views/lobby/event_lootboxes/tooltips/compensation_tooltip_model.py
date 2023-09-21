# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_lootboxes/scripts/client/event_lootboxes/gui/impl/gen/view_models/views/lobby/event_lootboxes/tooltips/compensation_tooltip_model.py
from enum import Enum
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class VehicleType(Enum):
    HEAVY = 'heavyTank'
    MEDIUM = 'mediumTank'
    LIGHT = 'lightTank'
    SPG = 'SPG'
    ATSPG = 'AT-SPG'


class CompensationTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(CompensationTooltipModel, self).__init__(properties=properties, commands=commands)

    def getIconBefore(self):
        return self._getResource(0)

    def setIconBefore(self, value):
        self._setResource(0, value)

    def getVehicleLevel(self):
        return self._getNumber(1)

    def setVehicleLevel(self, value):
        self._setNumber(1, value)

    def getVehicleType(self):
        return VehicleType(self._getString(2))

    def setVehicleType(self, value):
        self._setString(2, value.value)

    def getVehicleName(self):
        return self._getString(3)

    def setVehicleName(self, value):
        self._setString(3, value)

    def getCompensationCurrency(self):
        return self._getString(4)

    def setCompensationCurrency(self, value):
        self._setString(4, value)

    def getCompensationValue(self):
        return self._getNumber(5)

    def setCompensationValue(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(CompensationTooltipModel, self)._initialize()
        self._addResourceProperty('iconBefore', R.invalid())
        self._addNumberProperty('vehicleLevel', 0)
        self._addStringProperty('vehicleType')
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('compensationCurrency', '')
        self._addNumberProperty('compensationValue', 0)
