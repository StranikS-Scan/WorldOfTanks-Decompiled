# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/awards/reward_model.py
from enum import IntEnum
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class RentTypeEnum(IntEnum):
    NONE = 0
    DAYS = 1
    BATTLES = 2
    WINS = 3


class RewardModel(ItemBonusModel):
    __slots__ = ()

    def __init__(self, properties=22, commands=0):
        super(RewardModel, self).__init__(properties=properties, commands=commands)

    def getItem(self):
        return self._getString(10)

    def setItem(self, value):
        self._setString(10, value)

    def getIcon(self):
        return self._getString(11)

    def setIcon(self, value):
        self._setString(11, value)

    def getIconSmall(self):
        return self._getString(12)

    def setIconSmall(self, value):
        self._setString(12, value)

    def getIconBig(self):
        return self._getString(13)

    def setIconBig(self, value):
        self._setString(13, value)

    def getUserName(self):
        return self._getString(14)

    def setUserName(self, value):
        self._setString(14, value)

    def getVehicleType(self):
        return self._getString(15)

    def setVehicleType(self, value):
        self._setString(15, value)

    def getVehicleLevel(self):
        return self._getNumber(16)

    def setVehicleLevel(self, value):
        self._setNumber(16, value)

    def getVehicleRentType(self):
        return RentTypeEnum(self._getNumber(17))

    def setVehicleRentType(self, value):
        self._setNumber(17, value.value)

    def getVehicleRentValue(self):
        return self._getNumber(18)

    def setVehicleRentValue(self, value):
        self._setNumber(18, value)

    def getIsFromStorage(self):
        return self._getBool(19)

    def setIsFromStorage(self, value):
        self._setBool(19, value)

    def getIsVehicleOnChoice(self):
        return self._getBool(20)

    def setIsVehicleOnChoice(self, value):
        self._setBool(20, value)

    def getItemID(self):
        return self._getNumber(21)

    def setItemID(self, value):
        self._setNumber(21, value)

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
