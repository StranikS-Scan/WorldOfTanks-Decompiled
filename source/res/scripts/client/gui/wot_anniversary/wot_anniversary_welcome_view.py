# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wot_anniversary/wot_anniversary_welcome_view.py
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core.settings_constants import WotAnniversaryStorageKeys
from constants import IS_CHINA
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wot_anniversary.wot_anniversary_welcome_view_model import WotAnniversaryWelcomeViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IWotAnniversaryController
from wot_anniversary_common import WotAnniversaryUrls

class WotAnniversaryWelcomeView(ViewImpl):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __wotAnniversaryCtrl = dependency.descriptor(IWotAnniversaryController)

    def __init__(self, closeCallback=None):
        settings = ViewSettings(R.views.lobby.wot_anniversary.WelcomeScreen())
        settings.flags = ViewFlags.VIEW
        settings.model = WotAnniversaryWelcomeViewModel()
        self.__closeCallback = closeCallback
        super(WotAnniversaryWelcomeView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WotAnniversaryWelcomeView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        self.viewModel.onClose += self.__onClose
        self.viewModel.onAccept += self.__onClose
        self.viewModel.onPlay += self.__showWelcomeOverlayVideo
        self.__wotAnniversaryCtrl.onSettingsChanged += self.__onSettingsChange
        self.__markVisited()

    def _finalize(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onAccept -= self.__onClose
        self.viewModel.onPlay -= self.__showWelcomeOverlayVideo
        self.__wotAnniversaryCtrl.onSettingsChanged -= self.__onSettingsChange

    def _onLoading(self, *args, **kwargs):
        super(WotAnniversaryWelcomeView, self)._onLoading(*args, **kwargs)
        self.__fillModel()

    def __onClose(self):
        self.destroyWindow()

    def __showWelcomeOverlayVideo(self):
        parent = self.getParentWindow()
        showBrowserOverlayView(self.__wotAnniversaryCtrl.getUrl(WotAnniversaryUrls.WELCOME_VIDEO), VIEW_ALIAS.BROWSER_OVERLAY, parent=parent, callbackOnLoad=parent.sendToBack, callbackOnClose=self.destroyWindow)

    def __markVisited(self):
        if not self.__settingsCore.serverSettings.getSection(SETTINGS_SECTIONS.WOT_ANNIVERSARY_STORAGE).get(WotAnniversaryStorageKeys.WOT_ANNIVERSARY_WELCOME_SHOWED):
            self.__settingsCore.serverSettings.setSections([SETTINGS_SECTIONS.WOT_ANNIVERSARY_STORAGE], {WotAnniversaryStorageKeys.WOT_ANNIVERSARY_WELCOME_SHOWED: True})

    def __fillModel(self):
        config = self.__wotAnniversaryCtrl.getConfig()
        with self.viewModel.transaction() as tx:
            tx.setStartTime(config.startTime)
            tx.setEndTime(config.endTime)
            tx.setIsChina(IS_CHINA)

    def __onSettingsChange(self):
        if not self.__wotAnniversaryCtrl.isAvailable():
            self.destroyWindow()


class WotAnniversaryWelcomeWindow(LobbyNotificationWindow):

    def __init__(self, parent=None, closeCallback=None):
        super(WotAnniversaryWelcomeWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.FULLSCREEN_WINDOW, content=WotAnniversaryWelcomeView(closeCallback), parent=parent)

    def isParamsEqual(self, *args):
        return True
