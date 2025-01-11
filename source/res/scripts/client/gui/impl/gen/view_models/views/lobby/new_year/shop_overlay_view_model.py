# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/shop_overlay_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_reward_kit_statistics_model import NyRewardKitStatisticsModel
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.reward_kit_guaranteed_reward_model import RewardKitGuaranteedRewardModel

class ShopOverlayViewModel(ViewModel):
    __slots__ = ()
    SUB_VIEW_ID = 1

    def __init__(self, properties=3, commands=0):
        super(ShopOverlayViewModel, self).__init__(properties=properties, commands=commands)

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

    def getIsMainPageVisible(self):
        return self._getBool(2)

    def setIsMainPageVisible(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(ShopOverlayViewModel, self)._initialize()
        self._addViewModelProperty('guaranteedReward', RewardKitGuaranteedRewardModel())
        self._addViewModelProperty('rewardKitStatistics', NyRewardKitStatisticsModel())
        self._addBoolProperty('isMainPageVisible', False)
