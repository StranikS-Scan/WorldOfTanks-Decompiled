# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback/popovers/winback_leave_mode_popover_view.py
from account_helpers.AccountSettings import Winback
from constants import WINBACK_CALL_BATTLE_TOKEN_DRAW_REASON
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.winback.popovers.winback_leave_mode_popover_view_model import WinbackLeaveModePopoverViewModel
from gui.impl.lobby.winback.tooltips.mode_info_tooltip import ModeInfoTooltip
from gui.impl.pub import PopOverViewImpl
from gui.shared import g_eventBus
from gui.shared.events import ModeSelectorPopoverEvent
from gui.winback.winback_helpers import leaveWinbackMode, selectRandom, setWinbackSetting
from helpers import dependency
from skeletons.gui.game_control import IWinbackController

class WinbackLeaveModePopoverView(PopOverViewImpl):
    __slots__ = ()
    _winbackController = dependency.descriptor(IWinbackController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.winback.popovers.WinbackLeaveModePopoverView())
        settings.flags = ViewFlags.VIEW
        settings.model = WinbackLeaveModePopoverViewModel()
        super(WinbackLeaveModePopoverView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WinbackLeaveModePopoverView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return ModeInfoTooltip() if contentID == R.views.lobby.winback.tooltips.ModeInfoTooltip() else super(WinbackLeaveModePopoverView, self).createToolTipContent(event, contentID)

    def _onLoading(self):
        super(WinbackLeaveModePopoverView, self)._onLoading()
        self.viewModel.setBattlesCount(self._winbackController.getWinbackBattlesCountLeft())
        self.__updateBulletSetting()

    def _initialize(self):
        super(WinbackLeaveModePopoverView, self)._initialize()
        g_eventBus.handleEvent(ModeSelectorPopoverEvent(ModeSelectorPopoverEvent.NAME, ctx={'active': True}))

    def _finalize(self):
        g_eventBus.handleEvent(ModeSelectorPopoverEvent(ModeSelectorPopoverEvent.NAME, ctx={'active': False}))
        super(WinbackLeaveModePopoverView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onClick, self.__onClick),)

    def __onClick(self):
        leaveWinbackMode(WINBACK_CALL_BATTLE_TOKEN_DRAW_REASON.MANUAL, showConfirmDialog=True, callback=selectRandom)

    def __updateBulletSetting(self):
        setWinbackSetting(Winback.BATTLE_SELECTOR_SETTINGS_BULLET_SHOWN, True)
