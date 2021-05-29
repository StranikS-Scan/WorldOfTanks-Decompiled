# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_browser_pages.py
from helpers import dependency
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.components.browser_view_page import BrowserPageComponent
from gui.Scaleform.daapi.view.lobby.hangar.BrowserView import BrowserView
from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_page import IResetablePage
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from gui.ranked_battles.constants import SeasonResultTokenPatterns
from gui.ranked_battles.ranked_helpers import getRankedBattlesSeasonRatingUrl, getRankedBattlesInfoPageUrl, getRankedBattlesSeasonGapUrl, getRankedBattlesYearRatingUrl, getRankedBattlesShopUrl
from gui.ranked_battles.ranked_helpers.sound_manager import RANKED_MAIN_PAGE_SOUND_SPACE, RANKED_OVERLAY_SOUND_SPACE, Sounds, AmbientType
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
        if self.__isInited:
            if ctx is not None and (ctx.get('webParams', '') or ctx.get('clientParams', {})):
                self.__ctx = ctx
                self.invalidateUrl()
            elif self._isForcedRefresh() or self._wasError:
                self.refreshUrl()
        return

    def _isForcedRefresh(self):
        return False

    def _getWebHandlers(self):
        return createRankedBattlesWebHandlers()

    def _getUrl(self):
        url = self._getBaseUrl(**self.__getClientParams()) + self.__patchUrlByCtx()
        self.__isInited = True
        self.__ctx = None
        return url

    def _getBaseUrl(self, **kwargs):
        raise NotImplementedError

    def _updateSounds(self, soundManager):
        pass

    def __getClientParams(self):
        return self.__ctx.get('clientParams', {}) if self.__ctx is not None else {}

    def __patchUrlByCtx(self):
        return self.__ctx.get('webParams', '') if self.__ctx is not None else ''


class RankedSeasonGapPage(RankedBrowserPage):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self):
        super(RankedSeasonGapPage, self).__init__()
        self.__previousSeasonID = 0

    def _populate(self):
        super(RankedSeasonGapPage, self)._populate()
        previousSeason = self.__rankedController.getPreviousSeason()
        self.__previousSeasonID = previousSeason.getSeasonID() if previousSeason else self.__previousSeasonID
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__rankedController.onUpdated += self.refreshUrl

    def _dispose(self):
        self.__rankedController.onUpdated -= self.refreshUrl
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(RankedSeasonGapPage, self)._dispose()

    def _getBaseUrl(self, **kwargs):
        return getRankedBattlesSeasonGapUrl(**kwargs)

    def __onTokensUpdate(self, diff):
        for pattern in SeasonResultTokenPatterns.ALL():
            if pattern.format(self.__previousSeasonID) in diff:
                self.refreshUrl()


class RankedShopPage(RankedBrowserPage):

    def _isForcedRefresh(self):
        return True

    def _getBaseUrl(self, **kwargs):
        return getRankedBattlesShopUrl(**kwargs)

    def _updateSounds(self, soundManager):
        soundManager.setCustomProgressSound(Sounds.PROGRESSION_STATE_SHOP)
        soundManager.setAmbient(AmbientType.HANGAR)


class RankedRatingPage(RankedBrowserPage):

    def _getBaseUrl(self, **kwargs):
        return getRankedBattlesSeasonRatingUrl(**kwargs)

    @classmethod
    def _isRightClickAllowed(cls):
        return True


class RankedYearRatingPage(RankedBrowserPage):

    def _getBaseUrl(self, **kwargs):
        return getRankedBattlesYearRatingUrl(**kwargs)

    def _updateSounds(self, soundManager):
        soundManager.setProgressSound()


class RankedBattlesInfoPage(RankedBrowserPage):

    def _getBaseUrl(self, **kwargs):
        return getRankedBattlesInfoPageUrl(**kwargs)


class RankedLandingView(BrowserView):
    _COMMON_SOUND_SPACE = RANKED_MAIN_PAGE_SOUND_SPACE
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def onEscapePress(self):
        self.onCloseBtnClick()

    def _populate(self):
        super(RankedLandingView, self)._populate()
        self._populateSoundEnv(self.__rankedController.getSoundManager())
        self.__rankedController.onUpdated += self._checkDestroy

    def _dispose(self):
        self.__rankedController.onUpdated -= self._checkDestroy
        self._disposeSoundEnv(self.__rankedController.getSoundManager())
        self.__rankedController.onKillWebOverlays()
        super(RankedLandingView, self)._dispose()

    def _populateSoundEnv(self, soundManager):
        soundManager.onSoundModeChanged(True, Sounds.PROGRESSION_STATE_LEAGUES)

    def _disposeSoundEnv(self, soundManager):
        if self.__rankedController.isRankedPrbActive():
            if self.__rankedController.isAccountMastered():
                soundManager.setProgressSound()
            else:
                soundManager.setDefaultProgressSound()
        else:
            self.__rankedController.getSoundManager().onSoundModeChanged(False)

    def _checkDestroy(self):
        pass


class RankedShopLandingView(RankedLandingView):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def _populateSoundEnv(self, soundManager):
        soundManager.onSoundModeChanged(True, Sounds.PROGRESSION_STATE_SHOP)
        soundManager.setAmbient(AmbientType.HANGAR)

    def _checkDestroy(self):
        if not self.__rankedController.isRankedShopEnabled():
            self.onEscapePress()


class RankedYearLBLandingView(RankedLandingView):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def _checkDestroy(self):
        if not self.__rankedController.isYearLBEnabled():
            self.onEscapePress()


class RankedWebOverlay(WebView):
    _COMMON_SOUND_SPACE = RANKED_OVERLAY_SOUND_SPACE
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def webHandlers(self):
        return createRankedBattlesWebHandlers()

    def _populate(self):
        super(RankedWebOverlay, self)._populate()
        self.__rankedController.onKillWebOverlays += self.__destroy

    def _dispose(self):
        self.__rankedController.onKillWebOverlays -= self.__destroy
        super(RankedWebOverlay, self)._dispose()

    def __destroy(self):
        self.onEscapePress()
