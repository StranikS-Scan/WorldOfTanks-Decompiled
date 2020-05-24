# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_browser_pages.py
from helpers import dependency
from gui.Scaleform.daapi.view.lobby.components.browser_view_page import BrowserPageComponent
from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_page import IResetablePage
from gui.ranked_battles.ranked_helpers import getRankedBattlesRatingUrl, getRankedBattlesInfoPageUrl
from skeletons.gui.game_control import IRankedBattlesController
from web.web_client_api.ranked_battles import createRankedBattlesWebHandlers

class RankedBrowserPage(BrowserPageComponent, IResetablePage):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self):
        super(RankedBrowserPage, self).__init__()
        self.__ctx = self.__rankedController.getWebOpenPageCtx()
        self.__isInited = False

    def reset(self):
        self._updateSounds(self.__rankedController.getSoundManager())
        ctx = self.__rankedController.getWebOpenPageCtx()
        if ctx is not None and ctx.get('webParams', '') and self.__isInited:
            self.__ctx = ctx
            self.invalidateUrl()
            self.__ctx = None
        return

    def _getWebHandlers(self):
        return createRankedBattlesWebHandlers()

    def _getUrl(self):
        url = self._getBaseUrl() + self.__patchUrlByCtx()
        self.__isInited = True
        return url

    def _getBaseUrl(self):
        raise NotImplementedError

    def _updateSounds(self, soundManager):
        pass

    def __patchUrlByCtx(self):
        return self.__ctx.get('webParams', '') if self.__ctx is not None else ''


class RankedRatingPage(RankedBrowserPage):

    def _getBaseUrl(self):
        return getRankedBattlesRatingUrl()

    @classmethod
    def _isRightClickAllowed(cls):
        return True


class RankedBattlesInfoPage(RankedBrowserPage):

    def _getBaseUrl(self):
        return getRankedBattlesInfoPageUrl()
