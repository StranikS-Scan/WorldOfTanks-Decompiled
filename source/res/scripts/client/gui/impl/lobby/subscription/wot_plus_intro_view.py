# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/subscription/wot_plus_intro_view.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import SHOWN_WOT_PLUS_INTRO
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import LobbyHeader
from gui.Scaleform.daapi.view.lobby.wot_plus.sound_constants import WOT_PLUS_INTRO_SOUND_SPACE
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.impl.gen.view_models.views.lobby.subscription.wot_plus_intro_view_model import WotPlusIntroViewModel
from gui.impl.pub import ViewImpl
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showWotPlusInfoPage
from gui.shared.events import ViewEventType, LoadViewEvent
from helpers import dependency
from skeletons.gui.game_control import IWotPlusController
from uilogging.wot_plus.loggers import WotPlusAttendanceRewardScreenLogger
from uilogging.wot_plus.logging_constants import WotPlusInfoPageSource

class WotPlusIntroView(ViewImpl, EventSystemEntity):
    _COMMON_SOUND_SPACE = WOT_PLUS_INTRO_SOUND_SPACE
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)
    __slots__ = ('_wotPlusLogger',)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = WotPlusIntroViewModel()
        self._wotPlusLogger = WotPlusAttendanceRewardScreenLogger()
        super(WotPlusIntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WotPlusIntroView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        self.viewModel.onClose += self._onClose
        self.viewModel.onAffirmative += self._onClose
        self.viewModel.onInfo += self._onInfo
        self.addListener(ViewEventType.LOAD_VIEW, self.__onLobbyViewLoad, scope=EVENT_BUS_SCOPE.LOBBY)
        AccountSettings.setSettings(SHOWN_WOT_PLUS_INTRO, True)
        self._wotPlusCtrl.onIntroShown()
        self._wotPlusLogger.onViewInitialize()

    def _finalize(self):
        self.viewModel.onClose -= self._onClose
        self.viewModel.onAffirmative -= self._onClose
        self.viewModel.onInfo -= self._onInfo
        self.removeListener(ViewEventType.LOAD_VIEW, self.__onLobbyViewLoad, scope=EVENT_BUS_SCOPE.LOBBY)
        self._wotPlusLogger.onViewFinalize()

    def _onClose(self):
        self._wotPlusLogger.logCloseEvent()
        self.destroyWindow()

    def _onInfo(self):
        showWotPlusInfoPage(WotPlusInfoPageSource.ATTENDANCE_REWARDS_SCREEN)

    def __onLobbyViewLoad(self, event):
        if event.alias in LobbyHeader.TABS.ALL():
            self.destroyWindow()
