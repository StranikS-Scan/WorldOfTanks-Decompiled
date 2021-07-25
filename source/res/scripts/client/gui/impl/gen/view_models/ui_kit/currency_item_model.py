# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/currency_item_model.py
from frameworks.wulf import ViewModel

class CurrencyItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(CurrencyItemModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getString(0)

    def setValue(self, value):
        self._setString(0, value)

    def getCurrency(self):
        return self._getString(1)

    def setCurrency(self, value):
        self._setString(1, value)

    def getSpecialTooltip(self):
        return self._getString(2)

    def setSpecialTooltip(self, value):
        self._setString(2, value)

    def getTooltipHeader(self):
        return self._getString(3)

    def setTooltipHeader(self, value):
        self._setString(3, value)

    def getTooltipBody(self):
        return self._getString(4)

    def setTooltipBody(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(CurrencyItemModel, self)._initialize()
        self._addStringProperty('value', '--')
        self._addStringProperty('currency', '')
        self._addStringProperty('specialTooltip', '')
        self._addStringProperty('tooltipHeader', '')
        self._addStringProperty('tooltipBody', '')
