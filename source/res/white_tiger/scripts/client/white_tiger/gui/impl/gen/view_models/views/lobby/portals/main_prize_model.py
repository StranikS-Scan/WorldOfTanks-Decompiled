# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/portals/main_prize_model.py
from frameworks.wulf import ViewModel

class MainPrizeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(MainPrizeModel, self).__init__(properties=properties, commands=commands)

    def getTankName(self):
        return self._getString(0)

    def setTankName(self, value):
        self._setString(0, value)

    def getTankLevel(self):
        return self._getNumber(1)

    def setTankLevel(self, value):
        self._setNumber(1, value)

    def getTankNation(self):
        return self._getString(2)

    def setTankNation(self, value):
        self._setString(2, value)

    def getTankType(self):
        return self._getString(3)

    def setTankType(self, value):
        self._setString(3, value)

    def getTankRoleName(self):
        return self._getString(4)

    def setTankRoleName(self, value):
        self._setString(4, value)

    def getDiscountPerToken(self):
        return self._getNumber(5)

    def setDiscountPerToken(self, value):
        self._setNumber(5, value)

    def getDiscountTokenCount(self):
        return self._getNumber(6)

    def setDiscountTokenCount(self, value):
        self._setNumber(6, value)

    def getMaxDiscountTokenCount(self):
        return self._getNumber(7)

    def setMaxDiscountTokenCount(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(MainPrizeModel, self)._initialize()
        self._addStringProperty('tankName', '')
        self._addNumberProperty('tankLevel', 0)
        self._addStringProperty('tankNation', '')
        self._addStringProperty('tankType', '')
        self._addStringProperty('tankRoleName', '')
        self._addNumberProperty('discountPerToken', 0)
        self._addNumberProperty('discountTokenCount', 0)
        self._addNumberProperty('maxDiscountTokenCount', 0)
