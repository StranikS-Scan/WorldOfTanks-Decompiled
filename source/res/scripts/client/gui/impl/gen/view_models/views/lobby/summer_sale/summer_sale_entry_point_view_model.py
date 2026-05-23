# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/summer_sale/summer_sale_entry_point_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class StatusEnum(Enum):
    ACTIVE = 'active'
    ENDING = 'ending'
    DISABLE = 'disable'


class SummerSaleEntryPointViewModel(ViewModel):
    __slots__ = ('toSummerSaleEvent',)

    def __init__(self, properties=4, commands=1):
        super(SummerSaleEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getIsAloneBanner(self):
        return self._getBool(0)

    def setIsAloneBanner(self, value):
        self._setBool(0, value)

    def getTimer(self):
        return self._getNumber(1)

    def setTimer(self, value):
        self._setNumber(1, value)

    def getStatus(self):
        return StatusEnum(self._getString(2))

    def setStatus(self, value):
        self._setString(2, value.value)

    def getIsEnoughCurrency(self):
        return self._getBool(3)

    def setIsEnoughCurrency(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(SummerSaleEntryPointViewModel, self)._initialize()
        self._addBoolProperty('isAloneBanner', False)
        self._addNumberProperty('timer', 0)
        self._addStringProperty('status')
        self._addBoolProperty('isEnoughCurrency', False)
        self.toSummerSaleEvent = self._addCommand('toSummerSaleEvent')
