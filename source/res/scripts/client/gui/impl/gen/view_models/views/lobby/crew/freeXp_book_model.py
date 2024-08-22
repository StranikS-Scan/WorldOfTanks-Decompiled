# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/freeXp_book_model.py
from frameworks.wulf import ViewModel

class FreeXpBookModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(FreeXpBookModel, self).__init__(properties=properties, commands=commands)

    def getPlayerXp(self):
        return self._getNumber(0)

    def setPlayerXp(self, value):
        self._setNumber(0, value)

    def getDiscountSize(self):
        return self._getNumber(1)

    def setDiscountSize(self, value):
        self._setNumber(1, value)

    def getCurrentXpValue(self):
        return self._getNumber(2)

    def setCurrentXpValue(self, value):
        self._setNumber(2, value)

    def getCurrentMaxValue(self):
        return self._getNumber(3)

    def setCurrentMaxValue(self, value):
        self._setNumber(3, value)

    def getExchangeRate(self):
        return self._getNumber(4)

    def setExchangeRate(self, value):
        self._setNumber(4, value)

    def getHasError(self):
        return self._getBool(5)

    def setHasError(self, value):
        self._setBool(5, value)

    def getIsErrorTooltipVisible(self):
        return self._getBool(6)

    def setIsErrorTooltipVisible(self, value):
        self._setBool(6, value)

    def getCanApplyFreeXp(self):
        return self._getBool(7)

    def setCanApplyFreeXp(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(FreeXpBookModel, self)._initialize()
        self._addNumberProperty('playerXp', 0)
        self._addNumberProperty('discountSize', 0)
        self._addNumberProperty('currentXpValue', 0)
        self._addNumberProperty('currentMaxValue', 0)
        self._addNumberProperty('exchangeRate', 1)
        self._addBoolProperty('hasError', False)
        self._addBoolProperty('isErrorTooltipVisible', False)
        self._addBoolProperty('canApplyFreeXp', False)
