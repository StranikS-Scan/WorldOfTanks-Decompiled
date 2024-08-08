# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wot_anniversary/welcome_view.py
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core.settings_constants import WotAnniversaryStorageKeys
from constants import IS_CHINA
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wot_anniversary.welcome_view_model import WelcomeViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.wot_anniversary.sound import WOT_ANNIVERSARY_WELCOME_WINDOW_SOUND
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.wot_anniversary import IWotAnniversaryController
from wot_anniversary_common import WotAnniversaryUrls

class WotAnniversaryWelcomeView(ViewImpl):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __wotAnniversaryCtrl = dependency.descriptor(IWotAnniversaryController)
    _COMMON_SOUND_SPACE = WOT_ANNIVERSARY_WELCOME_WINDOW_SOUND

    def __init__(self):
        settings = ViewSettings(R.views.lobby.wot_anniversary.WelcomeScreen())
        settings.flags = ViewFlags.VIEW
        settings.model = WelcomeViewModel()
        super(WotAnniversaryWelcomeView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WotAnniversaryWelcomeView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        self.__markVisited()

    def _onLoading(self, *args, **kwargs):
        super(WotAnniversaryWelcomeView, self)._onLoading(*args, **kwargs)
        self.__fillModel()

    def _getEvents(self):
        return ((self.__wotAnniversaryCtrl.onSettingsChanged, self.__onSettingsChanged),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.onAccept, self.__onClose),
         (self.viewModel.onPlay, self.__showWelcomeOverlayVideo))

    def __onClose(self):
        self.destroyWindow()

    def __showWelcomeOverlayVideo(self):
        showBrowserOverlayView(self.__wotAnniversaryCtrl.getUrl(WotAnniversaryUrls.WELCOME_VIDEO), VIEW_ALIAS.BROWSER_OVERLAY)
        self.destroyWindow()

    def __markVisited(self):
        self.__settingsCore.serverSettings.setSectionSettings(SETTINGS_SECTIONS.WOT_ANNIVERSARY_STORAGE, {WotAnniversaryStorageKeys.WOT_ANNIVERSARY_WELCOME_SHOWED: True})

    def __fillModel(self):
        config = self.__wotAnniversaryCtrl.getConfig()
        with self.viewModel.transaction() as tx:
            tx.setStartTime(config.startTime)
            tx.setEndTime(config.activePhaseEndTime)
            tx.setIsChina(IS_CHINA)

    def __onSettingsChanged(self):
        if not self.__wotAnniversaryCtrl.isAvailableAndActivePhase():
            self.destroyWindow()


class WotAnniversaryWelcomeWindow(LobbyNotificationWindow):

    def __init__(self, parent=None):
        super(WotAnniversaryWelcomeWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.FULLSCREEN_WINDOW, content=WotAnniversaryWelcomeView(), parent=parent)

    def isParamsEqual(self, *args):
        return True
