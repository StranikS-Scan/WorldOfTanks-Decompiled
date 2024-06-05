# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/yearly_rewards_selection_screen.py
import typing
from AccountCommands import RES_SUCCESS
from frameworks.wulf import WindowFlags
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.yearly_rewards_selection_screen_model import YearlyRewardsSelectionScreenModel
from gui.impl.lobby.common.selectable_reward_base import SelectableRewardBase
from gui.impl.pub.lobby_window import LobbyWindow
from gui.selectable_reward.common import Comp7SelectableRewardManager
from gui.shared.event_dispatcher import showComp7SelectedRewardsScreen
if typing.TYPE_CHECKING:
    from gui.SystemMessages import ResultMsg

class YearlyRewardsSelectionView(SelectableRewardBase):
    _helper = Comp7SelectableRewardManager

    def __init__(self):
        super(YearlyRewardsSelectionView, self).__init__(R.views.lobby.comp7.YearlyRewardsSelectionScreen(), self._helper.getAvailableSelectableBonuses(), YearlyRewardsSelectionScreenModel)

    @property
    def viewModel(self):
        return super(YearlyRewardsSelectionView, self).getViewModel()

    def _processReceivedRewards(self, result):
        if result.success and result.auxData:
            successRewards = result.auxData.get(RES_SUCCESS, {})
            if successRewards:
                showComp7SelectedRewardsScreen(successRewards)
        else:
            SystemMessages.pushI18nMessage(backport.text(R.strings.system_messages.battlePass.rewardChoice.error()), type=SystemMessages.SM_TYPE.Error)
        self.destroyWindow()


class YearlyRewardsSelectionWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self):
        super(YearlyRewardsSelectionWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=YearlyRewardsSelectionView())
