# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/research_item_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.vehicle_mechanic_model import VehicleMechanicModel

class ResearchItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=24, commands=0):
        super(ResearchItemModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getImage(self):
        return self._getString(1)

    def setImage(self, value):
        self._setString(1, value)

    def getUserName(self):
        return self._getString(2)

    def setUserName(self, value):
        self._setString(2, value)

    def getState(self):
        return self._getNumber(3)

    def setState(self, value):
        self._setNumber(3, value)

    def getRenderer(self):
        return self._getString(4)

    def setRenderer(self, value):
        self._setString(4, value)

    def getIsInstalled(self):
        return self._getBool(5)

    def setIsInstalled(self, value):
        self._setBool(5, value)

    def getIsDisabled(self):
        return self._getBool(6)

    def setIsDisabled(self, value):
        self._setBool(6, value)

    def getLevel(self):
        return self._getNumber(7)

    def setLevel(self, value):
        self._setNumber(7, value)

    def getRequiredXp(self):
        return self._getNumber(8)

    def setRequiredXp(self, value):
        self._setNumber(8, value)

    def getIsDiscountedXp(self):
        return self._getBool(9)

    def setIsDiscountedXp(self, value):
        self._setBool(9, value)

    def getEarnedXp(self):
        return self._getNumber(10)

    def setEarnedXp(self, value):
        self._setNumber(10, value)

    def getPriceAmount(self):
        return self._getNumber(11)

    def setPriceAmount(self, value):
        self._setNumber(11, value)

    def getPriceCurrency(self):
        return self._getString(12)

    def setPriceCurrency(self, value):
        self._setString(12, value)

    def getIsDiscountedPrice(self):
        return self._getBool(13)

    def setIsDiscountedPrice(self, value):
        self._setBool(13, value)

    def getPrimaryClass(self):
        return self._getString(14)

    def setPrimaryClass(self, value):
        self._setString(14, value)

    def getIsResearched(self):
        return self._getBool(15)

    def setIsResearched(self, value):
        self._setBool(15, value)

    def getHasEnoughCurrency(self):
        return self._getBool(16)

    def setHasEnoughCurrency(self, value):
        self._setBool(16, value)

    def getHasEnoughXP(self):
        return self._getBool(17)

    def setHasEnoughXP(self, value):
        self._setBool(17, value)

    def getIsElite(self):
        return self._getBool(18)

    def setIsElite(self, value):
        self._setBool(18, value)

    def getAutoUnlocked(self):
        return self._getBool(19)

    def setAutoUnlocked(self, value):
        self._setBool(19, value)

    def getIsInInventory(self):
        return self._getBool(20)

    def setIsInInventory(self, value):
        self._setBool(20, value)

    def getUrgentIds(self):
        return self._getArray(21)

    def setUrgentIds(self, value):
        self._setArray(21, value)

    @staticmethod
    def getUrgentIdsType():
        return int

    def getPath(self):
        return self._getArray(22)

    def setPath(self, value):
        self._setArray(22, value)

    @staticmethod
    def getPathType():
        return int

    def getMechanics(self):
        return self._getArray(23)

    def setMechanics(self, value):
        self._setArray(23, value)

    @staticmethod
    def getMechanicsType():
        return VehicleMechanicModel

    def _initialize(self):
        super(ResearchItemModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('image', '')
        self._addStringProperty('userName', '')
        self._addNumberProperty('state', 0)
        self._addStringProperty('renderer', '')
        self._addBoolProperty('isInstalled', False)
        self._addBoolProperty('isDisabled', False)
        self._addNumberProperty('level', 1)
        self._addNumberProperty('requiredXp', 0)
        self._addBoolProperty('isDiscountedXp', False)
        self._addNumberProperty('earnedXp', 0)
        self._addNumberProperty('priceAmount', 0)
        self._addStringProperty('priceCurrency', '')
        self._addBoolProperty('isDiscountedPrice', False)
        self._addStringProperty('primaryClass', '')
        self._addBoolProperty('isResearched', False)
        self._addBoolProperty('hasEnoughCurrency', False)
        self._addBoolProperty('hasEnoughXP', False)
        self._addBoolProperty('isElite', False)
        self._addBoolProperty('autoUnlocked', False)
        self._addBoolProperty('isInInventory', False)
        self._addArrayProperty('urgentIds', Array())
        self._addArrayProperty('path', Array())
        self._addArrayProperty('mechanics', Array())
