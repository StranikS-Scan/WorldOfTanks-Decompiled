# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/rts_currency_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class CurrencyTypeEnum(Enum):
    CURRENCY1X1 = 'rts1x1currency'
    CURRENCY1X7 = 'rts1x7currency'


class RtsCurrencyViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(RtsCurrencyViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrencyValue(self):
        return self._getNumber(0)

    def setCurrencyValue(self, value):
        self._setNumber(0, value)

    def getCurrencyPrice(self):
        return self._getNumber(1)

    def setCurrencyPrice(self, value):
        self._setNumber(1, value)

    def getCurrencyType(self):
        return CurrencyTypeEnum(self._getString(2))

    def setCurrencyType(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(RtsCurrencyViewModel, self)._initialize()
        self._addNumberProperty('currencyValue', 0)
        self._addNumberProperty('currencyPrice', 0)
        self._addStringProperty('currencyType')
