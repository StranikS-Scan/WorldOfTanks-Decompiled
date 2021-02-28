# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/offers/offers_novelty.py
import Event
from account_helpers.AccountSettings import AccountSettings, VIEWED_OFFERS
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersNovelty, IOffersDataProvider

class OffersNovelty(IOffersNovelty):
    _offersProvider = dependency.descriptor(IOffersDataProvider)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _connMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        self.onUpdated = Event.Event()
        self.__newOffers = set()

    def init(self):
        self._offersProvider.onOffersUpdated += self.__updateNovelty
        self._connMgr.onConnected += self._onConnected
        self._lobbyContext.onServerSettingsChanged += self._onServerSettingsChanged
        self._serverSettings.onServerSettingsChange += self.__updateNovelty
        self.__updateNovelty()

    def fini(self):
        self._offersProvider.onOffersUpdated -= self.__updateNovelty
        self._connMgr.onConnected -= self._onConnected
        self._lobbyContext.onServerSettingsChanged -= self._onServerSettingsChanged
        self._serverSettings.onServerSettingsChange -= self.__updateNovelty

    def setAsSeen(self):
        if self.__newOffers:
            viewedOffers = self.__getViewedOffers()
            viewedOffers.update(self.__newOffers)
            self.__newOffers.clear()
            self.__setViewedOffers(viewedOffers)
            self.onUpdated()

    def saveAsSeen(self, offerId):
        if offerId in self.__newOffers:
            viewedOffers = self.__getViewedOffers()
            viewedOffers.add(offerId)
            self.__newOffers.remove(offerId)
            self.__setViewedOffers(viewedOffers)
            self.onUpdated()

    @property
    def showNovelty(self):
        return bool(self.__newOffers)

    @property
    def noveltyCount(self):
        return len(self.__newOffers)

    @property
    def _serverSettings(self):
        return self._lobbyContext.getServerSettings()

    def _onConnected(self, *args, **kwargs):
        self._lobbyContext.onServerSettingsChanged += self._onServerSettingsChanged

    def _onServerSettingsChanged(self, *args, **kwargs):
        self._serverSettings.onServerSettingsChange += self.__updateNovelty

    def __updateNovelty(self, *args, **kwargs):
        self.__updateNewOffers()
        if self._lobbyContext.getServerSettings().isOffersEnabled():
            self.__clearNotActiveOffers()

    def __updateNewOffers(self):
        viewedOffers = self.__getViewedOffers()
        newOffers = set((offer.id for offer in self._offersProvider.iAvailableOffers(onlyVisible=True) if offer.id not in viewedOffers))
        if newOffers != self.__newOffers:
            self.__newOffers = newOffers
            self.onUpdated()

    def __clearNotActiveOffers(self):
        if self._offersProvider.isSynced:
            viewedOffers = self.__getViewedOffers()
            availableOffers = [ offer.id for offer in self._offersProvider.getAvailableOffers(onlyVisible=True) ]
            activeViewedOffers = set((offerID for offerID in viewedOffers if offerID in availableOffers))
            if activeViewedOffers != viewedOffers:
                self.__setViewedOffers(activeViewedOffers)

    @staticmethod
    def __setViewedOffers(viewedOffers):
        AccountSettings.setNotifications(VIEWED_OFFERS, viewedOffers)

    @staticmethod
    def __getViewedOffers():
        return AccountSettings.getNotifications(VIEWED_OFFERS)
