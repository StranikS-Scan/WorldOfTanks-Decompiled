# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialog_prices_content_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class DialogPricesContentModel(ViewModel):
    __slots__ = ()

    def getValueMainCost(self):
        return self._getString(0)

    def setValueMainCost(self, value):
        self._setString(0, value)

    def getIconMainCost(self):
        return self._getResource(1)

    def setIconMainCost(self, value):
        self._setResource(1, value)

    def getNotEnoughMain(self):
        return self._getBool(2)

    def setNotEnoughMain(self, value):
        self._setBool(2, value)

    def getValueAdditionalCost(self):
        return self._getString(3)

    def setValueAdditionalCost(self, value):
        self._setString(3, value)

    def getIconAdditionalCost(self):
        return self._getResource(4)

    def setIconAdditionalCost(self, value):
        self._setResource(4, value)

    def getNotEnoughAdditional(self):
        return self._getBool(5)

    def setNotEnoughAdditional(self, value):
        self._setBool(5, value)

    def getTooltipId(self):
        return self._getNumber(6)

    def setTooltipId(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(DialogPricesContentModel, self)._initialize()
        self._addStringProperty('valueMainCost', '0')
        self._addResourceProperty('iconMainCost', R.invalid())
        self._addBoolProperty('notEnoughMain', False)
        self._addStringProperty('valueAdditionalCost', '0')
        self._addResourceProperty('iconAdditionalCost', R.invalid())
        self._addBoolProperty('notEnoughAdditional', False)
        self._addNumberProperty('tooltipId', 0)
