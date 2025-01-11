# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bob/bob_team_rewards_view.py
import WWISE
from frameworks.wulf import ViewSettings
from gui.bob.bob_bonuses_packers import packBonusModelAndTooltipData
from gui.game_control.bob_sound_controller import BOB_TEAM_REWARD_OPEN
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.bob.bob_team_rewards_view_model import BobTeamRewardsViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from shared_utils import findFirst

class BobTeamRewardView(ViewImpl):
    __slots__ = ('__tooltipItems', '__tooltipWindow')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.bob.BobTeamRewardsView())
        settings.model = BobTeamRewardsViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__tooltipItems = {}
        self.__tooltipWindow = None
        super(BobTeamRewardView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(BobTeamRewardView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            tooltipData = self.__tooltipItems.get(tooltipId)
            if tooltipData is None:
                return
            window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
            self.__tooltipWindow = window
            window.load()
            return window
        else:
            return super(BobTeamRewardView, self).createToolTip(event)

    def _onLoading(self, bonuses, level, *args, **kwargs):
        super(BobTeamRewardView, self)._onLoading(*args, **kwargs)
        self.__updateViewModel(bonuses, level)
        WWISE.WW_eventGlobal(BOB_TEAM_REWARD_OPEN)

    def _finalize(self):
        self.__clearTooltips()

    def __updateViewModel(self, bonuses, level):
        with self.getViewModel().transaction() as model:
            vehiclesBonus = findFirst(lambda b: b.getName() == 'vehicles', bonuses)
            if vehiclesBonus is None:
                title = R.strings.bob.teamReward.title()
            else:
                title = R.strings.bob.teamReward.title.vehicle()
            model.setTitle(backport.text(title))
            model.setLevel(level + 1)
            packBonusModelAndTooltipData(bonuses, model.rewards, self.__tooltipItems)
        return

    def __clearTooltips(self):
        self.__tooltipItems.clear()
        if self.__tooltipWindow is not None:
            self.__tooltipWindow.destroy()
            self.__tooltipWindow = None
        return


class BobTeamRewardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, bonuses, level):
        super(BobTeamRewardWindow, self).__init__(content=BobTeamRewardView(bonuses, level))
