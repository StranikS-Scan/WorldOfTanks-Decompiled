# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/offers/data_provider.py
import logging
from functools import wraps
import typing
import adisp
from account_helpers import AccountSettings
from account_helpers.AccountSettings import OFFERS_DISABLED_MSG_SEEN
from account_helpers.offers import events_data
from account_helpers.offers.cache import CdnResourcesCache, CachePrefetchResult
from gui import SystemMessages
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.SystemMessages import SM_TYPE
from gui.server_events.events_helpers import getEventsData
from gui.shared.gui_items.processors import makeI18nError
from helpers import dependency, isPlayerAccount
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersDataProvider
from gui.shared.utils.requesters.offers_requester import OffersRequester
from constants import OFFER_TOKEN_PREFIX, EVENT_CLIENT_DATA
from Event import Event, EventManager
from PlayerEvents import g_playerEvents
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_CDN_SYNC_TIMEOUT = 60.0

def _getEventsOffersData():
    data = getEventsData(EVENT_CLIENT_DATA.OFFER)
    return data if data is not None else {}


def _ifFeatureDisabled(result):

    def inner(function):

        @wraps(function)
        def wrapper(*args, **kwargs):
            _lobby = dependency.instance(ILobbyContext)
            if not _lobby.getServerSettings().isOffersEnabled():
                _logger.debug('[Offers] feature disabled.')
                return result
            return function(*args, **kwargs)

        return wrapper

    return inner


def _ifNotSynced(result):

    def inner(function):

        @wraps(function)
        def wrapper(self, *args, **kwargs):
            if not self.isSynced:
                _logger.debug('[Offers] items not synced.')
                return result
            return function(self, *args, **kwargs)

        return wrapper

    return inner


class OffersDataProvider(IOffersDataProvider):
    _itemsCache = dependency.descriptor(IItemsCache)
    _connMgr = dependency.descriptor(IConnectionManager)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self._em = EventManager()
        self._states = OffersRequester()
        self._ready = False
        self._pendingNotify = False
        self._cache = {}
        self._lastAvailableOffers = None
        self._cdnCache = CdnResourcesCache()
        self.onOffersUpdated = Event(self._em)
        return

    def init(self):
        g_playerEvents.onAccountBecomeNonPlayer += self.stop
        self._connMgr.onConnected += self._onConnected
        self._connMgr.onDisconnected += self._onDisconnected
        self._lobbyContext.onServerSettingsChanged += self._onServerSettingsChanged
        self._lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange

    def fini(self):
        g_playerEvents.onAccountBecomeNonPlayer -= self.stop
        self._connMgr.onConnected -= self._onConnected
        self._connMgr.onDisconnected -= self._onDisconnected
        self._lobbyContext.onServerSettingsChanged -= self._onServerSettingsChanged
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        self._em.clear()

    def start(self):
        self._ready = True
        _logger.debug('[Offers provider] ready to notify')
        self._notify()

    def stop(self):
        self._ready = False
        _logger.debug('[Offers provider] not ready to notify')

    def update(self, diff):
        changed = any((token.startswith(OFFER_TOKEN_PREFIX) for token in diff.get('tokens', {}))) or 'offersData' in diff or 'eventsData' in diff and EVENT_CLIENT_DATA.OFFER in diff['eventsData'] or 'serverSettings' in diff and 'isOffersEnabled' in diff['serverSettings']
        if changed:
            self._pendingNotify = True
            self._cache.clear()
            _logger.debug('[Offers provider] changed, pending notification')
            self._notify()

    @property
    def isSynced(self):
        return self._states.isSynced() and self._itemsCache.items.tokens.isSynced()

    @_ifFeatureDisabled(None)
    @_ifNotSynced(None)
    def getReceivedGifts(self, offerID):
        return self._states.getReceivedGifts(offerID)

    @_ifFeatureDisabled(True)
    @_ifNotSynced(True)
    def isBannerSeen(self, offerID):
        return self._states.isBannerSeen(offerID)

    @_ifFeatureDisabled(lambda callback: callback(CachePrefetchResult.CLOSED))
    @_ifNotSynced(lambda callback: callback(CachePrefetchResult.CLOSED))
    @adisp.async
    def isCdnResourcesReady(self, callback=None, timeout=_CDN_SYNC_TIMEOUT):
        _logger.debug('[Offers provider] CDN resources cache ready check')
        self._cdnCache.sync(callback=callback, timeout=timeout)

    def getCdnResourcePath(self, cdnRelativePath, relative=True):
        return self._cdnCache.get(cdnRelativePath, relative=relative)

    @_ifFeatureDisabled(None)
    @_ifNotSynced(None)
    def getOffer(self, offerID):
        offerData = _getEventsOffersData().get(offerID)
        return self._makeOffer(offerID, offerData)

    @_ifFeatureDisabled(None)
    @_ifNotSynced(None)
    def getOfferByToken(self, token):
        for offer in self._ioffers():
            if offer.token == token:
                return offer

        return None

    @_ifFeatureDisabled(())
    @_ifNotSynced(())
    def iAvailableOffers(self):
        for offer in self._ioffers():
            if offer.isOfferAvailable:
                yield offer

    def getAvailableOffers(self):
        return list(self.iAvailableOffers())

    def getAvailableOffersByToken(self, token):
        return list(self.__iAvailableOffersByToken(token))

    def _onDisconnected(self):
        self.stop()
        self._pendingNotify = False
        self._lastAvailableOffers = None
        self._cache.clear()
        self._states.clear()
        self._cdnCache.destroy()
        _logger.debug('[Offers provider] closed')
        return

    @_ifFeatureDisabled(None)
    @_ifNotSynced(None)
    def _makeOffer(self, offerID, offerData):
        if offerData:
            if offerID in self._cache:
                return self._cache[offerID]
            self._cache[offerID] = events_data.OfferEventData(offerID, offerData)
            return self._cache[offerID]

    @property
    def _readyToNotify(self):
        return self._pendingNotify and self._ready and isPlayerAccount()

    @_ifFeatureDisabled(None)
    @adisp.process
    def _notify(self):
        if self._readyToNotify:
            yield self._states.request()
            if self._readyToNotify and self.isSynced:
                self._cache.clear()
                self._checkAvailableOffersChanged()
                self._cdnCache.restart()
                self._pendingNotify = False
                _logger.debug('[Offers provider] send notification')
                self.onOffersUpdated()
                return
        _logger.debug('[Offers provider] can not send notification')

    def _onConnected(self, *args, **kwargs):
        self._lobbyContext.onServerSettingsChanged += self._onServerSettingsChanged

    def _onServerSettingsChanged(self, *args, **kwargs):
        self._lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange

    def _onServerSettingsChange(self, *args, **kwargs):
        if not self._lobbyContext.getServerSettings().isOffersEnabled():
            if not AccountSettings.getNotifications(OFFERS_DISABLED_MSG_SEEN) and _getEventsOffersData():
                AccountSettings.setNotifications(OFFERS_DISABLED_MSG_SEEN, True)
                msg = makeI18nError('offers/switch_off/body')
                SystemMessages.pushMessage(msg.userMsg, msg.sysMsgType)
        elif AccountSettings.getNotifications(OFFERS_DISABLED_MSG_SEEN):
            AccountSettings.setNotifications(OFFERS_DISABLED_MSG_SEEN, False)

    def _ioffers(self):
        for offerID, data in _getEventsOffersData().iteritems():
            offer = self._makeOffer(offerID, data)
            if offer:
                yield offer

    @_ifFeatureDisabled(None)
    @_ifNotSynced(None)
    def _checkAvailableOffersChanged(self):
        if self._lastAvailableOffers is not None:
            availableOffers = {offer.id for offer in self._ioffers() if self._itemsCache.items.tokens.getToken(offer.token)}
            missing = len(self._lastAvailableOffers - availableOffers)
            if missing:
                if missing == 1:
                    msgKey = SYSTEM_MESSAGES.OFFERS_UNAVAILABLE_ONE
                    kwargs = {}
                else:
                    msgKey = SYSTEM_MESSAGES.OFFERS_UNAVAILABLE_MANY
                    kwargs = {'count': missing}
                SystemMessages.pushI18nMessage(msgKey, type=SM_TYPE.Warning, **kwargs)
        self._lastAvailableOffers = set((offer.id for offer in self.iAvailableOffers()))
        return

    @_ifFeatureDisabled(())
    @_ifNotSynced(())
    def __iAvailableOffersByToken(self, token):
        for offer in self._ioffers():
            if offer.isOfferAvailable and offer.token == token:
                yield offer
