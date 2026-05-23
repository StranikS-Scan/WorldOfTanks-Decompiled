# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/summer_sale/vehicle_bonus_model.py
from enum import Enum
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel
from gui.impl.gen.view_models.views.lobby.summer_sale.price_model import PriceModel

class VehicleType(Enum):
    HEAVY = 'heavyTank'
    MEDIUM = 'mediumTank'
    LIGHT = 'lightTank'
    SPG = 'SPG'
    ATSPG = 'AT-SPG'


class VehicleBonusModel(ItemBonusModel):
    __slots__ = ()

    def __init__(self, properties=24, commands=0):
        super(VehicleBonusModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(9)

    @staticmethod
    def getPriceType():
        return PriceModel

    def getVehicleName(self):
        return self._getString(10)

    def setVehicleName(self, value):
        self._setString(10, value)

    def getTechName(self):
        return self._getString(11)

    def setTechName(self, value):
        self._setString(11, value)

    def getType(self):
        return VehicleType(self._getString(12))

    def setType(self, value):
        self._setString(12, value.value)

    def getLevel(self):
        return self._getNumber(13)

    def setLevel(self, value):
        self._setNumber(13, value)

    def getShortVehicleLabel(self):
        return self._getString(14)

    def setShortVehicleLabel(self, value):
        self._setString(14, value)

    def getNationTag(self):
        return self._getString(15)

    def setNationTag(self, value):
        self._setString(15, value)

    def getIsElite(self):
        return self._getBool(16)

    def setIsElite(self, value):
        self._setBool(16, value)

    def getIsRent(self):
        return self._getBool(17)

    def setIsRent(self, value):
        self._setBool(17, value)

    def getRentDays(self):
        return self._getNumber(18)

    def setRentDays(self, value):
        self._setNumber(18, value)

    def getRentBattles(self):
        return self._getNumber(19)

    def setRentBattles(self, value):
        self._setNumber(19, value)

    def getIntCD(self):
        return self._getNumber(20)

    def setIntCD(self, value):
        self._setNumber(20, value)

    def getInInventory(self):
        return self._getBool(21)

    def setInInventory(self, value):
        self._setBool(21, value)

    def getWasSold(self):
        return self._getBool(22)

    def setWasSold(self, value):
        self._setBool(22, value)

    def getProductCode(self):
        return self._getString(23)

    def setProductCode(self, value):
        self._setString(23, value)

    def _initialize(self):
        super(VehicleBonusModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('techName', '')
        self._addStringProperty('type')
        self._addNumberProperty('level', 0)
        self._addStringProperty('shortVehicleLabel', '')
        self._addStringProperty('nationTag', '')
        self._addBoolProperty('isElite', False)
        self._addBoolProperty('isRent', False)
        self._addNumberProperty('rentDays', 0)
        self._addNumberProperty('rentBattles', 0)
        self._addNumberProperty('intCD', 0)
        self._addBoolProperty('inInventory', False)
        self._addBoolProperty('wasSold', False)
        self._addStringProperty('productCode', '')
