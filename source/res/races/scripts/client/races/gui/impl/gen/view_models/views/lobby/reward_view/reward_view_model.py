# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/lobby/reward_view/reward_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class RewardViewModel(ViewModel):
    __slots__ = ('onCloseButtonClick', 'onContinueButtonClick')

    def __init__(self, properties=7, commands=2):
        super(RewardViewModel, self).__init__(properties=properties, commands=commands)

    def getSubtitle(self):
        return self._getResource(0)

    def setSubtitle(self, value):
        self._setResource(0, value)

    def getTitle(self):
        return self._getResource(1)

    def setTitle(self, value):
        self._setResource(1, value)

    def getInfoText(self):
        return self._getResource(2)

    def setInfoText(self, value):
        self._setResource(2, value)

    def getDisplayRewardsCount(self):
        return self._getBool(3)

    def setDisplayRewardsCount(self, value):
        self._setBool(3, value)

    def getProgressionStages(self):
        return self._getArray(4)

    def setProgressionStages(self, value):
        self._setArray(4, value)

    @staticmethod
    def getProgressionStagesType():
        return int

    def getRewards(self):
        return self._getArray(5)

    def setRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def getMainRewards(self):
        return self._getArray(6)

    def setMainRewards(self, value):
        self._setArray(6, value)

    @staticmethod
    def getMainRewardsType():
        return BonusModel

    def _initialize(self):
        super(RewardViewModel, self)._initialize()
        self._addResourceProperty('subtitle', R.invalid())
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('infoText', R.invalid())
        self._addBoolProperty('displayRewardsCount', False)
        self._addArrayProperty('progressionStages', Array())
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('mainRewards', Array())
        self.onCloseButtonClick = self._addCommand('onCloseButtonClick')
        self.onContinueButtonClick = self._addCommand('onContinueButtonClick')
