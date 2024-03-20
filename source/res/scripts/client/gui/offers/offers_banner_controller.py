# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/offers/offers_banner_controller.py
import logging
import weakref
from functools import partial
import BigWorld
import Event
from adisp import adisp_process
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.app_loader.settings import APP_NAME_SPACE
from gui.impl.lobby.offers.offer_banner_window import OfferBannerWindow
from gui.limited_ui.lui_rules_storage import LuiRules
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.app_loader import GuiGlobalSpaceID, IAppLoader
from skeletons.gui.game_control import ILimitedUIController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersBannerController, IOffersDataProvider
from web.cache.web_cache import CachePrefetchResult
_logger = logging.getLogger(__name__)

class OffersBannerController(IOffersBannerController):
    _appLoader = dependency.descriptor(IAppLoader)
    _offersProvider = dependency.descriptor(IOffersDataProvider)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _connMgr = dependency.descriptor(IConnectionManager)
    __limitedUIController = dependency.descriptor(ILimitedUIController)

    def __init__(self):
        self.__sync = False
        self.onShowBanners = Event.Event()
        self.onHideBanners = Event.Event()

    @property
    def _serverSettings(self):
        return self._lobbyContext.getServerSettings()

    def isEnabled(self):
        return self._serverSettings.isOffersEnabled() and self._appLoader.getSpaceID() == GuiGlobalSpaceID.LOBBY and self.__isHangarViewLoaded

    def init(self):
        self._offersProvider.onOffersUpdated += self._loadBanners
        self._connMgr.onConnected += self._onConnected
        self._lobbyContext.onServerSettingsChanged += self._onServerSettingsChanged
        self._serverSettings.onServerSettingsChange += self._loadBanners
        self.__limitedUIController.onConfigChanged += self.__subscribeLui

    def fini(self):
        self._offersProvider.onOffersUpdated -= self._loadBanners
        self._connMgr.onConnected -= self._onConnected
        self._lobbyContext.onServerSettingsChanged -= self._onServerSettingsChanged
        self._serverSettings.onServerSettingsChange -= self._loadBanners
        self.__limitedUIController.onConfigChanged -= self.__subscribeLui
        self.__unsubscribeLui()
        self.onShowBanners.clear()
        self.onShowBanners = None
        self.onHideBanners.clear()
        self.onHideBanners = None
        return

    def __subscribeLui(self):
        self.__limitedUIController.startObserve(LuiRules.OFFER_BANNER_WINDOW, self._loadBanners)

    def __unsubscribeLui(self):
        self.__limitedUIController.stopObserve(LuiRules.OFFER_BANNER_WINDOW, self._loadBanners)

    def showBanners(self, *args, **kwargs):
        self._loadBanners()
        self.onShowBanners()

    def hideBanners(self, *args, **kwargs):
        self.onHideBanners()

    @adisp_process
    def _loadBanners(self, *args, **kwargs):
        canShow = self.__limitedUIController.isRuleCompleted(LuiRules.OFFER_BANNER_WINDOW)
        if not canShow:
            for offer in self.__iNotSeenOffers():
                _logger.debug('OfferBannerWindow for offerID=%s was hidden by limitedUIController ', offer.id)

        if self.__sync or not self.isEnabled() or not self.__hasNotSeenOffers() or not canShow:
            return
        self.__sync = True
        result = yield self._offersProvider.isCdnResourcesReady()
        self.__sync = False
        if result != CachePrefetchResult.SUCCESS or not self.isEnabled():
            return
        for offer in self.__iNotSeenOffers():
            BigWorld.callback(0.1, partial(OfferBannerWindow.tryLoad, offer.id, weakref.proxy(self)))

    def _onConnected(self, *args, **kwargs):
        self._lobbyContext.onServerSettingsChanged += self._onServerSettingsChanged

    def _onServerSettingsChanged(self, *args, **kwargs):
        self._serverSettings.onServerSettingsChange += self._loadBanners

    def __hasNotSeenOffers(self):
        return any(self.__iNotSeenOffers())

    def __iNotSeenOffers(self):
        for offer in self._offersProvider.iUnlockedOffers():
            if offer.showBanner and not self._offersProvider.isBannerSeen(offer.id) and not OfferBannerWindow.isLoaded(offer.id):
                yield offer

    @property
    def __isHangarViewLoaded(self):
        app = self._appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
        return app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_HANGAR)) is not None if app and app.containerManager else False
