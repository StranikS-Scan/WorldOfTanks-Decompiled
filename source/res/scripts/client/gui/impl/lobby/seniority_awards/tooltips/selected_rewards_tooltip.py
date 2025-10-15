# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/tooltips/selected_rewards_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.seniority_awards.tooltips.selected_reward_model import SelectedRewardModel
from gui.impl.gen.view_models.views.lobby.seniority_awards.tooltips.selected_rewards_tooltip_model import SelectedRewardsTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from tutorial.control.game_vars import getVehicleByIntCD

class SelectedRewardsTooltip(ViewImpl):
    __slots__ = ('__vehicleCDs',)

    def __init__(self, layoutID, vehicleCDs):
        settings = ViewSettings(layoutID)
        settings.model = SelectedRewardsTooltipModel()
        self.__vehicleCDs = vehicleCDs
        super(SelectedRewardsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SelectedRewardsTooltip, self).getViewModel()

    def _onLoading(self):
        super(SelectedRewardsTooltip, self)._onLoading()
        self.__updateData()

    @replaceNoneKwargsModel
    def __updateData(self, model=None):
        selectedRewards = model.getSelectedRewards()
        selectedRewards.clear()
        for vehCD in self.__vehicleCDs:
            reward = SelectedRewardModel()
            vehicle = getVehicleByIntCD(vehCD)
            reward.setVehicleLvl(vehicle.level)
            reward.setUserName(vehicle.userName)
            selectedRewards.addViewModel(reward)

        selectedRewards.invalidate()
