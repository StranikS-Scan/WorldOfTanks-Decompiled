# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_cache.py
from Event import Event
from debug_utils import LOG_DEBUG
from PlayerEvents import g_playerEvents
from gui.server_events.events_helpers import isSuitableForPM
from gui.shared.utils.requesters import ItemsRequester
from gui.shared.utils.requesters import InventoryRequester
from gui.shared.utils.requesters import StatsRequester
from gui.shared.utils.requesters import DossierRequester
from gui.shared.utils.requesters import GoodiesRequester
from gui.shared.utils.requesters import ShopRequester
from gui.shared.utils.requesters import RecycleBinRequester
from gui.shared.utils.requesters import VehicleRotationRequester
from gui.shared.utils.requesters import TokensRequester
from gui.shared.utils.requesters.anonymizer_requester import AnonymizerRequester
from gui.shared.utils.requesters.badges_requester import BadgesRequester
from gui.shared.utils.requesters.RankedRequester import RankedRequester
from gui.shared.utils.requesters.BattleRoyaleRequester import BattleRoyaleRequester
from gui.shared.utils.requesters.EpicMetaGameRequester import EpicMetaGameRequester
from gui.shared.utils.requesters.battle_pass_requester import BattlePassRequester
from gui.shared.utils.requesters.blueprints_requester import BlueprintsRequester
from gui.shared.utils.requesters.game_restrictions_requester import GameRestrictionsRequester
from gui.shared.utils.requesters.session_stats_requester import SessionStatsRequester
from gui.shared.utils.requesters.gift_system_requester import GiftSystemRequester
from gui.shared.utils.requesters.achievements20_requester import Achievements20Requester
from gui.shared.compat_vehicles_cache import CompatVehiclesCache
from helpers import dependency
from skeletons.festivity_factory import IFestivityFactory
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from wg_async import wg_async, wg_await

class CACHE_SYNC_REASON(object):
    SHOW_GUI, CLIENT_UPDATE, SHOP_RESYNC, INVENTORY_RESYNC, DOSSIER_RESYNC, STATS_RESYNC = range(1, 7)


class ItemsCache(IItemsCache):

    def __init__(self):
        super(ItemsCache, self).__init__()
        goodies = GoodiesRequester()
        self.__isForPMSync = False
        self.__needCommonSync = False
        self.__items = ItemsRequester.ItemsRequester(InventoryRequester(), StatsRequester(), DossierRequester(), goodies, ShopRequester(goodies), RecycleBinRequester(), VehicleRotationRequester(), RankedRequester(), BattleRoyaleRequester(), BadgesRequester(), EpicMetaGameRequester(), TokensRequester(), dependency.instance(IFestivityFactory).getRequester(), BlueprintsRequester(), SessionStatsRequester(), AnonymizerRequester(), BattlePassRequester(), GiftSystemRequester(), GameRestrictionsRequester(), Achievements20Requester())
        self.__compatVehiclesCache = CompatVehiclesCache()
        self.__waitForSync = False
        self.__syncFailed = False
        self.onSyncStarted = Event()
        self.onSyncCompleted = Event()
        self.onSyncFailed = Event()
        self.onPMSyncCompleted = Event()

    def init(self):
        g_playerEvents.onInventoryResync += self.__pe_onInventoryResync
        g_playerEvents.onDossiersResync += self.__pe_onDossiersResync
        g_playerEvents.onStatsResync += self.__pe_onStatsResync
        g_playerEvents.onCenterIsLongDisconnected += self._onCenterIsLongDisconnected

    def fini(self):
        self.__items.fini()
        self.__compatVehiclesCache.clear()
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

    @property
    def compatVehiclesCache(self):
        return self.__compatVehiclesCache

    @wg_async
    def update(self, updateReason, diff=None, notify=True):
        if diff is not None:
            self.__isForPMSync, self.__needCommonSync = isSuitableForPM(diff)
        if diff is None or self.__syncFailed:
            yield wg_await(self.__invalidateFullData(updateReason, notify))
        else:
            yield wg_await(self.__invalidateData(updateReason, diff, notify))
        return

    def clear(self):
        LOG_DEBUG('Clearing items cache.')
        self.__compatVehiclesCache.clear()
        return self.items.clear()

    def request(self, callback=None):
        raise SoftException('This method should not be reached in this context')

    def onDisconnected(self):
        self.items.onDisconnected()

    def _onResync(self, reason):
        if not self.__waitForSync:
            self.__invalidateFullData(reason)

    def _onCenterIsLongDisconnected(self, isLongDisconnected):
        self.items.dossiers.onCenterIsLongDisconnected(isLongDisconnected)

    @wg_async
    def __invalidateData(self, updateReason, diff, notify=True):
        self.__waitForSync = True
        wasSyncFailed = self.__syncFailed
        self.__syncFailed = False
        if self.__needCommonSync:
            self.onSyncStarted()
        if updateReason != CACHE_SYNC_REASON.DOSSIER_RESYNC or wasSyncFailed:
            invalidItems = self.__items.invalidateCache(diff)
        else:
            invalidItems = {}
        yield wg_await(self.__items.request())
        self.__waitForSync = False
        if not self.isSynced():
            self.__syncFailed = True
            self.onSyncFailed(updateReason)
        else:
            self.__compatVehiclesCache.invalidateData(self, invalidItems)
            if self.__isForPMSync:
                self.onPMSyncCompleted(updateReason, invalidItems)
            if notify and self.__needCommonSync:
                self.onSyncCompleted(updateReason, invalidItems)

    @wg_async
    def __invalidateFullData(self, updateReason, notify=True):
        self.__waitForSync = True
        wasSyncFailed = self.__syncFailed
        self.__syncFailed = False
        if self.__needCommonSync:
            self.onSyncStarted()
        yield wg_await(self.__items.request())
        self.__waitForSync = False
        if not self.isSynced():
            self.__syncFailed = True
            self.onSyncFailed(updateReason)
        else:
            if updateReason != CACHE_SYNC_REASON.DOSSIER_RESYNC or wasSyncFailed:
                invalidItems = self.__items.invalidateCache()
            else:
                invalidItems = {}
            self.__compatVehiclesCache.invalidateFullData(self)
            if self.__isForPMSync:
                self.onPMSyncCompleted(updateReason, invalidItems)
                if self.__needCommonSync:
                    self.onSyncCompleted(updateReason, invalidItems)
            elif notify:
                self.onSyncCompleted(updateReason, invalidItems)

    def isSynced(self):
        return self.items.isSynced()

    def __pe_onStatsResync(self, *args):
        self._onResync(CACHE_SYNC_REASON.STATS_RESYNC)

    def __pe_onInventoryResync(self, *args):
        self._onResync(CACHE_SYNC_REASON.INVENTORY_RESYNC)

    def __pe_onDossiersResync(self, *args):
        self._onResync(CACHE_SYNC_REASON.DOSSIER_RESYNC)
