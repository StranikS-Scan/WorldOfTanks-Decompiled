# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_cache.py
from Event import Event
from adisp import async
from debug_utils import LOG_DEBUG
from PlayerEvents import g_playerEvents
from gui.shared.utils.requesters import ItemsRequester
from gui.shared.utils.requesters import InventoryRequester
from gui.shared.utils.requesters import StatsRequester
from gui.shared.utils.requesters import DossierRequester
from gui.shared.utils.requesters import GoodiesRequester
from gui.shared.utils.requesters import ShopRequester
from gui.shared.utils.requesters import RecycleBinRequester
from gui.shared.utils.requesters import VehicleRotationRequester
from gui.shared.utils.requesters.badges_requester import BadgesRequester
from gui.shared.utils.requesters.RankedRequester import RankedRequester
from gui.shared.utils.requesters.EpicMetaGameRequester import EpicMetaGameRequester
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException

class CACHE_SYNC_REASON(object):
    SHOW_GUI, CLIENT_UPDATE, SHOP_RESYNC, INVENTORY_RESYNC, DOSSIER_RESYNC, STATS_RESYNC = range(1, 7)


class ItemsCache(IItemsCache):

    def __init__(self):
        super(ItemsCache, self).__init__()
        goodies = GoodiesRequester()
        self.__items = ItemsRequester.ItemsRequester(InventoryRequester(), StatsRequester(), DossierRequester(), goodies, ShopRequester(goodies), RecycleBinRequester(), VehicleRotationRequester(), RankedRequester(), BadgesRequester(), EpicMetaGameRequester())
        self.__waitForSync = False
        self.__syncFailed = False
        self.onSyncStarted = Event()
        self.onSyncCompleted = Event()
        self.onSyncFailed = Event()

    def init(self):
        g_playerEvents.onInventoryResync += self.__pe_onInventoryResync
        g_playerEvents.onDossiersResync += self.__pe_onDossiersResync
        g_playerEvents.onStatsResync += self.__pe_onStatsResync
        g_playerEvents.onCenterIsLongDisconnected += self._onCenterIsLongDisconnected

    def fini(self):
        self.onSyncStarted.clear()
        self.onSyncCompleted.clear()
        self.onSyncFailed.clear()
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
    def update(self, updateReason, diff=None, notify=True, callback=None):
        if diff is None or self.__syncFailed:
            self.__invalidateFullData(updateReason, notify, callback)
        else:
            self.__invalidateData(updateReason, diff, notify, callback)
        return

    def clear(self):
        LOG_DEBUG('Clearing items cache.')
        return self.items.clear()

    def request(self, callback):
        raise SoftException('This method should not be reached in this context')

    def _onResync(self, reason):
        if not self.__waitForSync:
            self.__invalidateFullData(reason)

    def _onCenterIsLongDisconnected(self, isLongDisconnected):
        self.items.dossiers.onCenterIsLongDisconnected(isLongDisconnected)

    def __invalidateData(self, updateReason, diff, notify=True, callback=lambda *args: None):
        self.__waitForSync = True
        wasSyncFailed = self.__syncFailed
        self.__syncFailed = False
        self.onSyncStarted()
        if updateReason != CACHE_SYNC_REASON.DOSSIER_RESYNC or wasSyncFailed:
            invalidItems = self.__items.invalidateCache(diff)
        else:
            invalidItems = {}

        def cbWrapper(*args):
            self.__waitForSync = False
            if not self.isSynced():
                self.__syncFailed = True
                self.onSyncFailed(updateReason)
            elif notify:
                self.onSyncCompleted(updateReason, invalidItems)
            callback(*args)

        self.__items.request()(cbWrapper)

    def __invalidateFullData(self, updateReason, notify=True, callback=lambda *args: None):
        self.__waitForSync = True
        wasSyncFailed = self.__syncFailed
        self.__syncFailed = False
        self.onSyncStarted()

        def cbWrapper(*args):
            self.__waitForSync = False
            if not self.isSynced():
                self.__syncFailed = True
                self.onSyncFailed(updateReason)
            else:
                if updateReason != CACHE_SYNC_REASON.DOSSIER_RESYNC or wasSyncFailed:
                    invalidItems = self.__items.invalidateCache()
                else:
                    invalidItems = {}
                if updateReason == CACHE_SYNC_REASON.SHOW_GUI:
                    self.__items.inventory.updateC11nItemsAppliedCounts()
                if notify:
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
