# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/tooltips/leaderboard_reward_tooltip.py
from comp7_light.gui.impl.gen.view_models.views.lobby.tooltips.leaderboard_reward_tooltip_model import LeaderboardRewardTooltipModel, State
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import IComp7LightController

class LeaderboardRewardTooltipView(ViewImpl):
    __slots__ = ('__state',)
    __comp7LightController = dependency.descriptor(IComp7LightController)

    def __init__(self, state=State.SIMPLIFIED):
        settings = ViewSettings(R.views.comp7_light.mono.lobby.leaderboard_reward_tooltip_view())
        settings.model = LeaderboardRewardTooltipModel()
        self.__state = state
        super(LeaderboardRewardTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(LeaderboardRewardTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(LeaderboardRewardTooltipView, self)._onLoading(*args, **kwargs)
        self._fillViewModel()

    def _fillViewModel(self):
        currentSeason = self.__comp7LightController.getCurrentSeason()
        seasonEndTimeLeft = int(currentSeason.getEndDate() - getServerUTCTime()) if currentSeason else 0
        with self.viewModel.transaction() as vm:
            vm.setState(self.__state)
            vm.setSeasonEndTimestamp(seasonEndTimeLeft)
