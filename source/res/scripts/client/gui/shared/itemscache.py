# Embedded file name: scripts/client/gui/shared/ItemsCache.py
from Event import Event
from adisp import async
from debug_utils import LOG_DEBUG
from PlayerEvents import g_playerEvents
from gui.shared.utils.requesters import ItemsRequester, REQ_CRITERIA

class CACHE_SYNC_REASON(object):
    SHOW_GUI, CLIENT_UPDATE, SHOP_RESYNC, INVENTORY_RESYNC, DOSSIER_RESYNC, STATS_RESYNC = range(1, 7)


class _ItemsCache(object):

    def __init__(self):
        self.__items = ItemsRequester()
        self.__waitForSync = False
        self.onSyncStarted = Event()
        self.onSyncCompleted = Event()

    def init(self):
        g_playerEvents.onInventoryResync += self.__pe_onInventoryResync
        g_playerEvents.onDossiersResync += self.__pe_onDossiersResync
        g_playerEvents.onStatsResync += self.__pe_onStatsResync
        g_playerEvents.onCenterIsLongDisconnected += self._onCenterIsLongDisconnected

    def fini(self):
        self.onSyncStarted.clear()
        self.onSyncCompleted.clear()
        g_playerEvents.onCenterIsLongDisconnected -= self._onCenterIsLongDisconnected
        g_playerEvents.onStatsResync -= self.__pe_onStatsResync
        g_playerEvents.onDossiersResync -= self.__pe_onDossiersResync
        g_playerEvents.onInventoryResync -= self.__pe_onInventoryResync

    @property
    def waitForSync(self):
        return self.__waitForSync

    @property
    def items(self):
        return self.__items

    @async
    def update(self, updateReason, diff = None, callback = None):
        if diff is None:
            self.__invalidateFullData(updateReason, callback)
        else:
            self.__invalidateData(updateReason, diff, callback)
        return

    def clear(self):
        LOG_DEBUG('Clearing items cache.')
        return self.items.clear()

    def _onResync(self, reason):
        if not self.__waitForSync:
            self.__invalidateFullData(reason)

    def _onCenterIsLongDisconnected(self, isLongDisconnected):
        self.items.dossiers.onCenterIsLongDisconnected(isLongDisconnected)

    def __invalidateData(self, updateReason, diff, callback = lambda *args: None):
        self.__waitForSync = True
        self.onSyncStarted()
        if updateReason != CACHE_SYNC_REASON.DOSSIER_RESYNC:
            invalidItems = self.__items.invalidateCache(diff)
        else:
            invalidItems = {}

        def cbWrapper(*args):
            self.__waitForSync = False
            self.onSyncCompleted(updateReason, invalidItems)
            callback(*args)

        self.__items.request()(cbWrapper)

    def __invalidateFullData(self, updateReason, callback = lambda *args: None):
        self.__waitForSync = True
        self.onSyncStarted()

        def cbWrapper(*args):
            self.__waitForSync = False
            if updateReason != CACHE_SYNC_REASON.DOSSIER_RESYNC:
                invalidItems = self.__items.invalidateCache()
            else:
                invalidItems = {}
            self.onSyncCompleted(updateReason, invalidItems)
            callback(*args)

        self.__items.request()(cbWrapper)

    def isSynced(self):
        return self.items.isSynced()

    def __pe_onStatsResync(self, *args):
        self._onResync(CACHE_SYNC_REASON.STATS_RESYNC)

    def __pe_onInventoryResync(self, *args):
        self._onResync(CACHE_SYNC_REASON.INVENTORY_RESYNC)

    def __pe_onDossiersResync(self, *args):
        self._onResync(CACHE_SYNC_REASON.DOSSIER_RESYNC)


g_itemsCache = _ItemsCache()
