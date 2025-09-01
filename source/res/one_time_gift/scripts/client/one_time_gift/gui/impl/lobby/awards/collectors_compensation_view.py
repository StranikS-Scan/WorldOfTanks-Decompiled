# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/lobby/awards/collectors_compensation_view.py
from gui.impl.gen import R
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from helpers import dependency
from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_view_model import MainViews
from one_time_gift.gui.impl.gen.view_models.views.lobby.one_time_gift_reward_view_model import RewardType
from one_time_gift.gui.impl.lobby.awards.packers import getOTGMixedRewardsBonusPacker, composeBonuses
from one_time_gift.gui.impl.lobby.awards.base_reward_view import BaseRewardView
from one_time_gift.skeletons.gui.game_control import IOneTimeGiftController

class CollectorsCompensationView(BaseRewardView):
    __oneTimeGiftController = dependency.descriptor(IOneTimeGiftController)
    _REWARD_TYPE = RewardType.COLLECTORS_COMPENSATION_REWARD

    @property
    def viewId(self):
        return MainViews.COLLECTORS_COMPENSATION_REWARD

    @staticmethod
    def _composeRewards(bonuses):
        return composeBonuses(bonuses)

    def _setResources(self, vm):
        locales = R.strings.one_time_gift.awards.collectorsCompensation
        vm.setTitle(locales.title())
        vm.setUnderTitle(locales.underTitle())
        vm.setSubTitle(locales.subTitle())
        if not self.__oneTimeGiftController.isAdditionalRewardReceived():
            submit = locales.button.moreRewards
        else:
            submit = locales.button.affirmative
        vm.setDefaultButtonTitle(submit())
        vm.setBackground(R.images.gui.maps.icons.achievements.bg_summary())

    def _setRewards(self, vm, rewards):
        packBonusModelAndTooltipData(rewards, vm.mainRewards, self._tooltipItems, packer=getOTGMixedRewardsBonusPacker())
