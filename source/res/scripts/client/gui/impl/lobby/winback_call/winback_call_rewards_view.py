# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback_call/winback_call_rewards_view.py
import typing
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_rewards_view_model import WinbackCallRewardsViewModel
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.winback_call.winback_call_helper import getWinBackCallBonuses, getWinBackBonusPacker
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from uilogging.winback_call.constants import WinbackCallLogItem, WinbackCallLogScreenParent
from uilogging.winback_call.loggers import WinBackCallLogger
if typing.TYPE_CHECKING:
    from typing import Dict

class WinbackCallRewardsView(ViewImpl):
    __slots__ = ('__tooltips',)

    def __init__(self, rewards):
        settings = ViewSettings(R.views.lobby.winback_call.WinbackCallRewardsView())
        settings.flags = ViewFlags.VIEW
        settings.args = (rewards,)
        settings.model = WinbackCallRewardsViewModel()
        self.__tooltips = {}
        super(WinbackCallRewardsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WinbackCallRewardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(WinbackCallRewardsView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            return self.__tooltips[tooltipId] if tooltipId in self.__tooltips else None

    def _onLoading(self, rewards, *args, **kwargs):
        super(WinbackCallRewardsView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__updateRewards(rewards, model)

    def _getEvents(self):
        events = super(WinbackCallRewardsView, self)._getEvents()
        return events + ((self.viewModel.onClose, self.__onClose),)

    def __updateRewards(self, rewards, model):
        bonuses = getWinBackCallBonuses(rewards)
        rewardsModel = model.getRewards()
        rewardsModel.clear()
        packBonusModelAndTooltipData(bonuses, rewardsModel, self.__tooltips, packer=getWinBackBonusPacker())

    def __onClose(self):
        WinBackCallLogger().handleClick(WinbackCallLogItem.CLOSE_BUTTON, WinbackCallLogScreenParent.REWARDS_SCREEN)
        self.destroyWindow()


class WinbackCallRewardsViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, rewards, parent=None):
        super(WinbackCallRewardsViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WinbackCallRewardsView(rewards), parent=parent)
