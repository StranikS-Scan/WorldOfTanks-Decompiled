# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/buy_button_model.py
from frameworks.wulf import ViewModel

class BuyButtonModel(ViewModel):
    __slots__ = ()
    BUY_BP = 'buyBPState'
    BUY_LEVELS = 'buyLevelsState'
    DISABLE = 'disableState'
    ONBOARDING = 'onboardingState'

    def __init__(self, properties=5, commands=0):
        super(BuyButtonModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getSellAnyLevelsUnlockTimeLeft(self):
        return self._getString(1)

    def setSellAnyLevelsUnlockTimeLeft(self, value):
        self._setString(1, value)

    def getSeasonTimeLeft(self):
        return self._getString(2)

    def setSeasonTimeLeft(self, value):
        self._setString(2, value)

    def getIsHighlightOn(self):
        return self._getBool(3)

    def setIsHighlightOn(self, value):
        self._setBool(3, value)

    def getShowBuyButtonBubble(self):
        return self._getBool(4)

    def setShowBuyButtonBubble(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(BuyButtonModel, self)._initialize()
        self._addStringProperty('state', 'buyBPState')
        self._addStringProperty('sellAnyLevelsUnlockTimeLeft', '')
        self._addStringProperty('seasonTimeLeft', '')
        self._addBoolProperty('isHighlightOn', False)
        self._addBoolProperty('showBuyButtonBubble', False)
