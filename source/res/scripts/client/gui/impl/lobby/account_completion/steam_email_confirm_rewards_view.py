# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/steam_email_confirm_rewards_view.py
import typing
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.battle_pass.sounds import BattlePassSounds
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.steam_email_confirm_rewards_view_model import SteamEmailConfirmRewardsViewModel
from gui.impl.lobby.account_completion.utils.common import fillRewards
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.sounds.filters import States, StatesGroup
from sound_gui_manager import CommonSoundSpaceSettings
if typing.TYPE_CHECKING:
    from typing import Dict

class SteamEmailConfirmRewardsView(ViewImpl):
    __slots__ = ('__tooltips',)
    _COMMON_SOUND_SPACE = CommonSoundSpaceSettings(name=StatesGroup.OVERLAY_HANGAR_GENERAL, entranceStates={StatesGroup.OVERLAY_HANGAR_GENERAL: States.OVERLAY_HANGAR_GENERAL_ON}, exitStates={StatesGroup.OVERLAY_HANGAR_GENERAL: States.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=BattlePassSounds.REWARD_SCREEN, exitEvent='', parentSpace='')

    def __init__(self, rewards):
        settings = ViewSettings(R.views.lobby.account_completion.SteamEmailConfirmRewardsView())
        settings.flags = ViewFlags.VIEW
        settings.args = (rewards,)
        settings.model = SteamEmailConfirmRewardsViewModel()
        self.__tooltips = {}
        super(SteamEmailConfirmRewardsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SteamEmailConfirmRewardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(SteamEmailConfirmRewardsView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips.get(tooltipId)

    def _onLoading(self, rewards, *args, **kwargs):
        super(SteamEmailConfirmRewardsView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__updateRewards(rewards, model)

    def _getEvents(self):
        events = super(SteamEmailConfirmRewardsView, self)._getEvents()
        return events + ((self.viewModel.onClose, self.__onClose),)

    def __updateRewards(self, rewards, model):
        fillRewards(model, rewards, self.__tooltips)

    def __onClose(self):
        self.destroyWindow()


class SteamEmailConfirmRewardsViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, rewards, parent=None):
        super(SteamEmailConfirmRewardsViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=SteamEmailConfirmRewardsView(rewards), parent=parent)
