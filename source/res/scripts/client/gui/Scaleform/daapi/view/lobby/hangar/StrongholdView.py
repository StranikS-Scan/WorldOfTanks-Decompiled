# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/StrongholdView.py
from typing import TYPE_CHECKING
import BigWorld
from adisp import adisp_process
from debug_utils import LOG_ERROR
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers import dependency
from gui.shared import events, EVENT_BUS_SCOPE
from gui.clans.clan_helpers import getStrongholdUrl
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from gui.Scaleform.daapi.view.meta.StrongholdViewMeta import StrongholdViewMeta
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.strongholds.web_handlers import createStrongholdsWebHandlers
from gui.Scaleform.daapi.view.lobby.strongholds.sound_constants import STRONGHOLD_SOUND_SPACE, STRONGHOLD_ADS_SOUND_SPACE
from skeletons.gui.game_control import IBrowserController
if TYPE_CHECKING:
    from typing import Optional, Dict

class StrongholdView(LobbySubView, StrongholdViewMeta):
    __background_alpha__ = 1.0
    _COMMON_SOUND_SPACE = STRONGHOLD_SOUND_SPACE
    browserCtrl = dependency.descriptor(IBrowserController)

    def __init__(self, ctx=None):
        super(StrongholdView, self).__init__(ctx)
        self.__browser = None
        self.__hasFocus = False
        self.__browserId = 0
        self.__url = ctx.get('url', getStrongholdUrl()) if ctx is not None else getStrongholdUrl()
        return

    def onEscapePress(self):
        self.__close()

    def onFocusChange(self, hasFocus):
        self.__hasFocus = hasFocus
        self.__updateSkipEscape(not hasFocus)

    def viewSize(self, width, height):
        self.__loadBrowser(width, height)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(StrongholdView, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.init(self.__browserId, createStrongholdsWebHandlers())
            viewPy.onError += self.__onError

    def _onUnregisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.onError -= self.__onError
        super(StrongholdView, self)._onUnregisterFlashComponent(viewPy, alias)

    @adisp_process
    def __loadBrowser(self, width, height):
        if self.__url:
            self.__browserId = yield self.browserCtrl.load(url=self.__url, useBrowserWindow=False, browserSize=(width, height), showBrowserCallback=self.__showBrowser)
            self.__browser = self.browserCtrl.getBrowser(self.__browserId)
            if self.__browser:
                self.__browser.allowRightClick = True
                self.__browser.useSpecialKeys = False
            self.__updateSkipEscape(not self.__hasFocus)
        else:
            LOG_ERROR('Setting "StrongholdsTabUrl" missing!')

    def _populate(self):
        super(StrongholdView, self)._populate()
        self.fireEvent(events.StrongholdEvent(events.StrongholdEvent.STRONGHOLD_ACTIVATED), scope=EVENT_BUS_SCOPE.STRONGHOLD)

    def _dispose(self):
        super(StrongholdView, self)._dispose()
        if self.__browserId:
            self.browserCtrl.delBrowser(self.__browserId)
        self.fireEvent(events.StrongholdEvent(events.StrongholdEvent.STRONGHOLD_DEACTIVATED), scope=EVENT_BUS_SCOPE.STRONGHOLD)

    def __close(self):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)

    def __updateSkipEscape(self, skipEscape):
        if self.__browser is not None:
            self.__browser.skipEscape = skipEscape
            self.__browser.ignoreKeyEvents = skipEscape
        return

    def __onError(self):
        self.__updateSkipEscape(True)
        self.fireEvent(events.StrongholdEvent(events.StrongholdEvent.STRONGHOLD_DATA_UNAVAILABLE), scope=EVENT_BUS_SCOPE.STRONGHOLD)

    def __showBrowser(self):
        BigWorld.callback(0.01, self.as_loadBrowserS)
        self.fireEvent(events.StrongholdEvent(events.StrongholdEvent.STRONGHOLD_LOADED, {'browserID': self.__browserId}), scope=EVENT_BUS_SCOPE.STRONGHOLD)


class StrongholdAdsView(WebView):
    _COMMON_SOUND_SPACE = STRONGHOLD_ADS_SOUND_SPACE

    def webHandlers(self):
        return createStrongholdsWebHandlers()
