# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/currency_reserves/reserves_award_view_model.py
from frameworks.wulf import ViewModel

class ReservesAwardViewModel(ViewModel):
    __slots__ = ('onClose', 'onPremiumAccountExtend', 'onSubscriptionExtend')

    def __init__(self, properties=5, commands=3):
        super(ReservesAwardViewModel, self).__init__(properties=properties, commands=commands)

    def getCreditAmount(self):
        return self._getNumber(0)

    def setCreditAmount(self, value):
        self._setNumber(0, value)

    def getGoldAmount(self):
        return self._getNumber(1)

    def setGoldAmount(self, value):
        self._setNumber(1, value)

    def getIsPremiumActive(self):
        return self._getBool(2)

    def setIsPremiumActive(self, value):
        self._setBool(2, value)

    def getIsSubscriptionActive(self):
        return self._getBool(3)

    def setIsSubscriptionActive(self, value):
        self._setBool(3, value)

    def getIsSubscriptionEnabled(self):
        return self._getBool(4)

    def setIsSubscriptionEnabled(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(ReservesAwardViewModel, self)._initialize()
        self._addNumberProperty('creditAmount', 0)
        self._addNumberProperty('goldAmount', 0)
        self._addBoolProperty('isPremiumActive', False)
        self._addBoolProperty('isSubscriptionActive', False)
        self._addBoolProperty('isSubscriptionEnabled', False)
        self.onClose = self._addCommand('onClose')
        self.onPremiumAccountExtend = self._addCommand('onPremiumAccountExtend')
        self.onSubscriptionExtend = self._addCommand('onSubscriptionExtend')
