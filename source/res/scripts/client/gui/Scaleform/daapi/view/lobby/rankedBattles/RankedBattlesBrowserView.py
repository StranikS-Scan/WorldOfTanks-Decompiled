# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/RankedBattlesBrowserView.py
import BigWorld
from adisp import process
from debug_utils import LOG_ERROR
from gui.ranked_battles.ranked_helpers import getRankedBattlesUrl
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.RankedBattlesBrowserViewMeta import RankedBattlesBrowserViewMeta
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.game_control import IBrowserController
from web_client_api.ranked_battles import createRankedBattlesWebHandlers

class RankedBattlesBrowserView(RankedBattlesBrowserViewMeta):
    browserCtrl = dependency.descriptor(IBrowserController)

    def __init__(self, ctx=None):
        super(RankedBattlesBrowserView, self).__init__(ctx)
        self.__browserId = 0
        self.__ctx = ctx
        self.__hasFocus = False
        self.__browser = None
        return

    def onFocusChange(self, hasFocus):
        self.__hasFocus = hasFocus
        self.__updateSkipEscape()

    def onEscapePress(self):
        self.onCloseView()

    def onCloseBtnClick(self):
        self.onCloseView()

    def onCloseView(self):
        ctx = self.__ctx
        returnAlias = ctx.get('returnAlias', VIEW_ALIAS.LOBBY_HANGAR) if ctx else VIEW_ALIAS.LOBBY_HANGAR
        self.fireEvent(events.LoadViewEvent(returnAlias, ctx=ctx), EVENT_BUS_SCOPE.LOBBY)

    def viewSize(self, width, height):
        self.__loadBrowser(width, height)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(RankedBattlesBrowserView, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.init(self.__browserId, createRankedBattlesWebHandlers(ctx=self.__ctx), alias=self.alias)

    @process
    def __loadBrowser(self, width, height):
        rankedBattlesUrl = getRankedBattlesUrl()
        if rankedBattlesUrl is not None:
            self.__browserId = yield self.browserCtrl.load(url=rankedBattlesUrl, useBrowserWindow=False, showBrowserCallback=self.__showBrowser, browserSize=(width, height))
            browser = self.browserCtrl.getBrowser(self.__browserId)
            if browser:
                browser.useSpecialKeys = False
                browser.allowRightClick = True
                self.__browser = browser
                self.__updateSkipEscape()
            else:
                LOG_ERROR('Failed to create browser!')
        else:
            LOG_ERROR('Server setting "wg/rankedBattles/rblbHostUrl" is missing!')
        return

    def __showBrowser(self):
        BigWorld.callback(0.01, self.as_loadBrowserS)

    def __updateSkipEscape(self):
        if self.__browser is not None:
            self.__browser.skipEscape = not self.__hasFocus
        return
