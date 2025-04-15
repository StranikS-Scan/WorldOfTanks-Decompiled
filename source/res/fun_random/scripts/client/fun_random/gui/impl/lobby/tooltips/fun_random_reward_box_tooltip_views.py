# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/tooltips/fun_random_reward_box_tooltip_views.py
from fun_random.gui.feature.util.fun_mixins import FunProgressionWatcher
from gui.impl.gen import R
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip

class NearestAdditionalRewardsTooltip(AdditionalRewardsTooltip, FunProgressionWatcher):
    __slots__ = ()

    @classmethod
    def _getHeader(cls):
        progression = cls.getActiveProgression()
        return R.strings.tooltips.quests.awards.nearest.header() if progression is None or cls.getActiveProgression().isInUnlimitedProgression else R.strings.fun_random.quests.limitedProgression.awards.nearest.header()

    @classmethod
    def _getHeaderCount(cls):
        progression = cls.getActiveProgression()
        return 0 if progression is None or progression.isInUnlimitedProgression else progression.activeStage.requiredCounter
