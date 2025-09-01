# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/lobby/awards/bonus_vehicles_reward.py
from gui.impl.gen import R
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from one_time_gift.gui.impl.lobby.awards.branch_reward_view import BranchRewardView
from one_time_gift.gui.impl.lobby.awards.packers import getOTGVehicleRewardsBonusPacker, filterNonOwnedVehicles
from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_reward_view_model import RewardType
from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_view_model import MainViews

class BonusVehiclesRewardView(BranchRewardView):
    _REWARD_TYPE = RewardType.BONUS_VEHICLES_REWARD

    @property
    def viewId(self):
        return MainViews.PREMIUM_VEHICLES_REWARD

    @staticmethod
    def _setResources(vm):
        locales = R.strings.one_time_gift.awards.bonusVehiclesReward
        vm.setTitle(locales.title())
        vm.setSubTitle(locales.subTitle())
        vm.setDefaultButtonTitle(locales.button.submit())
        vm.setBackground(R.images.gui.maps.icons.achievements.bg_summary())

    def _setRewards(self, vm, rewards):
        packBonusModelAndTooltipData(self._sortRewards(filter(filterNonOwnedVehicles, rewards)), vm.vehicleRewards, self._tooltipItems, packer=getOTGVehicleRewardsBonusPacker())
