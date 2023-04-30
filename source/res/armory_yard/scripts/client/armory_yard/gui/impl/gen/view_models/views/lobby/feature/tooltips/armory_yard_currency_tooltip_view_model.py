# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/tooltips/armory_yard_currency_tooltip_view_model.py
from frameworks.wulf import ViewModel

class ArmoryYardCurrencyTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(ArmoryYardCurrencyTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getReceivedTokens(self):
        return self._getNumber(0)

    def setReceivedTokens(self, value):
        self._setNumber(0, value)

    def getTotalTokens(self):
        return self._getNumber(1)

    def setTotalTokens(self, value):
        self._setNumber(1, value)

    def getQuestsForToken(self):
        return self._getNumber(2)

    def setQuestsForToken(self, value):
        self._setNumber(2, value)

    def getStartTimestamp(self):
        return self._getNumber(3)

    def setStartTimestamp(self, value):
        self._setNumber(3, value)

    def getEndTimestamp(self):
        return self._getNumber(4)

    def setEndTimestamp(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(ArmoryYardCurrencyTooltipViewModel, self)._initialize()
        self._addNumberProperty('receivedTokens', 0)
        self._addNumberProperty('totalTokens', 0)
        self._addNumberProperty('questsForToken', 0)
        self._addNumberProperty('startTimestamp', 0)
        self._addNumberProperty('endTimestamp', 0)
