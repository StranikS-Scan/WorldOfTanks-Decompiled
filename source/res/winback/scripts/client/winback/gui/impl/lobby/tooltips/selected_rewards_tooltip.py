# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/lobby/tooltips/selected_rewards_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.auxiliary.rewards_helper import BlueprintBonusTypes
from gui.impl.gen import R
from winback.gui.impl.gen.view_models.views.lobby.tooltips.selected_rewards_tooltip_model import SelectedRewardsTooltipModel
from winback.gui.impl.gen.view_models.views.lobby.views.winback_reward_view_model import RewardName
from winback.gui.impl.lobby.winback_helpers import getDiscountFromGoody, getDiscountFromBlueprint
from gui.impl.pub import ViewImpl

class SelectedRewardsTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.winback.lobby.tooltips.SelectedRewardsTooltip(), model=SelectedRewardsTooltipModel())
        settings.args = args
        settings.kwargs = kwargs
        super(SelectedRewardsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SelectedRewardsTooltip, self).getViewModel()

    def _onLoading(self, selectedRewards):
        super(SelectedRewardsTooltip, self)._onLoading()
        vmType = self.viewModel.getSelectedRewardsType()
        with self.viewModel.getSelectedRewards().transaction() as tx:
            tx.clear()
            for level, reward in selectedRewards.iteritems():
                option = reward['option']
                name = option.getName()
                vm = vmType()
                vm.setVehicleLvl(level)
                vm.setName(name)
                if name == RewardName.VEHICLE_FOR_GIFT.value or name == RewardName.VEHICLE_DISCOUNT.value:
                    vm.setUserName(reward['vehicle'].userName)
                if name == RewardName.VEHICLE_DISCOUNT.value:
                    goodieId, blueprintsCount = option.getResources(reward['vehCD'])
                    vm.setCreditDiscount(getDiscountFromGoody(goodieId)[0])
                    vm.setExpDiscount(getDiscountFromBlueprint(reward['vehCD'], blueprintsCount))
                if name == BlueprintBonusTypes.BLUEPRINTS:
                    vm.setNation(option.getImageCategory())
                    vm.setCount(option.getCount())
                tx.addViewModel(vm)
