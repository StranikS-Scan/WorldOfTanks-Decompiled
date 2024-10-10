# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/main_vehicle_prize.py
from frameworks.wulf import ViewModel

class MainVehiclePrize(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(MainVehiclePrize, self).__init__(properties=properties, commands=commands)

    def getPrice(self):
        return self._getNumber(0)

    def setPrice(self, value):
        self._setNumber(0, value)

    def getActualPrice(self):
        return self._getNumber(1)

    def setActualPrice(self, value):
        self._setNumber(1, value)

    def getDiscountTokenCount(self):
        return self._getNumber(2)

    def setDiscountTokenCount(self, value):
        self._setNumber(2, value)

    def getMaxDiscountTokenCount(self):
        return self._getNumber(3)

    def setMaxDiscountTokenCount(self, value):
        self._setNumber(3, value)

    def getTankName(self):
        return self._getString(4)

    def setTankName(self, value):
        self._setString(4, value)

    def getTankLevel(self):
        return self._getNumber(5)

    def setTankLevel(self, value):
        self._setNumber(5, value)

    def getTankNation(self):
        return self._getString(6)

    def setTankNation(self, value):
        self._setString(6, value)

    def getIsTankPremium(self):
        return self._getBool(7)

    def setIsTankPremium(self, value):
        self._setBool(7, value)

    def getTankType(self):
        return self._getString(8)

    def setTankType(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(MainVehiclePrize, self)._initialize()
        self._addNumberProperty('price', 0)
        self._addNumberProperty('actualPrice', 0)
        self._addNumberProperty('discountTokenCount', 0)
        self._addNumberProperty('maxDiscountTokenCount', 0)
        self._addStringProperty('tankName', '')
        self._addNumberProperty('tankLevel', 0)
        self._addStringProperty('tankNation', '')
        self._addBoolProperty('isTankPremium', False)
        self._addStringProperty('tankType', '')
