# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/exchange/currency_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class CurrencyType(Enum):
    CREDITS = 'credits'
    GOLD = 'gold'
    CRYSTAL = 'crystal'
    FREEXP = 'freeXP'


class CurrencyModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(CurrencyModel, self).__init__(properties=properties, commands=commands)

    def getCurrencyType(self):
        return CurrencyType(self._getString(0))

    def setCurrencyType(self, value):
        self._setString(0, value.value)

    def getValue(self):
        return self._getNumber(1)

    def setValue(self, value):
        self._setNumber(1, value)

    def getTooltipId(self):
        return self._getNumber(2)

    def setTooltipId(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(CurrencyModel, self)._initialize()
        self._addStringProperty('currencyType', CurrencyType.GOLD.value)
        self._addNumberProperty('value', 0)
        self._addNumberProperty('tooltipId', 0)
