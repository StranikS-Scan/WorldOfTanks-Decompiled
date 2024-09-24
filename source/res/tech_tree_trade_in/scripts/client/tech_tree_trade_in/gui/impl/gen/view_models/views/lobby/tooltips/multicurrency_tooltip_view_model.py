# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/tooltips/multicurrency_tooltip_view_model.py
from frameworks.wulf import ViewModel

class MulticurrencyTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(MulticurrencyTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getIsFullPriceReached(self):
        return self._getBool(0)

    def setIsFullPriceReached(self, value):
        self._setBool(0, value)

    def getResourceType(self):
        return self._getString(1)

    def setResourceType(self, value):
        self._setString(1, value)

    def getLimit(self):
        return self._getNumber(2)

    def setLimit(self, value):
        self._setNumber(2, value)

    def getMaxValue(self):
        return self._getNumber(3)

    def setMaxValue(self, value):
        self._setNumber(3, value)

    def getCurValue(self):
        return self._getNumber(4)

    def setCurValue(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(MulticurrencyTooltipViewModel, self)._initialize()
        self._addBoolProperty('isFullPriceReached', False)
        self._addStringProperty('resourceType', '')
        self._addNumberProperty('limit', 0)
        self._addNumberProperty('maxValue', 0)
        self._addNumberProperty('curValue', 0)
