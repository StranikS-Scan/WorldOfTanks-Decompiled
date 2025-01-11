# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_challenge_progress_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.progress_reward_item_model import ProgressRewardItemModel

class NewYearChallengeProgressModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NewYearChallengeProgressModel, self).__init__(properties=properties, commands=commands)

    def getRewardLevel(self):
        return self._getNumber(0)

    def setRewardLevel(self, value):
        self._setNumber(0, value)

    def getStyleRewardIndex(self):
        return self._getNumber(1)

    def setStyleRewardIndex(self, value):
        self._setNumber(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return ProgressRewardItemModel

    def _initialize(self):
        super(NewYearChallengeProgressModel, self)._initialize()
        self._addNumberProperty('rewardLevel', 0)
        self._addNumberProperty('styleRewardIndex', -1)
        self._addArrayProperty('rewards', Array())
