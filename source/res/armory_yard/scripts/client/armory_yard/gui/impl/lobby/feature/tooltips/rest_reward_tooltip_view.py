# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/tooltips/rest_reward_tooltip_view.py
from armory_yard.gui.shared.bonus_packers import getArmoryYardBuyViewPacker
from frameworks.wulf import ViewSettings
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.tooltips.rest_reward_tooltip_view_model import RestRewardTooltipViewModel
from gui.impl.gen import R
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.pub import ViewImpl

class RestRewardTooltipView(ViewImpl):
    __slots__ = ('__rewards',)

    def __init__(self, rewards):
        settings = ViewSettings(R.views.armory_yard.lobby.feature.tooltips.RestRewardTooltipView())
        settings.model = RestRewardTooltipViewModel()
        self.__rewards = rewards
        super(RestRewardTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RestRewardTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RestRewardTooltipView, self)._onLoading()
        with self.viewModel.transaction() as vm:
            rewardsModel = vm.getRewards()
            packBonusModelAndTooltipData(self.__rewards, rewardsModel, packer=getArmoryYardBuyViewPacker())
            rewardsModel.invalidate()
