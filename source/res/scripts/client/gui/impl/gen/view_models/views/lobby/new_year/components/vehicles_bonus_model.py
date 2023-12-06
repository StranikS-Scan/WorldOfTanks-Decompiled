# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/vehicles_bonus_model.py
from enum import Enum
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class VehicleType(Enum):
    HEAVY = 'heavyTank'
    MEDIUM = 'mediumTank'
    LIGHT = 'lightTank'
    SPG = 'SPG'
    ATSPG = 'AT-SPG'


class VehiclesBonusModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(VehiclesBonusModel, self).__init__(properties=properties, commands=commands)

    def getVehicleName(self):
        return self._getString(7)

    def setVehicleName(self, value):
        self._setString(7, value)

    def getType(self):
        return VehicleType(self._getString(8))

    def setType(self, value):
        self._setString(8, value.value)

    def getLevel(self):
        return self._getNumber(9)

    def setLevel(self, value):
        self._setNumber(9, value)

    def getNationTag(self):
        return self._getString(10)

    def setNationTag(self, value):
        self._setString(10, value)

    def _initialize(self):
        super(VehiclesBonusModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('type')
        self._addNumberProperty('level', 0)
        self._addStringProperty('nationTag', '')
