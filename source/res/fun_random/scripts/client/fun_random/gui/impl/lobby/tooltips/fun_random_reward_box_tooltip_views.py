# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/tooltips/fun_random_reward_box_tooltip_views.py
from gui.impl.gen import R
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip

class NearestAdditionalRewardsTooltip(AdditionalRewardsTooltip):
    __slots__ = ()

    @classmethod
    def _getHeader(cls):
        return R.strings.tooltips.quests.awards.nearest.header()
