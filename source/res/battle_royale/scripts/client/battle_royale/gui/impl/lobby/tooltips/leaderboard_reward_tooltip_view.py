# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/leaderboard_reward_tooltip_view.py
from __future__ import absolute_import
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.leaderboard_reward_tooltip_model import LeaderboardRewardTooltipModel
from battle_royale.gui.shared.tooltips.helper import fillProgressionPointsTableModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController

class LeaderboardRewardTooltipView(ViewImpl):
    battleRoyale = dependency.descriptor(IBattleRoyaleController)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.battle_royale.mono.lobby.tooltips.leaderboard_reward_tooltip_view())
        settings.model = LeaderboardRewardTooltipModel()
        super(LeaderboardRewardTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(LeaderboardRewardTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        fillProgressionPointsTableModel(self.viewModel, self.battleRoyale.getProgressionPointsTableData())
