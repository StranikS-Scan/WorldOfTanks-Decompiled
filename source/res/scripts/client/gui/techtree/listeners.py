# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/techtree/listeners.py
from logging import getLogger
import typing
import weakref
from collector_vehicle import CollectorVehicleConsts
from PlayerEvents import g_playerEvents
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.game_control import IWalletController, IVehicleComparisonBasket, IRentalsController, IRestoreController, IEarlyAccessController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.techtree_events import ITechTreeEventsListener
_logger = getLogger(__name__)
_INV_ITEM_VCDESC_KEY = 'compDescr'
_CACHE_VEHS_LOCK_KEY = 'vehsLock'
_STAT_DIFF_KEY = 'stats'
_INVENTORY_DIFF_KEY = 'inventory'
_CACHE_DIFF_KEY = 'cache'
_GOODIES_DIFF_KEY = 'goodies'
_STAT_DIFF_FORMAT = _STAT_DIFF_KEY + '.{0:>s}'
_CREDITS_DIFF_KEY = _STAT_DIFF_FORMAT.format('credits')
_GOLD_DIFF_KEY = _STAT_DIFF_FORMAT.format('gold')
_FREE_XP_DIFF_KEY = _STAT_DIFF_FORMAT.format('freeXP')
_UNLOCKS_DIFF_KEY = _STAT_DIFF_FORMAT.format('unlocks')
_VEH_XP_DIFF_KEY = _STAT_DIFF_FORMAT.format('vehTypeXP')
_ELITE_DIFF_KEY = _STAT_DIFF_FORMAT.format('eliteVehicles')
_BLUEPRINT_DIFF_KEY = 'blueprints'
_BLUEPRINT_SETTINGS_KEY = 'serverSettings.blueprints_config'

class IPage(object):

    def redraw(self):
        pass

    def invalidateBlueprints(self, blueprints):
        pass

    def invalidateBlueprintMode(self, isEnabled):
        pass

    def invalidateCredits(self):
        pass

    def invalidateGold(self):
        pass

    def invalidateFreeXP(self):
        pass

    def invalidateElites(self, elites):
        pass

    def invalidateVTypeXP(self, xps):
        pass

    def invalidateUnlocks(self, unlocks):
        pass

    def invalidateInventory(self, data):
        pass

    def invalidateVehCompare(self):
        pass

    def invalidateVehicleCollectorState(self):
        pass

    def invalidateVehPostProgression(self):
        pass

    def invalidatePrbState(self):
        pass

    def invalidateDiscounts(self, data):
        pass

    def invalidateVehLocks(self, locks):
        pass

    def invalidateWalletStatus(self, status):
        pass

    def invalidateRent(self, vehicles):
        pass

    def invalidateRestore(self, vehicles):
        pass

    def invalidateEventsData(self):
        pass

    def invalidateParagonsAnouncement(self):
        pass

    def clearSelectedNation(self):
        pass


class _Listener(object):

    def __init__(self):
        super(_Listener, self).__init__()
        self._page = None
        return

    def __del__(self):
        _logger.debug('Listener deleted: %s', self.__class__.__name__)

    def startListen(self, page):
        self._page = page

    def stopListen(self):
        self._page = None
        return


class _BlueprintsListener(_Listener):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def startListen(self, page):
        super(_BlueprintsListener, self).startListen(page)
        g_clientUpdateManager.addCallbacks({_BLUEPRINT_DIFF_KEY: self._onBlueprintsUpdate,
         _BLUEPRINT_SETTINGS_KEY: self.__onBlueprintsModeChanged})

    def stopListen(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(_BlueprintsListener, self).stopListen()

    def _onBlueprintsUpdate(self, blueprints):
        self._page.invalidateBlueprints(blueprints)

    def __onBlueprintsModeChanged(self, _):
        isEnabled = self.__lobbyContext.getServerSettings().blueprintsConfig.isBlueprintsAvailable()
        self._page.invalidateBlueprintMode(isEnabled)


class _StatsListener(_Listener):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def startListen(self, page):
        super(_StatsListener, self).startListen(page)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        g_clientUpdateManager.addCallbacks({_CREDITS_DIFF_KEY: self._onCreditsUpdate,
         _GOLD_DIFF_KEY: self._onGoldUpdate,
         _FREE_XP_DIFF_KEY: self._onFreeXPUpdate,
         _UNLOCKS_DIFF_KEY: self._onUnlocksUpdate,
         _VEH_XP_DIFF_KEY: self._onVehiclesXPUpdate,
         _ELITE_DIFF_KEY: self._onEliteVehiclesUpdate})

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
        if self.__lobbyContext.getServerSettings().isShopDataChangedInDiff(diff, 'isEnabled'):
            self._onGoldUpdate(None)
        if CollectorVehicleConsts.CONFIG_NAME in diff:
            self._page.invalidateVehicleCollectorState()
        return


class _ItemsCacheListener(_Listener):
    __itemsCache = dependency.descriptor(IItemsCache)
    __comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self):
        super(_ItemsCacheListener, self).__init__()
        self.__invalidated = set()

    def startListen(self, page):
        super(_ItemsCacheListener, self).startListen(page)
        g_clientUpdateManager.addCallbacks({_INVENTORY_DIFF_KEY: self.__onInventoryUpdate,
         _CACHE_DIFF_KEY: self.__onCacheUpdate,
         _GOODIES_DIFF_KEY: self.__onGoodiesUpdate})
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
        if _CACHE_VEHS_LOCK_KEY in cache:
            vehLocks = cache.get(_CACHE_VEHS_LOCK_KEY)
            if vehLocks:
                self._page.invalidateVehLocks(vehLocks)

    def __items_onSyncCompleted(self, reason, invalidated):
        self.__invalidated = set()
        for itemTypeID, uniqueIDs in invalidated.iteritems():
            if itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES or itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                self.__invalidated |= uniqueIDs

        if reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            self._page.redraw()
        if GUI_ITEM_TYPE.VEH_POST_PROGRESSION in invalidated:
            self._page.invalidateVehPostProgression()

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
        g_playerEvents.onDisconnected += self.__onDisconnected
        self.startGlobalListening()

    def stopListen(self):
        super(_PrbGlobalListener, self).stopListen()
        g_playerEvents.onDisconnected -= self.__onDisconnected
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

    def __onDisconnected(self):
        self._page.clearSelectedNation()


class _EarlyAccessListener(_Listener):
    __earlyAccessController = dependency.descriptor(IEarlyAccessController)

    def startListen(self, page):
        super(_EarlyAccessListener, self).startListen(page)
        self.__earlyAccessController.onUpdated += self.__onUpdated
        self.__earlyAccessController.onBalanceUpdated += self.__onUpdated

    def stopListen(self):
        self.__earlyAccessController.onUpdated -= self.__onUpdated
        self.__earlyAccessController.onBalanceUpdated -= self.__onUpdated
        super(_EarlyAccessListener, self).stopListen()

    def __onUpdated(self):
        self._page.invalidateEarlyAccess()


class _TechTreeActionEventsListener(_Listener):
    __techTreeEventsListener = dependency.descriptor(ITechTreeEventsListener)

    def startListen(self, page):
        super(_TechTreeActionEventsListener, self).startListen(page)
        self.__techTreeEventsListener.onSettingsChanged += self.__onSettingsChanged
        self.__techTreeEventsListener.onEntryPointUpdated += self.__onEntryPointsUpdated

    def stopListen(self):
        self.__techTreeEventsListener.onSettingsChanged -= self.__onSettingsChanged
        self.__techTreeEventsListener.onEntryPointUpdated -= self.__onEntryPointsUpdated
        super(_TechTreeActionEventsListener, self).stopListen()

    def __onSettingsChanged(self):
        self._page.invalidateEventsData()

    def __onEntryPointsUpdated(self):
        self._page.invalidateParagonsAnouncement()


class TTListenerDecorator(_Listener):
    __slots__ = ('_stats', '_items', '_wallet', '_prbListener', '_rent', '_restore', '_blueprints', '_earlyAccess', '_actions')

    def __init__(self):
        super(TTListenerDecorator, self).__init__()
        self._stats = _StatsListener()
        self._items = _ItemsCacheListener()
        self._wallet = _WalletStatusListener()
        self._prbListener = _PrbGlobalListener()
        self._rent = _RentChangeListener()
        self._restore = _RestoreListener()
        self._blueprints = _BlueprintsListener()
        self._earlyAccess = _EarlyAccessListener()
        self._actions = _TechTreeActionEventsListener()

    def startListen(self, page):
        proxy = weakref.proxy(page)
        self._stats.startListen(proxy)
        self._items.startListen(proxy)
        self._wallet.startListen(proxy)
        self._prbListener.startListen(proxy)
        self._rent.startListen(proxy)
        self._restore.startListen(proxy)
        self._blueprints.startListen(proxy)
        self._earlyAccess.startListen(proxy)
        self._actions.startListen(proxy)

    def stopListen(self):
        self._stats.stopListen()
        self._items.stopListen()
        self._wallet.stopListen()
        self._prbListener.stopListen()
        self._rent.stopListen()
        self._restore.stopListen()
        self._blueprints.stopListen()
        self._earlyAccess.stopListen()
        self._actions.stopListen()
