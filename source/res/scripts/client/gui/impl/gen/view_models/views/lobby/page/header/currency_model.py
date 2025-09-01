# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/header/currency_model.py
from frameworks.wulf import ViewModel

class CurrencyModel(ViewModel):
    __slots__ = ()
    STATUS_SYNCING = 'SYNCING'
    STATUS_NOT_AVAILABLE = 'NOT_AVAILABLE'
    STATUS_AVAILABLE = 'AVAILABLE'

    def __init__(self, properties=4, commands=0):
        super(CurrencyModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getNumber(0)

    def setValue(self, value):
        self._setNumber(0, value)

    def getDiscount(self):
        return self._getNumber(1)

    def setDiscount(self, value):
        self._setNumber(1, value)

    def getStatus(self):
        return self._getString(2)

    def setStatus(self, value):
        self._setString(2, value)

    def getTooltipType(self):
        return self._getString(3)

    def setTooltipType(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(CurrencyModel, self)._initialize()
        self._addNumberProperty('value', 0)
        self._addNumberProperty('discount', 0)
        self._addStringProperty('status', '')
        self._addStringProperty('tooltipType', '')
