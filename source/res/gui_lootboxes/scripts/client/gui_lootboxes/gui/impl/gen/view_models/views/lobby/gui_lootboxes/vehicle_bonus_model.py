# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/vehicle_bonus_model.py
from enum import Enum
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class VehicleType(Enum):
    HEAVY = 'heavyTank'
    MEDIUM = 'mediumTank'
    LIGHT = 'lightTank'
    SPG = 'SPG'
    ATSPG = 'AT-SPG'


class VehicleBonusModel(ItemBonusModel):
    __slots__ = ()

    def __init__(self, properties=17, commands=0):
        super(VehicleBonusModel, self).__init__(properties=properties, commands=commands)

    def getVehicleName(self):
        return self._getString(9)

    def setVehicleName(self, value):
        self._setString(9, value)

    def getType(self):
        return VehicleType(self._getString(10))

    def setType(self, value):
        self._setString(10, value.value)

    def getLevel(self):
        return self._getNumber(11)

    def setLevel(self, value):
        self._setNumber(11, value)

    def getNationTag(self):
        return self._getString(12)

    def setNationTag(self, value):
        self._setString(12, value)

    def getIsElite(self):
        return self._getBool(13)

    def setIsElite(self, value):
        self._setBool(13, value)

    def getIsRent(self):
        return self._getBool(14)

    def setIsRent(self, value):
        self._setBool(14, value)

    def getRentDays(self):
        return self._getNumber(15)

    def setRentDays(self, value):
        self._setNumber(15, value)

    def getRentBattles(self):
        return self._getNumber(16)

    def setRentBattles(self, value):
        self._setNumber(16, value)

    def _initialize(self):
        super(VehicleBonusModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('type')
        self._addNumberProperty('level', 0)
        self._addStringProperty('nationTag', '')
        self._addBoolProperty('isElite', False)
        self._addBoolProperty('isRent', False)
        self._addNumberProperty('rentDays', 0)
        self._addNumberProperty('rentBattles', 0)
