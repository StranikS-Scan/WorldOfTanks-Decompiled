# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/EpicBattlesBrowserView.py
import BigWorld
from adisp import process
from gui import GUI_SETTINGS
from helpers import dependency
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui.shared import events, EVENT_BUS_SCOPE
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from skeletons.gui.game_control import IBrowserController
from skeletons.gui.lobby_context import ILobbyContext
from gui.Scaleform.daapi.view.meta.EpicBattlesBrowserViewMeta import EpicBattlesBrowserViewMeta

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
        self.__urlID = ctx
        return

    def onEscapePress(self):
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

    @process
    def __loadBrowser(self, width, height):
        epicBattlesUrl = getFrontlineUrl(self.__urlID)
        if epicBattlesUrl is not None:
            self.__browserId = yield self.browserCtrl.load(url=epicBattlesUrl, useBrowserWindow=False, browserSize=(width, height), showBrowserCallback=self.__showBrowser)
            self.__browser = self.browserCtrl.getBrowser(self.__browserId)
            if self.__browser:
                self.__browser.allowRightClick = True
                self.__browser.useSpecialKeys = False
            self.__updateSkipEscape(not self.__hasFocus)
        else:
            LOG_ERROR('Setting "epicBattlesUrl" missing!')
        return

    def __close(self):
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_ALIAS), scope=EVENT_BUS_SCOPE.LOBBY)

    def __updateSkipEscape(self, skipEscape):
        if self.__browser is not None:
            self.__browser.skipEscape = skipEscape
            self.__browser.ignoreKeyEvents = skipEscape
        return

    def __onError(self):
        self.__updateSkipEscape(True)

    def __showBrowser(self):
        BigWorld.callback(0.01, self.as_loadBrowserS)
