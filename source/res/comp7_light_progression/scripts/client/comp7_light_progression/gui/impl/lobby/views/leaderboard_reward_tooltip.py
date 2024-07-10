# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light_progression/scripts/client/comp7_light_progression/gui/impl/lobby/views/leaderboard_reward_tooltip.py
from comp7_light_progression.gui.impl.gen.view_models.views.lobby.views.leaderboard_reward_tooltip_model import LeaderboardRewardTooltipModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class LeaderboardRewardTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.comp7_light_progression.LeaderboardRewardTooltipView())
        settings.model = LeaderboardRewardTooltipModel()
        super(LeaderboardRewardTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(LeaderboardRewardTooltipView, self).getViewModel()
