# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ranked/rank_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class RankModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(RankModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardsType():
        return RewardItemModel

    def getRankID(self):
        return self._getNumber(1)

    def setRankID(self, value):
        self._setNumber(1, value)

    def getStepsToRank(self):
        return self._getNumber(2)

    def setStepsToRank(self, value):
        self._setNumber(2, value)

    def getIsUnburnable(self):
        return self._getBool(3)

    def setIsUnburnable(self, value):
        self._setBool(3, value)

    def getNeedTakeReward(self):
        return self._getBool(4)

    def setNeedTakeReward(self, value):
        self._setBool(4, value)

    def getCanTakeReward(self):
        return self._getBool(5)

    def setCanTakeReward(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(RankModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addNumberProperty('rankID', 0)
        self._addNumberProperty('stepsToRank', 0)
        self._addBoolProperty('isUnburnable', False)
        self._addBoolProperty('needTakeReward', False)
        self._addBoolProperty('canTakeReward', False)
