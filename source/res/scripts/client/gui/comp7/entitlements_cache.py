# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/comp7/entitlements_cache.py
import logging
from enum import Enum
import Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import COMP7_ENTITLEMENTS, COMP7_ENTITLEMENTS_TIMESTAMP, COMP7_ENTITLEMENTS_BALANCE
from gui.entitlements.entitlements_requester import EntitlementsRequester
from helpers import dependency
from helpers.time_utils import ONE_DAY, getServerUTCTime
from skeletons.gui.lobby_context import ILobbyContext
from wg_async import wg_async, await_callback
_logger = logging.getLogger(__name__)

class CacheStatus(Enum):
    IDLE = 'idle'
    PENDING = 'pending'
    DATA_READY = 'data_ready'
    ERROR = 'error'


class EntitlementsCache(object):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__requester = EntitlementsRequester()
        self.__entitlements = None
        self.__status = CacheStatus.IDLE
        self.onCacheUpdated = Event.Event()
        return

    def reset(self):
        self.__requester.clear()
        self.__entitlements = None
        self.__status = CacheStatus.IDLE
        return

    def clear(self):
        self.reset()
        self.__requester = None
        self.__status = None
        return

    def getEntitlementCount(self, entitlementName):
        if self.__shouldBeUpdated():
            self.update()
        return self.__entitlements.get(entitlementName)

    @wg_async
    def update(self, retryTimes=None, force=False):
        if self.__status == CacheStatus.PENDING and not force:
            return
        if not self.__shouldBeUpdated(force):
            self.__setStatus(CacheStatus.IDLE)
            return
        entitlements = list(self.__getCacheEntitlements())
        if not entitlements:
            self.__clearCache()
            self.__setStatus(CacheStatus.IDLE)
            return
        self.__setStatus(CacheStatus.PENDING)
        try:
            isSuccess, result = yield await_callback(self.__requester.requestByCodes)(entitlements, retryTimes)
            if isSuccess:
                balance = {ent:result.get(ent, {}).get('amount', 0) for ent in entitlements}
                comp7Entitlements = {COMP7_ENTITLEMENTS_TIMESTAMP: getServerUTCTime(),
                 COMP7_ENTITLEMENTS_BALANCE: balance}
                AccountSettings.setSettings(COMP7_ENTITLEMENTS, comp7Entitlements)
                self.__entitlements = balance
                self.__setStatus(CacheStatus.DATA_READY)
            else:
                _logger.error('Failed to update comp7 entitlements cache through agate')
                self.__setStatus(CacheStatus.ERROR)
        except Exception as e:
            logging.error('An exception has occurred while updating entitlements cache: %s', e)
            self.__setStatus(CacheStatus.ERROR)

    def __shouldBeUpdated(self, force=False):
        if self.__entitlements is None:
            self.__entitlements = self.__getPlayerEntitlements()
        return self.__isExpired() or force

    def __getPlayerEntitlements(self):
        return AccountSettings.getSettings(COMP7_ENTITLEMENTS).get(COMP7_ENTITLEMENTS_BALANCE, {})

    def __isExpired(self):
        currentTimestamp = getServerUTCTime()
        isTimeExpired = currentTimestamp > self.__getCacheTimestamp() + self.__getExpiryTime()
        isEntitlementsListChanged = set(self.__entitlements.keys()) != self.__getCacheEntitlements()
        return isTimeExpired or isEntitlementsListChanged

    def __setStatus(self, status):
        self.__status = status
        self.onCacheUpdated(status)

    def __getExpiryTime(self):
        return ONE_DAY * self.__getCacheTTL()

    def __getCacheEntitlements(self):
        return self.__getCacheConfig().get('entitlements', set())

    def __getCacheTTL(self):
        return self.__getCacheConfig().get('TTL', 0)

    def __getCacheConfig(self):
        return self.__lobbyContext.getServerSettings().comp7Config.clientEntitlementsCache

    def __clearCache(self):
        self.__entitlements.clear()
        AccountSettings.setSettings(COMP7_ENTITLEMENTS, {})

    def __getCacheTimestamp(self):
        return AccountSettings.getSettings(COMP7_ENTITLEMENTS).get(COMP7_ENTITLEMENTS_TIMESTAMP, 0)
