# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_preview/buying_panel/style_buying_panel_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class StyleBuyingStatus(IntEnum):
    AVAILABLE = 0
    NOTENOUGHMONEY = 1
    BPNOTPASSED = 2


class StyleBuyingPanelModel(ViewModel):
    __slots__ = ('onBuy',)

    def __init__(self, properties=5, commands=1):
        super(StyleBuyingPanelModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getPrice(self):
        return self._getNumber(1)

    def setPrice(self, value):
        self._setNumber(1, value)

    def getCurrency(self):
        return self._getString(2)

    def setCurrency(self, value):
        self._setString(2, value)

    def getUserCurrency(self):
        return self._getNumber(3)

    def setUserCurrency(self, value):
        self._setNumber(3, value)

    def getStatus(self):
        return StyleBuyingStatus(self._getNumber(4))

    def setStatus(self, value):
        self._setNumber(4, value.value)

    def _initialize(self):
        super(StyleBuyingPanelModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addNumberProperty('price', 0)
        self._addStringProperty('currency', '')
        self._addNumberProperty('userCurrency', 0)
        self._addNumberProperty('status')
        self.onBuy = self._addCommand('onBuy')
