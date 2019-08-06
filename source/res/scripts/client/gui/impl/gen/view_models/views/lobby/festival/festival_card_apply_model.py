# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_card_apply_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class FestivalCardApplyModel(ViewModel):
    __slots__ = ('onPlayerCardReset', 'onPlayerCardApply')

    def getPaymentItems(self):
        return self._getArray(0)

    def setPaymentItems(self, value):
        self._setArray(0, value)

    def getStorageItems(self):
        return self._getArray(1)

    def setStorageItems(self, value):
        self._setArray(1, value)

    def getBuyCost(self):
        return self._getNumber(2)

    def setBuyCost(self, value):
        self._setNumber(2, value)

    def getIsCanBuy(self):
        return self._getBool(3)

    def setIsCanBuy(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(FestivalCardApplyModel, self)._initialize()
        self._addArrayProperty('paymentItems', Array())
        self._addArrayProperty('storageItems', Array())
        self._addNumberProperty('buyCost', 0)
        self._addBoolProperty('isCanBuy', False)
        self.onPlayerCardReset = self._addCommand('onPlayerCardReset')
        self.onPlayerCardApply = self._addCommand('onPlayerCardApply')
