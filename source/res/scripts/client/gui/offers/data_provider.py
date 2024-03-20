# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/offers/data_provider.py
import logging
from functools import wraps
import typing
import adisp
from Event import Event, EventManager
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import OFFERS_DISABLED_MSG_SEEN
from account_helpers.offers import events_data
from account_helpers.offers.cache import CdnResourcesCache
from constants import EVENT_CLIENT_DATA, OFFERS_ENABLED_KEY, OFFER_TOKEN_PREFIX
from gui import SystemMessages
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.SystemMessages import SM_TYPE
from gui.server_events.events_helpers import getEventsData
from gui.shared.gui_items.processors import makeI18nError
from gui.shared.utils.requesters.offers_requester import OffersRequester
from helpers import dependency, isPlayerAccount
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.shared import IItemsCache
from web.cache.web_cache import CachePrefetchResult
if typing.TYPE_CHECKING:
    from typing import Callable, Optional, Set, Union
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
    _connMgr = dependency.descriptor(IConnectionManager)
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self._em = EventManager()
        self._states = OffersRequester()
        self._ready = False
        self._pendingNotify = False
        self._cache = {}
        self._lastAvailableOffers = None
        self._cdnCache = CdnResourcesCache()
        self._getOffersData = None
        self.onOffersUpdated = Event(self._em)
        return

    def init(self):
        self._getOffersData = _getEventsOffersData
        g_playerEvents.onAccountBecomeNonPlayer += self.stop
        self._connMgr.onConnected += self._onConnected
        self._connMgr.onDisconnected += self._onDisconnected
        self._lobbyContext.onServerSettingsChanged += self._onServerSettingsChanged
        self._lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange

    def fini(self):
        self._getOffersData = None
        g_playerEvents.onAccountBecomeNonPlayer -= self.stop
        self._connMgr.onConnected -= self._onConnected
        self._connMgr.onDisconnected -= self._onDisconnected
        self._lobbyContext.onServerSettingsChanged -= self._onServerSettingsChanged
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        self._em.clear()
        return

    def start(self):
        self._ready = True
        _logger.debug('[Offers provider] ready to notify')
        self._notify()

    def stop(self):
        self._ready = False
        _logger.debug('[Offers provider] not ready to notify')

    def update(self, diff):
        changed = any((token.startswith(OFFER_TOKEN_PREFIX) for token in diff.get('tokens', {}))) or 'offersData' in diff or 'eventsData' in diff and EVENT_CLIENT_DATA.OFFER in diff['eventsData'] or 'serverSettings' in diff and OFFERS_ENABLED_KEY in diff['serverSettings']
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
    @adisp.adisp_async
    def isCdnResourcesReady(self, callback=None, timeout=_CDN_SYNC_TIMEOUT):
        _logger.debug('[Offers provider] CDN resources cache ready check')
        self._cdnCache.sync(callback=callback, timeout=timeout)

    def getCdnResourcePath(self, cdnRelativePath, relative=True):
        return self._cdnCache.get(cdnRelativePath, relative=relative)

    @_ifFeatureDisabled(None)
    @_ifNotSynced(None)
    def getOffer(self, offerID):
        offerData = self._getOffersData().get(offerID)
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
    def iAvailableOffers(self, onlyVisible=True):
        for offer in self._ioffers():
            if offer.isOfferAvailable:
                if onlyVisible and not offer.showInGUI:
                    continue
                yield offer

    def getAvailableOffers(self, onlyVisible=True):
        return list(self.iAvailableOffers(onlyVisible))

    def getAvailableOffersByToken(self, token):
        return list(self.__iAvailableOffersByToken(token))

    def isOfferAvailable(self, tokenID):
        for offer in self.iAvailableOffers():
            if offer.token == tokenID:
                return True

        return False

    @_ifFeatureDisabled(())
    @_ifNotSynced(())
    def iUnlockedOffers(self, onlyVisible=True, includeAllOffers=True):
        for offer in self._ioffers():
            if onlyVisible and not offer.showInGUI:
                continue
            if includeAllOffers:
                if offer.isOfferUnlocked:
                    yield offer
            if offer.showWhenZeroCurrency:
                if offer.isOfferUnlocked:
                    yield offer
            if offer.isOfferAvailable:
                yield offer

    def getUnlockedOffers(self, onlyVisible=True, includeAllOffers=True):
        return list(self.iUnlockedOffers(onlyVisible, includeAllOffers))

    def isOfferUnlocked(self, tokenID):
        for offer in self.iUnlockedOffers():
            if offer.token == tokenID:
                return True

        return False

    def getAmountOfGiftsGenerated(self, tokenID, mainTokenCount):
        offerData = self.getOfferByToken(tokenID)
        if offerData is not None:
            if mainTokenCount > 1:
                return offerData.giftTokenCount
            return offerData.giftTokenCount * mainTokenCount
        else:
            return 0

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
    @adisp.adisp_process
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
            if not AccountSettings.getNotifications(OFFERS_DISABLED_MSG_SEEN) and self._getOffersData():
                AccountSettings.setNotifications(OFFERS_DISABLED_MSG_SEEN, True)
                msg = makeI18nError('offers/switch_off/body')
                SystemMessages.pushMessage(msg.userMsg, msg.sysMsgType)
        elif AccountSettings.getNotifications(OFFERS_DISABLED_MSG_SEEN):
            AccountSettings.setNotifications(OFFERS_DISABLED_MSG_SEEN, False)

    def _ioffers(self):
        for offerID, data in self._getOffersData().iteritems():
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
            if offer.token == token and offer.isOfferAvailable:
                yield offer
