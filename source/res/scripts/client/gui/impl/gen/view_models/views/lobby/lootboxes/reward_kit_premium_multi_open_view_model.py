# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/reward_kit_premium_multi_open_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.lootboxes.components.loot_box_multi_open_renderer_model import LootBoxMultiOpenRendererModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_reward_kit_statistics_model import NyRewardKitStatisticsModel
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.reward_kit_guaranteed_reward_model import RewardKitGuaranteedRewardModel

class RewardKitPremiumMultiOpenViewModel(ViewModel):
    __slots__ = ('onOpenBox', 'showSpecialReward', 'openNextBoxes', 'onViewShowed', 'onClose')
    WINDOW_MAX_BOX_COUNT = 5

    def __init__(self, properties=16, commands=5):
        super(RewardKitPremiumMultiOpenViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def guaranteedReward(self):
        return self._getViewModel(0)

    @staticmethod
    def getGuaranteedRewardType():
        return RewardKitGuaranteedRewardModel

    @property
    def rewardKitStatistics(self):
        return self._getViewModel(1)

    @staticmethod
    def getRewardKitStatisticsType():
        return NyRewardKitStatisticsModel

    @property
    def rewardRows(self):
        return self._getViewModel(2)

    @staticmethod
    def getRewardRowsType():
        return LootBoxMultiOpenRendererModel

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getRewardsType():
        return LootBoxMultiOpenRendererModel

    def getBoxesCounter(self):
        return self._getNumber(4)

    def setBoxesCounter(self, value):
        self._setNumber(4, value)

    def getMaxRewardsInRow(self):
        return self._getNumber(5)

    def setMaxRewardsInRow(self, value):
        self._setNumber(5, value)

    def getBoxCategory(self):
        return self._getString(6)

    def setBoxCategory(self, value):
        self._setString(6, value)

    def getIsRewardKitsEnabled(self):
        return self._getBool(7)

    def setIsRewardKitsEnabled(self, value):
        self._setBool(7, value)

    def getHardReset(self):
        return self._getBool(8)

    def setHardReset(self, value):
        self._setBool(8, value)

    def getIsPausedForSpecial(self):
        return self._getBool(9)

    def setIsPausedForSpecial(self, value):
        self._setBool(9, value)

    def getIsOnPause(self):
        return self._getBool(10)

    def setIsOnPause(self, value):
        self._setBool(10, value)

    def getLeftToOpenCount(self):
        return self._getNumber(11)

    def setLeftToOpenCount(self, value):
        self._setNumber(11, value)

    def getCurrentPage(self):
        return self._getNumber(12)

    def setCurrentPage(self, value):
        self._setNumber(12, value)

    def getIsServerError(self):
        return self._getBool(13)

    def setIsServerError(self, value):
        self._setBool(13, value)

    def getNeedToOpen(self):
        return self._getNumber(14)

    def setNeedToOpen(self, value):
        self._setNumber(14, value)

    def getIsMemoryRiskySystem(self):
        return self._getBool(15)

    def setIsMemoryRiskySystem(self, value):
        self._setBool(15, value)

    def _initialize(self):
        super(RewardKitPremiumMultiOpenViewModel, self)._initialize()
        self._addViewModelProperty('guaranteedReward', RewardKitGuaranteedRewardModel())
        self._addViewModelProperty('rewardKitStatistics', NyRewardKitStatisticsModel())
        self._addViewModelProperty('rewardRows', UserListModel())
        self._addArrayProperty('rewards', Array())
        self._addNumberProperty('boxesCounter', 0)
        self._addNumberProperty('maxRewardsInRow', 0)
        self._addStringProperty('boxCategory', '')
        self._addBoolProperty('isRewardKitsEnabled', True)
        self._addBoolProperty('hardReset', False)
        self._addBoolProperty('isPausedForSpecial', False)
        self._addBoolProperty('isOnPause', False)
        self._addNumberProperty('leftToOpenCount', 0)
        self._addNumberProperty('currentPage', 0)
        self._addBoolProperty('isServerError', False)
        self._addNumberProperty('needToOpen', 0)
        self._addBoolProperty('isMemoryRiskySystem', False)
        self.onOpenBox = self._addCommand('onOpenBox')
        self.showSpecialReward = self._addCommand('showSpecialReward')
        self.openNextBoxes = self._addCommand('openNextBoxes')
        self.onViewShowed = self._addCommand('onViewShowed')
        self.onClose = self._addCommand('onClose')
