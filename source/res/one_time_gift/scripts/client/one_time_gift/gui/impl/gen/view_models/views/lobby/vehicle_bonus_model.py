# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/gen/view_models/views/lobby/vehicle_bonus_model.py
from enum import IntEnum
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class RentTypeEnum(IntEnum):
    NONE = 0
    DAYS = 1
    BATTLES = 2
    WINS = 3


class VehicleBonusModel(RewardItemModel):
    __slots__ = ()

    def __init__(self, properties=25, commands=0):
        super(VehicleBonusModel, self).__init__(properties=properties, commands=commands)

    def getIsElite(self):
        return self._getBool(17)

    def setIsElite(self, value):
        self._setBool(17, value)

    def getVehicleName(self):
        return self._getString(18)

    def setVehicleName(self, value):
        self._setString(18, value)

    def getVehicleType(self):
        return self._getString(19)

    def setVehicleType(self, value):
        self._setString(19, value)

    def getVehicleLvl(self):
        return self._getNumber(20)

    def setVehicleLvl(self, value):
        self._setNumber(20, value)

    def getTechName(self):
        return self._getString(21)

    def setTechName(self, value):
        self._setString(21, value)

    def getNation(self):
        return self._getString(22)

    def setNation(self, value):
        self._setString(22, value)

    def getVehicleRentType(self):
        return RentTypeEnum(self._getNumber(23))

    def setVehicleRentType(self, value):
        self._setNumber(23, value.value)

    def getVehicleRentValue(self):
        return self._getNumber(24)

    def setVehicleRentValue(self, value):
        self._setNumber(24, value)

    def _initialize(self):
        super(VehicleBonusModel, self)._initialize()
        self._addBoolProperty('isElite', False)
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleType', '')
        self._addNumberProperty('vehicleLvl', 0)
        self._addStringProperty('techName', '')
        self._addStringProperty('nation', '')
        self._addNumberProperty('vehicleRentType')
        self._addNumberProperty('vehicleRentValue', 0)
