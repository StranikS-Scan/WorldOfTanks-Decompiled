# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/Fortifications2View.py
import BigWorld
from adisp import process
from debug_utils import LOG_ERROR
from helpers import dependency
from gui.shared import events, EVENT_BUS_SCOPE
from gui.clans.clan_helpers import getStrongholdUrl
from gui.sounds.ambients import StrongholdEnv
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.meta.Fortifications2ViewMeta import Fortifications2ViewMeta
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.strongholds import createStrongholdsWebHandlers
from skeletons.gui.game_control import IBrowserController

class Fortifications2View(LobbySubView, Fortifications2ViewMeta):
    __background_alpha__ = 1.0
    __sound_env__ = StrongholdEnv
    browserCtrl = dependency.descriptor(IBrowserController)

    def __init__(self, ctx=None):
        super(Fortifications2View, self).__init__(ctx)
        self.__browser = None
        self.__hasFocus = False
        self.__browserId = 0
        return

    def onEscapePress(self):
        self.__close()

    def onFocusChange(self, hasFocus):
        self.__hasFocus = hasFocus
        self.__updateKeyHandlers()

    def viewSize(self, width, height):
        self.__loadBrowser(width, height)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(Fortifications2View, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.init(self.__browserId, createStrongholdsWebHandlers())
            viewPy.onError += self.__onError

    def _onUnregisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.onError -= self.__onError
        super(Fortifications2View, self)._onUnregisterFlashComponent(viewPy, alias)

    @process
    def __loadBrowser(self, width, height):
        strongholdsTabUrl = getStrongholdUrl('tabUrl')
        if strongholdsTabUrl is not None:
            self.__browserId = yield self.browserCtrl.load(url=strongholdsTabUrl, useBrowserWindow=False, browserSize=(width, height), showBrowserCallback=self.__showBrowser)
            self.__browser = self.browserCtrl.getBrowser(self.__browserId)
            if self.__browser:
                self.__browser.allowRightClick = True
                self.__browser.useSpecialKeys = False
            self.__updateKeyHandlers()
        else:
            LOG_ERROR('Setting "StrongholdsTabUrl" missing!')
        return

    def _populate(self):
        super(Fortifications2View, self)._populate()
        self.fireEvent(events.StrongholdEvent(events.StrongholdEvent.STRONGHOLD_ACTIVATED), scope=EVENT_BUS_SCOPE.FORT)

    def _dispose(self):
        super(Fortifications2View, self)._dispose()
        self.fireEvent(events.StrongholdEvent(events.StrongholdEvent.STRONGHOLD_DEACTIVATED), scope=EVENT_BUS_SCOPE.FORT)

    def __close(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def __updateKeyHandlers(self):
        if self.__browser is not None:
            self.__browser.skipEscape = not self.__hasFocus
            self.__browser.ignoreKeyEvents = not self.__hasFocus
        return

    def __onError(self):
        self.fireEvent(events.StrongholdEvent(events.StrongholdEvent.STRONGHOLD_DATA_UNAVAILABLE), scope=EVENT_BUS_SCOPE.FORT)

    def __showBrowser(self):
        BigWorld.callback(0.01, self.as_loadBrowserS)
