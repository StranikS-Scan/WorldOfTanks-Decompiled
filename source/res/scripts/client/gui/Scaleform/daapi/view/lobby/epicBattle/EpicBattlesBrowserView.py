# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/EpicBattlesBrowserView.py
import BigWorld
from adisp import process
from gui import GUI_SETTINGS
from helpers import dependency
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui.shared import events, EVENT_BUS_SCOPE
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from skeletons.gui.game_control import IBrowserController
from skeletons.gui.lobby_context import ILobbyContext
from gui.Scaleform.daapi.view.meta.EpicBattlesBrowserViewMeta import EpicBattlesBrowserViewMeta
from web_client_api import webApiCollection
from web_client_api.sound import SoundWebApi

def getFrontlineUrl(urlName):
    try:
        return _getFlHost() + GUI_SETTINGS.frontline.get(urlName)
    except (AttributeError, TypeError):
        LOG_CURRENT_EXCEPTION()
        return None

    return None


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _getFlHost(lobbyContext=None):
    if lobbyContext is None:
        return
    else:
        try:
            return lobbyContext.getServerSettings().frontline.flHostUrl
        except AttributeError:
            LOG_CURRENT_EXCEPTION()
            return

        return


class EpicBattlesBrowserView(LobbySubView, EpicBattlesBrowserViewMeta):
    browserCtrl = dependency.descriptor(IBrowserController)
    lobbyCtx = dependency.instance(ILobbyContext)

    def __init__(self, ctx=None):
        super(EpicBattlesBrowserView, self).__init__(ctx)
        self.__browser = None
        self.__hasFocus = False
        self.__browserId = 0
        self.__previousPage = VIEW_ALIAS.LOBBY_HANGAR
        if ctx.get('urlID') is None:
            LOG_ERROR("EpicBattlesBrowserView: urlID missing from given ctx. When opening EPICBATTLES_ALIASES.EPIC_BATTLES_BROWSER_ALIAS please always set a dictionary with 'urlID' key.")
            self.__urlID = ''
        else:
            self.__urlID = ctx['urlID']
            self.__previousPage = ctx.get('previousPage')
        return

    def onEscapePress(self):
        self.__back()

    def onCloseBtnClick(self):
        self.__close()

    def onFocusChange(self, hasFocus):
        self.__hasFocus = hasFocus
        self.__updateSkipEscape(not hasFocus)

    def viewSize(self, width, height):
        self.__loadBrowser(width, height)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(EpicBattlesBrowserView, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.init(self.__browserId, [])
            viewPy.onError += self.__onError

    def _onUnregisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.onError -= self.__onError
        super(EpicBattlesBrowserView, self)._onUnregisterFlashComponent(viewPy, alias)

    def _dispose(self):
        super(EpicBattlesBrowserView, self)._dispose()
        if self.__browserId:
            self.browserCtrl.delBrowser(self.__browserId)

    @process
    def __loadBrowser(self, width, height):
        epicBattlesUrl = getFrontlineUrl(self.__urlID)
        if epicBattlesUrl is not None:
            self.__browserId = yield self.browserCtrl.load(url=epicBattlesUrl, useBrowserWindow=False, browserSize=(width, height), showBrowserCallback=self.__showBrowser, handlers=webApiCollection(SoundWebApi))
            self.__browser = self.browserCtrl.getBrowser(self.__browserId)
            if self.__browser:
                self.__browser.allowRightClick = True
                self.__browser.useSpecialKeys = False
            self.__updateSkipEscape(not self.__hasFocus)
        else:
            LOG_ERROR('Setting "epicBattlesUrl" missing! urlID = "{}"'.format(self.__urlID))
        return

    def __close(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def __back(self):
        self.fireEvent(events.LoadViewEvent(self.__previousPage), scope=EVENT_BUS_SCOPE.LOBBY)

    def __updateSkipEscape(self, skipEscape):
        if self.__browser is not None:
            self.__browser.skipEscape = skipEscape
            self.__browser.ignoreKeyEvents = skipEscape
        return

    def __onError(self):
        self.__updateSkipEscape(True)

    def __showBrowser(self):
        BigWorld.callback(0.01, self.as_loadBrowserS)
