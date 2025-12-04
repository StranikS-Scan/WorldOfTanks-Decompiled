# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_shop_item.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class TemplateType(Enum):
    VEHICLE = 'vehicle'
    BUNDLE = 'bundle'
    OTHER = 'other'
    MAINTAIN = 'maintain'
    CUSTOMIZATION = 'customization'
    ECONOMICBOOSTER = 'economicBooster'


class ArmoryYardShopItem(ViewModel):
    __slots__ = ()

    def __init__(self, properties=21, commands=0):
        super(ArmoryYardShopItem, self).__init__(properties=properties, commands=commands)

    def getItemID(self):
        return self._getNumber(0)

    def setItemID(self, value):
        self._setNumber(0, value)

    def getItemType(self):
        return self._getString(1)

    def setItemType(self, value):
        self._setString(1, value)

    def getImage(self):
        return self._getString(2)

    def setImage(self, value):
        self._setString(2, value)

    def getLargeImage(self):
        return self._getString(3)

    def setLargeImage(self, value):
        self._setString(3, value)

    def getNationFlagIcon(self):
        return self._getString(4)

    def setNationFlagIcon(self, value):
        self._setString(4, value)

    def getTitle(self):
        return self._getString(5)

    def setTitle(self, value):
        self._setString(5, value)

    def getSpecializations(self):
        return self._getArray(6)

    def setSpecializations(self, value):
        self._setArray(6, value)

    @staticmethod
    def getSpecializationsType():
        return unicode

    def getCount(self):
        return self._getNumber(7)

    def setCount(self, value):
        self._setNumber(7, value)

    def getLimit(self):
        return self._getNumber(8)

    def setLimit(self, value):
        self._setNumber(8, value)

    def getAvailable(self):
        return self._getBool(9)

    def setAvailable(self, value):
        self._setBool(9, value)

    def getExtraParams(self):
        return self._getArray(10)

    def setExtraParams(self, value):
        self._setArray(10, value)

    @staticmethod
    def getExtraParamsType():
        return unicode

    def getDescription(self):
        return self._getString(11)

    def setDescription(self, value):
        self._setString(11, value)

    def getLongDescription(self):
        return self._getString(12)

    def setLongDescription(self, value):
        self._setString(12, value)

    def getAdditionalInfo(self):
        return self._getString(13)

    def setAdditionalInfo(self, value):
        self._setString(13, value)

    def getIsOnlyArmoryCoins(self):
        return self._getBool(14)

    def setIsOnlyArmoryCoins(self, value):
        self._setBool(14, value)

    def getVehicleType(self):
        return self._getString(15)

    def setVehicleType(self, value):
        self._setString(15, value)

    def getVehicleLevel(self):
        return self._getString(16)

    def setVehicleLevel(self, value):
        self._setString(16, value)

    def getVehicleRoleName(self):
        return self._getString(17)

    def setVehicleRoleName(self, value):
        self._setString(17, value)

    def getCoinsCost(self):
        return self._getNumber(18)

    def setCoinsCost(self, value):
        self._setNumber(18, value)

    def getTemplate(self):
        return TemplateType(self._getString(19))

    def setTemplate(self, value):
        self._setString(19, value.value)

    def getEffect(self):
        return self._getString(20)

    def setEffect(self, value):
        self._setString(20, value)

    def _initialize(self):
        super(ArmoryYardShopItem, self)._initialize()
        self._addNumberProperty('itemID', 0)
        self._addStringProperty('itemType', '')
        self._addStringProperty('image', '')
        self._addStringProperty('largeImage', '')
        self._addStringProperty('nationFlagIcon', '')
        self._addStringProperty('title', '')
        self._addArrayProperty('specializations', Array())
        self._addNumberProperty('count', 0)
        self._addNumberProperty('limit', 0)
        self._addBoolProperty('available', False)
        self._addArrayProperty('extraParams', Array())
        self._addStringProperty('description', '')
        self._addStringProperty('longDescription', '')
        self._addStringProperty('additionalInfo', '')
        self._addBoolProperty('isOnlyArmoryCoins', False)
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('vehicleLevel', '')
        self._addStringProperty('vehicleRoleName', '')
        self._addNumberProperty('coinsCost', 0)
        self._addStringProperty('template')
        self._addStringProperty('effect', '')
