# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/buy_toy_view_model.py
from frameworks.wulf import ViewModel

class BuyToyViewModel(ViewModel):
    __slots__ = ('onClose', 'onBuy')

    def __init__(self, properties=4, commands=2):
        super(BuyToyViewModel, self).__init__(properties=properties, commands=commands)

    def getToyName(self):
        return self._getString(0)

    def setToyName(self, value):
        self._setString(0, value)

    def getToyIcon(self):
        return self._getString(1)

    def setToyIcon(self, value):
        self._setString(1, value)

    def getCost(self):
        return self._getNumber(2)

    def setCost(self, value):
        self._setNumber(2, value)

    def getIsBuyBtnDisable(self):
        return self._getBool(3)

    def setIsBuyBtnDisable(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(BuyToyViewModel, self)._initialize()
        self._addStringProperty('toyName', '')
        self._addStringProperty('toyIcon', '')
        self._addNumberProperty('cost', 0)
        self._addBoolProperty('isBuyBtnDisable', True)
        self.onClose = self._addCommand('onClose')
        self.onBuy = self._addCommand('onBuy')
