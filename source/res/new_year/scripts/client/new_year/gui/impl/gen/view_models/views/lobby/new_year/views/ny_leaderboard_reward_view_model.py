# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/ny_leaderboard_reward_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.reward_item_model import RewardItemModel

class NyLeaderboardRewardViewModel(ViewModel):
    __slots__ = ('onClose', 'onGoToLootbox')

    def __init__(self, properties=5, commands=2):
        super(NyLeaderboardRewardViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardsType():
        return RewardItemModel

    def getIsFinal(self):
        return self._getBool(1)

    def setIsFinal(self, value):
        self._setBool(1, value)

    def getPosition(self):
        return self._getNumber(2)

    def setPosition(self, value):
        self._setNumber(2, value)

    def getTop(self):
        return self._getNumber(3)

    def setTop(self, value):
        self._setNumber(3, value)

    def getStage(self):
        return self._getNumber(4)

    def setStage(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(NyLeaderboardRewardViewModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addBoolProperty('isFinal', False)
        self._addNumberProperty('position', 0)
        self._addNumberProperty('top', 0)
        self._addNumberProperty('stage', 0)
        self.onClose = self._addCommand('onClose')
        self.onGoToLootbox = self._addCommand('onGoToLootbox')
