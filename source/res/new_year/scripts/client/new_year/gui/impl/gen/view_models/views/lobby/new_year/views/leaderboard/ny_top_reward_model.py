# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/leaderboard/ny_top_reward_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.reward_item_model import RewardItemModel

class NyTopRewardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(NyTopRewardModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardsType():
        return RewardItemModel

    def getTop(self):
        return self._getNumber(1)

    def setTop(self, value):
        self._setNumber(1, value)

    def getPointsToTop(self):
        return self._getNumber(2)

    def setPointsToTop(self, value):
        self._setNumber(2, value)

    def getIsRewarded(self):
        return self._getBool(3)

    def setIsRewarded(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(NyTopRewardModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addNumberProperty('top', 0)
        self._addNumberProperty('pointsToTop', 0)
        self._addBoolProperty('isRewarded', False)
