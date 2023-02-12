# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_buy_rewards_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class PackageType(IntEnum):
    BATTLEPASS = 0
    ANYLEVELS = 1
    SHOPOFFER = 2


class BattlePassBuyRewardsViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(BattlePassBuyRewardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def nowRewards(self):
        return self._getViewModel(0)

    @staticmethod
    def getNowRewardsType():
        return RewardItemModel

    @property
    def futureRewards(self):
        return self._getViewModel(1)

    @staticmethod
    def getFutureRewardsType():
        return RewardItemModel

    @property
    def topPriorityRewards(self):
        return self._getViewModel(2)

    @staticmethod
    def getTopPriorityRewardsType():
        return RewardItemModel

    def getFromLevel(self):
        return self._getNumber(3)

    def setFromLevel(self, value):
        self._setNumber(3, value)

    def getToLevel(self):
        return self._getNumber(4)

    def setToLevel(self, value):
        self._setNumber(4, value)

    def getPackageState(self):
        return PackageType(self._getNumber(5))

    def setPackageState(self, value):
        self._setNumber(5, value.value)

    def getChapterID(self):
        return self._getNumber(6)

    def setChapterID(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(BattlePassBuyRewardsViewModel, self)._initialize()
        self._addViewModelProperty('nowRewards', UserListModel())
        self._addViewModelProperty('futureRewards', UserListModel())
        self._addViewModelProperty('topPriorityRewards', UserListModel())
        self._addNumberProperty('fromLevel', 0)
        self._addNumberProperty('toLevel', 0)
        self._addNumberProperty('packageState')
        self._addNumberProperty('chapterID', 0)
