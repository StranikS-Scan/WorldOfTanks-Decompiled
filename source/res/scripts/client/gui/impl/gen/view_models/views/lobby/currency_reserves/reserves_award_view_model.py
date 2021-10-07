# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/currency_reserves/reserves_award_view_model.py
from frameworks.wulf import ViewModel

class ReservesAwardViewModel(ViewModel):
    __slots__ = ('onClose', 'onPremiumAccountExtend', 'onSubscriptionExtend')

    def __init__(self, properties=4, commands=3):
        super(ReservesAwardViewModel, self).__init__(properties=properties, commands=commands)

    def getCreditAmount(self):
        return self._getNumber(0)

    def setCreditAmount(self, value):
        self._setNumber(0, value)

    def getGoldAmount(self):
        return self._getNumber(1)

    def setGoldAmount(self, value):
        self._setNumber(1, value)

    def getShowCreditWarning(self):
        return self._getBool(2)

    def setShowCreditWarning(self, value):
        self._setBool(2, value)

    def getShowGoldWarning(self):
        return self._getBool(3)

    def setShowGoldWarning(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(ReservesAwardViewModel, self)._initialize()
        self._addNumberProperty('creditAmount', 0)
        self._addNumberProperty('goldAmount', 0)
        self._addBoolProperty('showCreditWarning', False)
        self._addBoolProperty('showGoldWarning', False)
        self.onClose = self._addCommand('onClose')
        self.onPremiumAccountExtend = self._addCommand('onPremiumAccountExtend')
        self.onSubscriptionExtend = self._addCommand('onSubscriptionExtend')
