# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_onboarding_view_model.py
from frameworks.wulf import ViewModel

class BattlePassOnboardingViewModel(ViewModel):
    __slots__ = ('onCollectClick', 'onBackClick')

    def __init__(self, properties=3, commands=2):
        super(BattlePassOnboardingViewModel, self).__init__(properties=properties, commands=commands)

    def getIsOffersEnabled(self):
        return self._getBool(0)

    def setIsOffersEnabled(self, value):
        self._setBool(0, value)

    def getIsAllReceived(self):
        return self._getBool(1)

    def setIsAllReceived(self, value):
        self._setBool(1, value)

    def getMaxLevelForNewbie(self):
        return self._getNumber(2)

    def setMaxLevelForNewbie(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(BattlePassOnboardingViewModel, self)._initialize()
        self._addBoolProperty('isOffersEnabled', False)
        self._addBoolProperty('isAllReceived', False)
        self._addNumberProperty('maxLevelForNewbie', 0)
        self.onCollectClick = self._addCommand('onCollectClick')
        self.onBackClick = self._addCommand('onBackClick')
