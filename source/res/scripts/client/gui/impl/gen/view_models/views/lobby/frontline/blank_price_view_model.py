# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/frontline/blank_price_view_model.py
from frameworks.wulf import ViewModel

class BlankPriceViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BlankPriceViewModel, self).__init__(properties=properties, commands=commands)

    def getTooltipId(self):
        return self._getString(0)

    def setTooltipId(self, value):
        self._setString(0, value)

    def getCount(self):
        return self._getNumber(1)

    def setCount(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(BlankPriceViewModel, self)._initialize()
        self._addStringProperty('tooltipId', '')
        self._addNumberProperty('count', 0)
