# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/awards/reward_model.py
from enum import IntEnum
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class RentTypeEnum(IntEnum):
    NONE = 0
    DAYS = 1
    BATTLES = 2
    WINS = 3


class RewardModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=0):
        super(RewardModel, self).__init__(properties=properties, commands=commands)

    def getItem(self):
        return self._getString(7)

    def setItem(self, value):
        self._setString(7, value)

    def getIcon(self):
        return self._getString(8)

    def setIcon(self, value):
        self._setString(8, value)

    def getIconSmall(self):
        return self._getString(9)

    def setIconSmall(self, value):
        self._setString(9, value)

    def getIconBig(self):
        return self._getString(10)

    def setIconBig(self, value):
        self._setString(10, value)

    def getUserName(self):
        return self._getString(11)

    def setUserName(self, value):
        self._setString(11, value)

    def getVehicleType(self):
        return self._getString(12)

    def setVehicleType(self, value):
        self._setString(12, value)

    def getVehicleLevel(self):
        return self._getNumber(13)

    def setVehicleLevel(self, value):
        self._setNumber(13, value)

    def getVehicleRentType(self):
        return RentTypeEnum(self._getNumber(14))

    def setVehicleRentType(self, value):
        self._setNumber(14, value.value)

    def getVehicleRentValue(self):
        return self._getNumber(15)

    def setVehicleRentValue(self, value):
        self._setNumber(15, value)

    def getIsFromStorage(self):
        return self._getBool(16)

    def setIsFromStorage(self, value):
        self._setBool(16, value)

    def getIsVehicleOnChoice(self):
        return self._getBool(17)

    def setIsVehicleOnChoice(self, value):
        self._setBool(17, value)

    def getItemID(self):
        return self._getNumber(18)

    def setItemID(self, value):
        self._setNumber(18, value)

    def _initialize(self):
        super(RewardModel, self)._initialize()
        self._addStringProperty('item', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('iconSmall', '')
        self._addStringProperty('iconBig', '')
        self._addStringProperty('userName', '')
        self._addStringProperty('vehicleType', '')
        self._addNumberProperty('vehicleLevel', 0)
        self._addNumberProperty('vehicleRentType')
        self._addNumberProperty('vehicleRentValue', 0)
        self._addBoolProperty('isFromStorage', False)
        self._addBoolProperty('isVehicleOnChoice', False)
        self._addNumberProperty('itemID', 0)
