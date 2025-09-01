# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/lobby/awards/branch_reward_view.py
from helpers import dependency
from gui.impl.gen import R
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from skeletons.gui.shared import IItemsCache
from one_time_gift.gui.impl.lobby.awards.base_reward_view import BaseRewardView
from one_time_gift.gui.impl.lobby.awards.packers import getOTGVehicleRewardsBonusPacker, composeVehicleBonuses
from one_time_gift.skeletons.gui.game_control import IOneTimeGiftController
from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_reward_view_model import RewardType
from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_view_model import MainViews
_TYPES_ORDER = ('lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG')

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _vehicleBonusSortKey(vehicleBonus, itemsCache=None):
    for vehCD in vehicleBonus.getValue():
        vehicle = itemsCache.items.getItemByCD(vehCD)
        if vehicle is not None:
            return (vehicle.level, _TYPES_ORDER.index(vehicle.type))

    return (-1, -1)


class BranchRewardView(BaseRewardView):
    _oneTimeGiftController = dependency.descriptor(IOneTimeGiftController)
    _REWARD_TYPE = RewardType.BRANCH_REWARD

    @property
    def viewId(self):
        return MainViews.BRANCH_REWARD

    @staticmethod
    def _composeRewards(bonuses):
        return composeVehicleBonuses(bonuses)

    def _setResources(self, vm):
        locales = R.strings.one_time_gift.awards.branchReward
        vm.setTitle(locales.title())
        vm.setBackground(R.images.gui.maps.icons.achievements.bg_summary())
        if not self._oneTimeGiftController.isFullListBranchReceived():
            vm.setDefaultButtonTitle(locales.button.selectAnotherBranch())
        elif not self._oneTimeGiftController.isAdditionalRewardReceived():
            if self._oneTimeGiftController.isPlayerNewbie():
                vm.setDefaultButtonTitle(locales.button.moreVehicles())
            else:
                vm.setDefaultButtonTitle(locales.button.moreRewards())
        else:
            vm.setDefaultButtonTitle(locales.button.affirmative())

    @classmethod
    def _sortRewards(cls, rewards):
        return sorted(rewards, key=_vehicleBonusSortKey)

    def _setRewards(self, vm, rewards):
        packBonusModelAndTooltipData(self._sortRewards(rewards), vm.vehicleRewards, self._tooltipItems, packer=getOTGVehicleRewardsBonusPacker())
