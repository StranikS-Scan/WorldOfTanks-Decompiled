# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/sub_views/currency_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class CurrencySize(Enum):
    SMALL = 'small'
    BIG = 'big'
    LARGE = 'large'


class CurrencyType(Enum):
    CREDITS = 'credits'
    GOLD = 'gold'
    CRYSTAL = 'crystal'
    XP = 'xp'
    FREEXP = 'freeXP'
    EQUIPCOIN = 'equipCoin'


class CurrencyViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(CurrencyViewModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getNumber(0)

    def setValue(self, value):
        self._setNumber(0, value)

    def getIsEnough(self):
        return self._getBool(1)

    def setIsEnough(self, value):
        self._setBool(1, value)

    def getIsDiscount(self):
        return self._getBool(2)

    def setIsDiscount(self, value):
        self._setBool(2, value)

    def getDiscountValue(self):
        return self._getReal(3)

    def setDiscountValue(self, value):
        self._setReal(3, value)

    def getShowPlus(self):
        return self._getBool(4)

    def setShowPlus(self, value):
        self._setBool(4, value)

    def getSize(self):
        return CurrencySize(self._getString(5))

    def setSize(self, value):
        self._setString(5, value.value)

    def getType(self):
        return CurrencyType(self._getString(6))

    def setType(self, value):
        self._setString(6, value.value)

    def _initialize(self):
        super(CurrencyViewModel, self)._initialize()
        self._addNumberProperty('value', 0)
        self._addBoolProperty('isEnough', False)
        self._addBoolProperty('isDiscount', False)
        self._addRealProperty('discountValue', 0.0)
        self._addBoolProperty('showPlus', False)
        self._addStringProperty('size')
        self._addStringProperty('type')
