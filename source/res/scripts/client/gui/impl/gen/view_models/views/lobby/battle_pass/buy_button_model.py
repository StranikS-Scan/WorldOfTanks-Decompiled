# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/buy_button_model.py
from frameworks.wulf import ViewModel

class BuyButtonModel(ViewModel):
    __slots__ = ()
    BUY_BP = 'buyBPState'
    BUY_LEVELS = 'buyLevelsState'
    DISABLE_BP = 'disableBPState'
    DISABLE_LEVELS = 'disableLevelsState'

    def __init__(self, properties=4, commands=0):
        super(BuyButtonModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getSeasonTimeLeft(self):
        return self._getString(1)

    def setSeasonTimeLeft(self, value):
        self._setString(1, value)

    def getIsHighlightOn(self):
        return self._getBool(2)

    def setIsHighlightOn(self, value):
        self._setBool(2, value)

    def getShowBuyButtonBubble(self):
        return self._getBool(3)

    def setShowBuyButtonBubble(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(BuyButtonModel, self)._initialize()
        self._addStringProperty('state', 'buyBPState')
        self._addStringProperty('seasonTimeLeft', '')
        self._addBoolProperty('isHighlightOn', False)
        self._addBoolProperty('showBuyButtonBubble', False)
