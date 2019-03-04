# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/listeners.py
import weakref
from PlayerEvents import g_playerEvents
from debug_utils import LOG_DEBUG
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.game_control import IWalletController, IVehicleComparisonBasket, IRentalsController, IRestoreController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
INV_ITEM_VCDESC_KEY = 'compDescr'
CACHE_VEHS_LOCK_KEY = 'vehsLock'
STAT_DIFF_KEY = 'stats'
INVENTORY_DIFF_KEY = 'inventory'
CACHE_DIFF_KEY = 'cache'
GOODIES_DIFF_KEY = 'goodies'
_STAT_DIFF_FORMAT = STAT_DIFF_KEY + '.{0:>s}'
CREDITS_DIFF_KEY = _STAT_DIFF_FORMAT.format('credits')
GOLD_DIFF_KEY = _STAT_DIFF_FORMAT.format('gold')
FREE_XP_DIFF_KEY = _STAT_DIFF_FORMAT.format('freeXP')
UNLOCKS_DIFF_KEY = _STAT_DIFF_FORMAT.format('unlocks')
VEH_XP_DIFF_KEY = _STAT_DIFF_FORMAT.format('vehTypeXP')
ELITE_DIFF_KEY = _STAT_DIFF_FORMAT.format('eliteVehicles')
BLUEPRINT_DIFF_KEY = 'blueprints'
BLUEPRINT_SETTINGS_KEY = 'serverSettings.blueprints_config'

class _Listener(object):

    def __init__(self):
        super(_Listener, self).__init__()
        self._page = None
        return

    def __del__(self):
        LOG_DEBUG('Listener deleted:', self.__class__.__name__)

    def startListen(self, page):
        self._page = page

    def stopListen(self):
        self._page = None
        return


class _BlueprintsListener(_Listener):
    __lobbyContext = dependency.instance(ILobbyContext)

    def startListen(self, page):
        super(_BlueprintsListener, self).startListen(page)
        g_clientUpdateManager.addCallbacks({BLUEPRINT_DIFF_KEY: self._onBlueprintsUpdate,
         BLUEPRINT_SETTINGS_KEY: self.__onBlueprintsModeChanged})

    def stopListen(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(_BlueprintsListener, self).stopListen()

    def _onBlueprintsUpdate(self, blueprints):
        self._page.invalidateBlueprints(blueprints)

    def __onBlueprintsModeChanged(self, _):
        isEnabled = self.__lobbyContext.getServerSettings().blueprintsConfig.isBlueprintsAvailable()
        self._page.invalidateBlueprintMode(isEnabled)


class _StatsListener(_Listener):
    __lobbyContext = dependency.instance(ILobbyContext)

    def startListen(self, page):
        super(_StatsListener, self).startListen(page)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        g_clientUpdateManager.addCallbacks({CREDITS_DIFF_KEY: self._onCreditsUpdate,
         GOLD_DIFF_KEY: self._onGoldUpdate,
         FREE_XP_DIFF_KEY: self._onFreeXPUpdate,
         UNLOCKS_DIFF_KEY: self._onUnlocksUpdate,
         VEH_XP_DIFF_KEY: self._onVehiclesXPUpdate,
         ELITE_DIFF_KEY: self._onEliteVehiclesUpdate})

    def stopListen(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(_StatsListener, self).stopListen()

    def _onCreditsUpdate(self, _):
        self._page.invalidateCredits()

    def _onGoldUpdate(self, _):
        self._page.invalidateGold()

    def _onFreeXPUpdate(self, _):
        self._page.invalidateFreeXP()

    def _onEliteVehiclesUpdate(self, elites):
        self._page.invalidateElites(elites)

    def _onVehiclesXPUpdate(self, xps):
        newXPs = {key:(value if value else 0) for key, value in xps.iteritems()}
        self._page.invalidateVTypeXP(newXPs)

    def _onUnlocksUpdate(self, unlocks):
        self._page.invalidateUnlocks(unlocks)

    def __onServerSettingsChanged(self, diff):
        if self.__lobbyContext.getServerSettings().isIngameDataChangedInDiff(diff, 'isEnabled'):
            self._onGoldUpdate(None)
        return


class _ItemsCacheListener(_Listener):
    __itemsCache = dependency.descriptor(IItemsCache)
    __comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self):
        super(_ItemsCacheListener, self).__init__()
        self.__invalidated = set()

    def startListen(self, page):
        super(_ItemsCacheListener, self).startListen(page)
        g_clientUpdateManager.addCallbacks({INVENTORY_DIFF_KEY: self.__onInventoryUpdate,
         CACHE_DIFF_KEY: self.__onCacheUpdate,
         GOODIES_DIFF_KEY: self.__onGoodiesUpdate})
        g_playerEvents.onCenterIsLongDisconnected += self.__center_onIsLongDisconnected
        self.__itemsCache.onSyncCompleted += self.__items_onSyncCompleted
        self.__comparisonBasket.onChange += self.__onVehCompareBasketChanged
        self.__comparisonBasket.onSwitchChange += self.__onVehCompareBasketSwitchChange

    def stopListen(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_playerEvents.onCenterIsLongDisconnected -= self.__center_onIsLongDisconnected
        self.__itemsCache.onSyncCompleted -= self.__items_onSyncCompleted
        self.__comparisonBasket.onChange -= self.__onVehCompareBasketChanged
        self.__comparisonBasket.onSwitchChange -= self.__onVehCompareBasketSwitchChange
        super(_ItemsCacheListener, self).stopListen()

    def __onInventoryUpdate(self, _):
        self._page.invalidateInventory(self.__invalidated)

    def __onGoodiesUpdate(self, goodies):
        invalidated = set()
        vehicleDiscounts = self.__itemsCache.items.shop.getVehicleDiscountDescriptions()
        for goodieID in goodies:
            vehicleDiscount = vehicleDiscounts.get(goodieID)
            if vehicleDiscount:
                invalidated.add(vehicleDiscount.target.targetValue)

        self._page.invalidateDiscounts(invalidated)

    def __onCacheUpdate(self, cache):
        if CACHE_VEHS_LOCK_KEY in cache:
            vehLocks = cache.get(CACHE_VEHS_LOCK_KEY)
            if vehLocks:
                self._page.invalidateVehLocks(vehLocks)

    def __items_onSyncCompleted(self, reason, invalidated):
        self.__invalidated = set()
        for itemTypeID, uniqueIDs in invalidated.iteritems():
            if itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES or itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                self.__invalidated |= uniqueIDs

        if reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            self._page.redraw()

    def __center_onIsLongDisconnected(self, _):
        self._page.redraw()

    def __onVehCompareBasketChanged(self, changedData):
        if changedData.isFullChanged:
            self._page.invalidateVehCompare()

    def __onVehCompareBasketSwitchChange(self):
        self._page.invalidateVehCompare()


class _WalletStatusListener(_Listener):
    __wallet = dependency.descriptor(IWalletController)

    def startListen(self, page):
        super(_WalletStatusListener, self).startListen(page)
        self.__wallet.onWalletStatusChanged += self.__onWalletStatusChanged

    def stopListen(self):
        self.__wallet.onWalletStatusChanged -= self.__onWalletStatusChanged
        super(_WalletStatusListener, self).stopListen()

    def __onWalletStatusChanged(self, status):
        self._page.invalidateWalletStatus(status)


class _RentChangeListener(_Listener):
    __rentals = dependency.descriptor(IRentalsController)

    def startListen(self, page):
        super(_RentChangeListener, self).startListen(page)
        self.__rentals.onRentChangeNotify += self.__onRentChange

    def stopListen(self):
        self.__rentals.onRentChangeNotify -= self.__onRentChange
        super(_RentChangeListener, self).stopListen()

    def __onRentChange(self, vehicles):
        self._page.invalidateRent(vehicles)


class _RestoreListener(_Listener):
    __restores = dependency.descriptor(IRestoreController)

    def startListen(self, page):
        self.__restores.onRestoreChangeNotify += self.__onRestoreChanged
        super(_RestoreListener, self).startListen(page)

    def stopListen(self):
        self.__restores.onRestoreChangeNotify -= self.__onRestoreChanged
        super(_RestoreListener, self).stopListen()

    def __onRestoreChanged(self, vehicles):
        self._page.invalidateRestore(vehicles)


class _PrbGlobalListener(_Listener, IGlobalListener):

    def startListen(self, page):
        super(_PrbGlobalListener, self).startListen(page)
        self.startGlobalListening()

    def stopListen(self):
        super(_PrbGlobalListener, self).stopListen()
        self.stopGlobalListening()

    def onPrbEntitySwitched(self):
        self._page.invalidatePrbState()

    def onPreQueueSettingsChanged(self, diff):
        self._page.invalidatePrbState()

    def onPlayerStateChanged(self, entity, roster, accountInfo):
        if accountInfo.isCurrentPlayer():
            self._page.invalidatePrbState()

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self._page.invalidatePrbState()


class TTListenerDecorator(_Listener):
    __slots__ = ('_stats', '_items', '_wallet', '_prbListener', '_rent')

    def __init__(self):
        super(TTListenerDecorator, self).__init__()
        self._stats = _StatsListener()
        self._items = _ItemsCacheListener()
        self._wallet = _WalletStatusListener()
        self._prbListener = _PrbGlobalListener()
        self._rent = _RentChangeListener()
        self._restore = _RestoreListener()
        self._blueprints = _BlueprintsListener()

    def startListen(self, page):
        proxy = weakref.proxy(page)
        self._stats.startListen(proxy)
        self._items.startListen(proxy)
        self._wallet.startListen(proxy)
        self._prbListener.startListen(proxy)
        self._rent.startListen(proxy)
        self._restore.startListen(proxy)
        self._blueprints.startListen(proxy)

    def stopListen(self):
        self._stats.stopListen()
        self._items.stopListen()
        self._wallet.stopListen()
        self._prbListener.stopListen()
        self._rent.stopListen()
        self._restore.stopListen()
        self._blueprints.stopListen()
