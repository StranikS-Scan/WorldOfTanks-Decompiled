# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tooltips/battle_pass_in_progress_tooltip_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_royale_reward_points import BattleRoyaleRewardPoints
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.reward_points_model import RewardPointsModel

class BattlePassInProgressTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(BattlePassInProgressTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewardPoints(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardPointsType():
        return RewardPointsModel

    @property
    def battleRoyaleRewardPoints(self):
        return self._getViewModel(1)

    @staticmethod
    def getBattleRoyaleRewardPointsType():
        return BattleRoyaleRewardPoints

    @property
    def rewardsCommon(self):
        return self._getViewModel(2)

    @staticmethod
    def getRewardsCommonType():
        return BonusModel

    @property
    def rewardsElite(self):
        return self._getViewModel(3)

    @staticmethod
    def getRewardsEliteType():
        return BonusModel

    def getLevel(self):
        return self._getNumber(4)

    def setLevel(self, value):
        self._setNumber(4, value)

    def getChapter(self):
        return self._getNumber(5)

    def setChapter(self, value):
        self._setNumber(5, value)

    def getCurrentPoints(self):
        return self._getNumber(6)

    def setCurrentPoints(self, value):
        self._setNumber(6, value)

    def getMaxPoints(self):
        return self._getNumber(7)

    def setMaxPoints(self, value):
        self._setNumber(7, value)

    def getIsBattlePassPurchased(self):
        return self._getBool(8)

    def setIsBattlePassPurchased(self, value):
        self._setBool(8, value)

    def getTimeTillEnd(self):
        return self._getString(9)

    def setTimeTillEnd(self, value):
        self._setString(9, value)

    def getBattleType(self):
        return self._getString(10)

    def setBattleType(self, value):
        self._setString(10, value)

    def getNotChosenRewardCount(self):
        return self._getNumber(11)

    def setNotChosenRewardCount(self, value):
        self._setNumber(11, value)

    def getIsExtra(self):
        return self._getBool(12)

    def setIsExtra(self, value):
        self._setBool(12, value)

    def getExpireTime(self):
        return self._getNumber(13)

    def setExpireTime(self, value):
        self._setNumber(13, value)

    def getFinalReward(self):
        return self._getString(14)

    def setFinalReward(self, value):
        self._setString(14, value)

    def _initialize(self):
        super(BattlePassInProgressTooltipViewModel, self)._initialize()
        self._addViewModelProperty('rewardPoints', UserListModel())
        self._addViewModelProperty('battleRoyaleRewardPoints', BattleRoyaleRewardPoints())
        self._addViewModelProperty('rewardsCommon', UserListModel())
        self._addViewModelProperty('rewardsElite', UserListModel())
        self._addNumberProperty('level', 0)
        self._addNumberProperty('chapter', 0)
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('maxPoints', 0)
        self._addBoolProperty('isBattlePassPurchased', False)
        self._addStringProperty('timeTillEnd', '')
        self._addStringProperty('battleType', '')
        self._addNumberProperty('notChosenRewardCount', 0)
        self._addBoolProperty('isExtra', False)
        self._addNumberProperty('expireTime', 0)
        self._addStringProperty('finalReward', '')
