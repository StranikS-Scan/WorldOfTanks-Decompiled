# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/game_control/battle_royale_rent_vehicles_controller.py
import logging
import math
import typing
import time
from functools import wraps, partial
from wg_async import wg_await, wg_async
import BigWorld
import AccountCommands
from CurrentVehicle import g_currentVehicle
from Event import Event, EventManager
from constants import Configs
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen.view_models.views.battle_royale.equipment_panel_cmp_rent_states import EquipmentPanelCmpRentStates
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.money import DynamicMoney, Currency
from helpers import dependency, time_utils, server_settings
from skeletons.gui.game_control import IBattleRoyaleRentVehiclesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import getUserName
from items import vehicles
from gui import SystemMessages
from gui.impl.dialogs import dialogs
from battle_royale.gui.impl.dialogs.rentConfirm import RentConfirm
from battle_royale.gui.constants import STP_COIN, BR_COIN
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)
_RENT_CURRENCIES = {Currency.CREDITS}
ACTIVE_RANT_STATES = (EquipmentPanelCmpRentStates.STATE_TEST_DRIVE_ACTIVE, EquipmentPanelCmpRentStates.STATE_RENT_ACTIVE)

def _defaultCurrentVehicle(func):

    @wraps(func)
    def decorator(self, intCD=None, *args, **kwargs):
        if intCD is None:
            intCD = g_currentVehicle.intCD
        return func(self, intCD, *args, **kwargs)

    return decorator


def _getTillTimeStringByRClass(timeValue, isRoundUp=False):
    gmtime = time.gmtime(timeValue)
    if isRoundUp and gmtime.tm_sec > 0:
        timeValue += time_utils.ONE_MINUTE
        gmtime = time.gmtime(timeValue)
    tm = time.struct_time(gmtime)
    if timeValue >= time_utils.ONE_DAY:
        return backport.text(R.strings.battle_royale.status.timeLeft.days(), day=str(tm.tm_yday))
    if timeValue >= time_utils.ONE_HOUR:
        return backport.text(R.strings.battle_royale.status.timeLeft.hours(), hour=str(tm.tm_hour))
    return backport.text(R.strings.battle_royale.status.timeLeft.min(), min=str(tm.tm_min)) if timeValue >= time_utils.ONE_MINUTE else backport.text(R.strings.battle_royale.status.timeLeft.min(), min='1')


class BattleRoyaleRentVehiclesController(IBattleRoyaleRentVehiclesController):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(BattleRoyaleRentVehiclesController, self).__init__()
        self.__balance = None
        self.__economics = None
        self.__rentWatcher = None
        self.__rentWatchCallbackId = None
        self.__rentWatcherCurrentVehicleCallback = None
        self._eManager = EventManager()
        self.onBalanceUpdated = Event(self._eManager)
        self.onPriceInfoUpdated = Event(self._eManager)
        self.onRentInfoUpdated = Event(self._eManager)
        self.onUpdated = Event(self._eManager)
        return

    def init(self):
        self.__balance = DynamicMoney()

    def fini(self):
        self._eManager.clear()
        self.__clear()

    def onLobbyInited(self, event):
        self.__economics = {}
        self.__rentWatcher = {}
        self.__readEconomics()
        self.__initBalanceCurrencies()
        self.__addEventHandlers()

    def onAvatarBecomePlayer(self):
        self.__removeEventHandlers()

    def onAccountBecomePlayer(self):
        self.init()

    def onAccountBecomeNonPlayer(self):
        self.__clear()

    @_defaultCurrentVehicle
    def isInTestDriveRent(self, intCD=None):
        return self.__getTestDriveTimeLeft(intCD) > 0

    def getBRCoinBalance(self, default=None):
        return self.__balance.get(BR_COIN, default)

    def getSTPCoinBalance(self, default=None):
        return self.__balance.get(STP_COIN, default)

    @_defaultCurrentVehicle
    def getRentState(self, intCD=None):
        vehicle = self.__itemsCache.items.getItemByCD(intCD)
        if vehicle is None:
            _logger.error('Unable to get rent state for non existing vehicle')
            return
        elif vehicle.isRented:
            if not vehicle.rentExpiryState:
                if self.isInTestDriveRent(intCD):
                    return EquipmentPanelCmpRentStates.STATE_TEST_DRIVE_ACTIVE
                return EquipmentPanelCmpRentStates.STATE_RENT_ACTIVE
            if self.__wasInTestDrive(intCD):
                return EquipmentPanelCmpRentStates.STATE_RENT_AVAILABLE
            return EquipmentPanelCmpRentStates.STATE_TEST_DRIVE_AVAILABLE
        else:
            return EquipmentPanelCmpRentStates.STATE_NORMAL

    @_defaultCurrentVehicle
    def isRentable(self, intCD=None):
        return bool(self.__getEconomicsRent(intCD))

    @_defaultCurrentVehicle
    def getTestDrivePrice(self, intCD=None):
        return self.__getEconomicsTestDriveRentMoney(intCD)

    @_defaultCurrentVehicle
    def getRentPrice(self, intCD=None):
        return self.__getEconomicsRentMoney(intCD)

    @_defaultCurrentVehicle
    def getRentDaysLeft(self, intCD=None):
        seconds = self.getRentTimeLeft(intCD)
        return int(math.ceil(seconds / time_utils.ONE_DAY))

    @_defaultCurrentVehicle
    def getRentTimeLeft(self, intCD=None):
        seconds = 0
        state = self.getRentState(intCD)
        if state in ACTIVE_RANT_STATES:
            if self.isInTestDriveRent(intCD):
                seconds = self.__getTestDriveTimeLeft(intCD)
            else:
                seconds = self.__getRentTimeLeft(intCD)
        return seconds

    @_defaultCurrentVehicle
    def getFormatedRentTimeLeft(self, intCD=None, isRoundUp=False):
        seconds = self.getRentTimeLeft(intCD)
        return _getTillTimeStringByRClass(seconds, isRoundUp) if seconds > 0 else ''

    @_defaultCurrentVehicle
    def getPendingRentDays(self, intCD=None):
        return self.getNextTestDriveDaysTotal(intCD) if not self.__wasInTestDrive(intCD) or self.isInTestDriveRent(intCD) else int(self.getNextRentDaysTotal(intCD))

    @_defaultCurrentVehicle
    def getNextTestDriveDaysTotal(self, intCD=None):
        if not self.isRentable(intCD):
            return 0
        economics = self.__getEconomics(intCD)
        return int(economics.get('testDrive', 0))

    @_defaultCurrentVehicle
    def getNextRentDaysTotal(self, intCD=None):
        if not self.isRentable(intCD):
            return 0
        rent = self.__getEconomicsRent(intCD)
        return int(rent.get('time', 0))

    @_defaultCurrentVehicle
    def isEnoughMoneyToPurchase(self, intCD=None, state=None):
        if state is None:
            state = self.getRentState(intCD)
        if state == EquipmentPanelCmpRentStates.STATE_TEST_DRIVE_AVAILABLE:
            price = self.getTestDrivePrice(intCD)
        elif state == EquipmentPanelCmpRentStates.STATE_RENT_AVAILABLE:
            price = self.getRentPrice(intCD)
        else:
            return False
        return not self.__balance.getShortage(price)

    @_defaultCurrentVehicle
    def purchaseRent(self, intCD=None):
        state = self.getRentState(intCD)
        rentMethod = None
        if state == EquipmentPanelCmpRentStates.STATE_TEST_DRIVE_AVAILABLE:
            rentMethod = BigWorld.player().AccountBattleRoyaleComponent.applyTestDrive
        elif state == EquipmentPanelCmpRentStates.STATE_RENT_AVAILABLE:
            if self.isEnoughMoneyToPurchase(intCD, state=state):
                rentMethod = BigWorld.player().AccountBattleRoyaleComponent.applyRent
            else:
                _logger.warn('not enough money to purchase rent! (%s)', intCD)
        if rentMethod is not None:
            self.showBuyConfirmDialog(intCD, rentMethod, state)
        return

    @wg_async
    def showBuyConfirmDialog(self, intCD, rentMethod, state):
        result = yield wg_await(dialogs.showSingleDialogWithResultData(vehicleCD=intCD, layoutID=RentConfirm.LAYOUT_ID, wrappedViewClass=RentConfirm))
        isOK, _ = result.result
        if isOK:
            vehicle = self.__itemsCache.items.getItemByCD(intCD)
            respone = partial(self.__rentResponce, state, intCD)
            rentMethod(vehicle.invID, respone)

    def watchRentVehicles(self, callback, vehIntCDs=None):
        if not callable(callback) or self.__rentWatcher is None:
            return
        else:
            self.unwatchRentVehicles(callback, runWatch=False)
            if vehIntCDs is not None:
                vehIntCDs = set(vehIntCDs if isinstance(vehIntCDs, (tuple, list, set)) else [vehIntCDs])
                self.__rentWatcher[callback] = vehIntCDs
            self.__runWatch()
            return

    def unwatchRentVehicles(self, callback, runWatch=True):
        if not callable(callback) or self.__rentWatcher is None:
            return
        else:
            if callback in self.__rentWatcher:
                del self.__rentWatcher[callback]
                if runWatch:
                    self.__runWatch()
            return

    def setRentUpdateCurrentVehicleCallback(self, callback):
        self.__rentWatcherCurrentVehicleCallback = callback

    def clearRentUpdateCurrentVehicleCallback(self, callback):
        self.__rentWatcherCurrentVehicleCallback = None
        return

    def __rentResponce(self, state, intCD, *args):
        resultID = args[1]
        vehicleName = getUserName(vehicles.getVehicleType(intCD))
        messageStr = ''
        smType = SystemMessages.SM_TYPE.Information
        priority = 'medium'
        if resultID != AccountCommands.RES_SUCCESS:
            messageStr = backport.text(R.strings.battle_royale.vehicleRentNoMoney(), vehicle=vehicleName)
            smType = SystemMessages.SM_TYPE.Error
            priority = 'high'
        else:
            _resId = None
            if state == EquipmentPanelCmpRentStates.STATE_TEST_DRIVE_AVAILABLE:
                _resId = R.strings.battle_royale.vehicleTestDriveIsOk
            elif state == EquipmentPanelCmpRentStates.STATE_RENT_AVAILABLE:
                _resId = R.strings.battle_royale.vehicleRentIsOk
            if _resId:
                rentTime = self.getRentDaysLeft(intCD)
                messageStr = backport.text(_resId(), vehicle=vehicleName, days=rentTime)
        if messageStr:
            SystemMessages.pushI18nMessage(messageStr, type=smType, priority=priority)
        return

    def __getTestDriveTimeLeft(self, intCD):
        expiredTime = self.__testDriveExpiredTime(intCD)
        if expiredTime != float('inf'):
            seconds = float(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(expiredTime)))
            return seconds

    def __getRentTimeLeft(self, intCD):
        vehicle = self.__itemsCache.items.getItemByCD(intCD)
        return 0 if vehicle is None or not vehicle.isRented else vehicle.rentLeftTime

    def __readEconomics(self):
        config = self.__lobbyContext.getServerSettings().battleRoyale
        self.__economics = config.economics

    def __testDriveExpiredTime(self, intCD):
        return self.__itemsCache.items.battleRoyale.testDriveExpired.get(intCD, float('inf'))

    def __wasInTestDrive(self, intCD):
        return self.__testDriveExpiredTime(intCD) != float('inf')

    def __getEconomicsRent(self, intCD):
        return self.__getEconomics(intCD).get('rent', {})

    def __getEconomicsTestDriveRent(self, intCD):
        testDriveRent = self.__getEconomics(intCD).get('testDriveRent', None)
        if testDriveRent is None:
            currency = self.__getRentCurrency(intCD)
            if currency is None:
                return {}
            return {'currency': currency,
             'amount': 0}
        else:
            return testDriveRent

    def __getRentCurrency(self, intCD):
        rent = self.__getEconomicsRent(intCD)
        return rent.get('currency')

    def __getEconomics(self, intCD):
        return self.__economics.get(intCD, {})

    def __getEconomicsTestDriveRentMoney(self, intCD):
        rent = self.__getEconomicsTestDriveRent(intCD)
        return self.__readRentPrice(rent)

    def __getEconomicsRentMoney(self, intCD):
        rent = self.__getEconomicsRent(intCD)
        return self.__readRentPrice(rent)

    def __readRentPrice(self, rent, default=0):
        currency = rent.get('currency')
        if currency is None:
            return DynamicMoney()
        else:
            amount = rent.get('amount', default)
            return DynamicMoney(**{currency: amount})

    def __getRentPrice(self, intCD):
        state = self.getRentState(intCD)
        if state == EquipmentPanelCmpRentStates.STATE_TEST_DRIVE_AVAILABLE:
            return self.getTestDrivePrice(intCD)
        else:
            return self.getRentPrice(intCD) if state == EquipmentPanelCmpRentStates.STATE_RENT_AVAILABLE else None

    def __onSyncCompleted(self, reason, diff):
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            self.onUpdated()

    def __initBalanceCurrencies(self):
        self.__updateBalanceCurrencies()
        self.onBalanceUpdated()

    def __updateBalanceCurrencies(self):
        self.__balance = self.__itemsCache.items.stats.getDynamicMoney()

    def __onBalanceUpdate(self, *_):
        self.__updateBalanceCurrencies()
        self.onPriceInfoUpdated()

    def __updateDynamicCurrencies(self, currencies):
        if BR_COIN not in currencies and STP_COIN not in currencies:
            return False
        brCoin = currencies.get(BR_COIN, 0)
        stpCoin = currencies.get(STP_COIN, 0)
        if self.getBRCoinBalance(0) != brCoin or self.getSTPCoinBalance(0) != stpCoin:
            self.__onBalanceUpdate()
        self.onBalanceUpdated()

    def __updateBattleRoyale(self, _):
        self.onRentInfoUpdated()

    @server_settings.serverSettingsChangeListener(Configs.BATTLE_ROYALE_CONFIG.value)
    def __onServerSettingsChanged(self, diff):
        self.__readEconomics()
        self.onUpdated()

    def __addEventHandlers(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
        g_clientUpdateManager.addCallbacks({'stats.{}'.format(c):self.__onBalanceUpdate for c in _RENT_CURRENCIES})
        g_clientUpdateManager.addCallbacks({'battleRoyale': self.__updateBattleRoyale,
         'cache.dynamicCurrencies': self.__updateDynamicCurrencies})

    def __removeEventHandlers(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __runWatch(self):
        self.__clearRentWatchCallback()
        vehiclesIntCDs = set().union(*self.__rentWatcher.values())
        updateTime = float('inf')
        vehIntCDs = []
        for intCD in vehiclesIntCDs:
            rentTimeUpdate = self.__calculateVehicleRentTimeUpdate(intCD)
            if rentTimeUpdate > 0:
                if rentTimeUpdate < updateTime:
                    updateTime = rentTimeUpdate + 1
                    vehIntCDs = [intCD]
                elif rentTimeUpdate == updateTime:
                    vehIntCDs.append(intCD)

        if vehIntCDs:
            self.__rentWatchCallbackId = BigWorld.callback(updateTime, partial(self.__updateVehicleRentTime, vehIntCDs))

    def __calculateVehicleRentTimeUpdate(self, intCD):
        timeLeft = self.getRentTimeLeft(intCD)
        if timeLeft <= 0:
            return 0
        if timeLeft < time_utils.ONE_MINUTE:
            return timeLeft
        return timeLeft % time_utils.ONE_MINUTE or time_utils.ONE_MINUTE if timeLeft <= time_utils.ONE_DAY else timeLeft % time_utils.ONE_HOUR or time_utils.ONE_HOUR

    def __updateVehicleRentTime(self, vehIntCDs):
        self.__rentWatchCallbackId = None
        if not vehIntCDs:
            return
        else:
            for callback, intCDs in self.__rentWatcher.iteritems():
                for intCD in vehIntCDs:
                    if intCD in intCDs:
                        callback(intCD)
                        if self.__rentWatcherCurrentVehicleCallback:
                            self.__rentWatcherCurrentVehicleCallback()

            self.__runWatch()
            return

    def __clearRentWatchCallback(self):
        if self.__rentWatchCallbackId is not None:
            BigWorld.cancelCallback(self.__rentWatchCallbackId)
            self.__rentWatchCallbackId = None
        return

    def __clear(self):
        self.__clearRentWatchCallback()
        self.__removeEventHandlers()
        if self.__rentWatcher:
            self.__rentWatcher.clear()
            self.__rentWatcher = None
        self.__rentWatcherCurrentVehicleCallback = None
        self.__economics = None
        self.__balance = None
        return
