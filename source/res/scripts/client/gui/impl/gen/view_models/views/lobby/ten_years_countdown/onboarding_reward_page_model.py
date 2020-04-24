# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ten_years_countdown/onboarding_reward_page_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class OnboardingRewardPageModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(OnboardingRewardPageModel, self).__init__(properties=properties, commands=commands)

    def getRewardImage(self):
        return self._getResource(0)

    def setRewardImage(self, value):
        self._setResource(0, value)

    def getRewardSubTitle(self):
        return self._getResource(1)

    def setRewardSubTitle(self, value):
        self._setResource(1, value)

    def getRewardDescription(self):
        return self._getResource(2)

    def setRewardDescription(self, value):
        self._setResource(2, value)

    def getIsRewardImageShown(self):
        return self._getBool(3)

    def setIsRewardImageShown(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(OnboardingRewardPageModel, self)._initialize()
        self._addResourceProperty('rewardImage', R.invalid())
        self._addResourceProperty('rewardSubTitle', R.invalid())
        self._addResourceProperty('rewardDescription', R.invalid())
        self._addBoolProperty('isRewardImageShown', False)
