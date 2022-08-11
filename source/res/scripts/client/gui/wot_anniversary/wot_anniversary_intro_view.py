# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wot_anniversary/wot_anniversary_intro_view.py
import WWISE
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core.settings_constants import WotAnniversaryStorageKeys
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wot_anniversary.wot_anniversary_intro_view_model import WotAnniversaryIntroViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IWotAnniversaryController

class WotAnniversaryIntroView(ViewImpl):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __wotAnniversaryCtrl = dependency.descriptor(IWotAnniversaryController)
    __slots__ = ('__closeCallback',)

    def __init__(self, closeCallback=None):
        settings = ViewSettings(R.views.lobby.wot_anniversary.IntroScreen())
        settings.flags = ViewFlags.VIEW
        settings.model = WotAnniversaryIntroViewModel()
        self.__closeCallback = closeCallback
        super(WotAnniversaryIntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WotAnniversaryIntroView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        self.viewModel.onClose += self.__onClose
        self.viewModel.onAccept += self.__onClose
        self.__wotAnniversaryCtrl.onSettingsChanged += self.__onSettingsChange
        self.__markVisited()

    def _finalize(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onAccept -= self.__onClose
        self.__wotAnniversaryCtrl.onSettingsChanged -= self.__onSettingsChange

    def _onLoading(self, *args, **kwargs):
        super(WotAnniversaryIntroView, self)._onLoading(*args, **kwargs)
        WWISE.WW_eventGlobal(backport.sound(R.sounds.ev_bday_12_intro()))
        self.__setEventTimes()

    def __onClose(self):
        self.destroyWindow()
        if self.__closeCallback is not None:
            self.__closeCallback()
        return

    def __markVisited(self):
        if not self.__settingsCore.serverSettings.getSection(SETTINGS_SECTIONS.WOT_ANNIVERSARY_STORAGE).get(WotAnniversaryStorageKeys.WOT_ANNIVERSARY_INTRO_SHOWED):
            self.__settingsCore.serverSettings.setSections([SETTINGS_SECTIONS.WOT_ANNIVERSARY_STORAGE], {WotAnniversaryStorageKeys.WOT_ANNIVERSARY_INTRO_SHOWED: True})

    def __setEventTimes(self):
        config = self.__wotAnniversaryCtrl.getConfig()
        with self.viewModel.transaction() as tx:
            tx.setStartTime(config.startTime)
            tx.setEndTime(config.endTime)

    def __onSettingsChange(self):
        if not self.__wotAnniversaryCtrl.isAvailable():
            self.destroyWindow()


class WotAnniversaryIntroWindow(LobbyWindow):

    def __init__(self, parent=None, closeCallback=None):
        super(WotAnniversaryIntroWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.FULLSCREEN_WINDOW, content=WotAnniversaryIntroView(closeCallback), parent=parent)
