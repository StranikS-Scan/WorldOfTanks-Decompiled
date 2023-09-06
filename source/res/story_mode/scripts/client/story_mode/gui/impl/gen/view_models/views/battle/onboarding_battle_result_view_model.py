# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/battle/onboarding_battle_result_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class OnboardingBattleResultViewModel(ViewModel):
    __slots__ = ('onContinue', 'onLoaded')

    def __init__(self, properties=2, commands=2):
        super(OnboardingBattleResultViewModel, self).__init__(properties=properties, commands=commands)

    def getCauseText(self):
        return self._getResource(0)

    def setCauseText(self, value):
        self._setResource(0, value)

    def getMissionId(self):
        return self._getNumber(1)

    def setMissionId(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(OnboardingBattleResultViewModel, self)._initialize()
        self._addResourceProperty('causeText', R.invalid())
        self._addNumberProperty('missionId', 0)
        self.onContinue = self._addCommand('onContinue')
        self.onLoaded = self._addCommand('onLoaded')
