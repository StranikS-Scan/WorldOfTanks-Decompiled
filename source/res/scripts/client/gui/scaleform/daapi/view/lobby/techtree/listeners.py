# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/listeners.py
import weakref
from PlayerEvents import g_playerEvents
from debug_utils import LOG_DEBUG
from gui import game_control
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.game_control import getVehicleComparisonBasketCtrl
from gui.prb_control.prb_helpers import GlobalListener
from gui.shared.ItemsCache import CACHE_SYNC_REASON, g_itemsCache
from gui.shared.gui_items import GUI_ITEM_TYPE
INV_ITEM_VCDESC_KEY = 'compDescr'
CACHE_VEHS_LOCK_KEY = 'vehsLock'
STAT_DIFF_KEY = 'stats'
INVENTORY_DIFF_KEY = 'inventory'
CACHE_DIFF_KEY = 'cache'
_STAT_DIFF_FORMAT = STAT_DIFF_KEY + '.{0:>s}'
CREDITS_DIFF_KEY = _STAT_DIFF_FORMAT.format('credits')
GOLD_DIFF_KEY = _STAT_DIFF_FORMAT.format('gold')
FREE_XP_DIFF_KEY = _STAT_DIFF_FORMAT.format('freeXP')
UNLOCKS_DIFF_KEY = _STAT_DIFF_FORMAT.format('unlocks')
VEH_XP_DIFF_KEY = _STAT_DIFF_FORMAT.format('vehTypeXP')
ELITE_DIFF_KEY = _STAT_DIFF_FORMAT.format('eliteVehicles')

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


class _StatsListener(_Listener):

    def startListen(self, page):
        super(_StatsListener, self).startListen(page)
        g_clientUpdateManager.addCallbacks({CREDITS_DIFF_KEY: self._onCreditsUpdate,
         GOLD_DIFF_KEY: self._onGoldUpdate,
         FREE_XP_DIFF_KEY: self._onFreeXPUpdate,
         UNLOCKS_DIFF_KEY: self._onUnlocksUpdate,
         VEH_XP_DIFF_KEY: self._onVehiclesXPUpdate,
         ELITE_DIFF_KEY: self._onEliteVehiclesUpdate})

    def stopListen(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(_StatsListener, self).stopListen()

    def _onCreditsUpdate(self, _):
        """
        Value of credits updated.
        """
        self._page.invalidateCredits()

    def _onGoldUpdate(self, _):
        """
        Value of gold updated.
        """
        self._page.invalidateGold()

    def _onFreeXPUpdate(self, _):
        """
        Value of free experience updated.
        """
        self._page.invalidateFreeXP()

    def _onEliteVehiclesUpdate(self, elites):
        """
        Set of elite vehicles updated.
        :param elites: set([<compactDescr>, ...])
        """
        self._page.invalidateElites(elites)

    def _onVehiclesXPUpdate(self, xps):
        """
        Dict of vehicles experience updated.
        :param xps: dict(<int:vehicle compact descriptor> : <XP>, ...)
        """
        self._page.invalidateVTypeXP(xps)

    def _onUnlocksUpdate(self, unlocks):
        """
        Set of unlocks items updated.
        :param unlocks: set([<int:compactDescr>, ...])
        """
        self._page.invalidateUnlocks(unlocks)


class _ItemsCacheListener(_Listener):

    def __init__(self):
        super(_ItemsCacheListener, self).__init__()
        self.__invalidated = set()

    def startListen(self, page):
        super(_ItemsCacheListener, self).startListen(page)
        g_clientUpdateManager.addCallbacks({INVENTORY_DIFF_KEY: self.__onInventoryUpdate,
         CACHE_DIFF_KEY: self.__onCacheUpdate})
        g_itemsCache.onSyncCompleted += self.__items_onSyncCompleted
        g_playerEvents.onCenterIsLongDisconnected += self.__center_onIsLongDisconnected
        comparisonBasket = getVehicleComparisonBasketCtrl()
        comparisonBasket.onChange += self.__onVehCompareBasketChanged
        comparisonBasket.onSwitchChange += self.__onVehCompareBasketSwitchChange

    def stopListen(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_itemsCache.onSyncCompleted -= self.__items_onSyncCompleted
        g_playerEvents.onCenterIsLongDisconnected -= self.__center_onIsLongDisconnected
        comparisonBasket = getVehicleComparisonBasketCtrl()
        comparisonBasket.onChange -= self.__onVehCompareBasketChanged
        comparisonBasket.onSwitchChange -= self.__onVehCompareBasketSwitchChange
        super(_ItemsCacheListener, self).stopListen()

    def __onInventoryUpdate(self, _):
        self._page.invalidateInventory(self.__invalidated)

    def __onCacheUpdate(self, cache):
        if CACHE_VEHS_LOCK_KEY in cache:
            vehLocks = cache.get(CACHE_VEHS_LOCK_KEY)
            if vehLocks and len(vehLocks):
                self._page.invalidateVehLocks(vehLocks)

    def __items_onSyncCompleted(self, reason, invalidated):
        """
        Listener for event __ItemsCache.onSyncCompleted.
        :param reason: CACHE_SYNC_REASON
        :param invalidated: dict( <itemTypeID> : <int-type compact > )
        """
        self.__invalidated = set()
        for itemTypeID, uniqueIDs in invalidated.iteritems():
            if itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES or itemTypeID == GUI_ITEM_TYPE.VEHICLE:
                self.__invalidated |= uniqueIDs

        if reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            self._page.redraw()

    def __center_onIsLongDisconnected(self, _):
        """
        Listener for event _PlayerEvents.onCenterIsLongDisconnected.
        """
        self._page.redraw()

    def __onVehCompareBasketChanged(self, changedData):
        """
        gui.game_control.VehComparisonBasket.onChange event handler
        :param changedData: instance of gui.game_control.veh_comparison_basket._ChangedData
        """
        if changedData.isFullChanged:
            self._page.invalidateVehCompare()

    def __onVehCompareBasketSwitchChange(self):
        """
        gui.game_control.VehComparisonBasket.onSwitchChange event handler
        """
        self._page.invalidateVehCompare()


class _WalletStatusListener(_Listener):

    def startListen(self, page):
        super(_WalletStatusListener, self).startListen(page)
        game_control.g_instance.wallet.onWalletStatusChanged += self.__onWalletStatusChanged

    def stopListen(self):
        game_control.g_instance.wallet.onWalletStatusChanged -= self.__onWalletStatusChanged
        super(_WalletStatusListener, self).stopListen()

    def __onWalletStatusChanged(self, status):
        self._page.invalidateWalletStatus(status)


class _RentChangeListener(_Listener):

    def startListen(self, page):
        super(_RentChangeListener, self).startListen(page)
        game_control.g_instance.rentals.onRentChangeNotify += self.__onRentChange

    def stopListen(self):
        game_control.g_instance.rentals.onRentChangeNotify -= self.__onRentChange
        super(_RentChangeListener, self).stopListen()

    def __onRentChange(self, vehicles):
        self._page.invalidateRent(vehicles)


class _PrbGlobalListener(_Listener, GlobalListener):

    def startListen(self, page):
        super(_PrbGlobalListener, self).startListen(page)
        self.startGlobalListening()

    def stopListen(self):
        super(_PrbGlobalListener, self).stopListen()
        self.stopGlobalListening()

    def onPrbFunctionalInited(self):
        self._page.invalidatePrbState()

    def onPrbFunctionalFinished(self):
        self._page.invalidatePrbState()

    def onPreQueueFunctionalInited(self):
        self._page.invalidatePrbState()

    def onPreQueueFunctionalFinished(self):
        self._page.invalidatePrbState()

    def onPreQueueSettingsChanged(self, diff):
        self._page.invalidatePrbState()

    def onPlayerStateChanged(self, functional, roster, accountInfo):
        if accountInfo.isCurrentPlayer():
            self._page.invalidatePrbState()

    def onUnitFunctionalInited(self):
        self._page.invalidatePrbState()

    def onUnitFunctionalFinished(self):
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

    def startListen(self, page):
        proxy = weakref.proxy(page)
        self._stats.startListen(proxy)
        self._items.startListen(proxy)
        self._wallet.startListen(proxy)
        self._prbListener.startListen(proxy)
        self._rent.startListen(proxy)

    def stopListen(self):
        self._stats.stopListen()
        self._items.stopListen()
        self._wallet.stopListen()
        self._prbListener.stopListen()
        self._rent.stopListen()
