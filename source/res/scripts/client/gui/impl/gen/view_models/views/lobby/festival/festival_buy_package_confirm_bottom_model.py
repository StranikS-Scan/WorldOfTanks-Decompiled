# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_buy_package_confirm_bottom_model.py
from frameworks.wulf import ViewModel

class FestivalBuyPackageConfirmBottomModel(ViewModel):
    __slots__ = ('onCounterChanged',)

    def getPrice(self):
        return self._getNumber(0)

    def setPrice(self, value):
        self._setNumber(0, value)

    def getIsCounterVisible(self):
        return self._getBool(1)

    def setIsCounterVisible(self, value):
        self._setBool(1, value)

    def getSelectedCounter(self):
        return self._getNumber(2)

    def setSelectedCounter(self, value):
        self._setNumber(2, value)

    def getIsMoneyEnough(self):
        return self._getBool(3)

    def setIsMoneyEnough(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(FestivalBuyPackageConfirmBottomModel, self)._initialize()
        self._addNumberProperty('price', 0)
        self._addBoolProperty('isCounterVisible', False)
        self._addNumberProperty('selectedCounter', 1)
        self._addBoolProperty('isMoneyEnough', True)
        self.onCounterChanged = self._addCommand('onCounterChanged')
