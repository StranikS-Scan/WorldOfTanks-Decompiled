# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/vehicles_controller.py
import logging
import BigWorld
import Event
from adisp import async
from items import vehicles
from helpers import dependency
from helpers.time_utils import makeLocalServerTime, getTimeDeltaFromNow
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.shared.gui_items.processors import Processor, plugins, makeI18nError, makeI18nSuccess
from gui.shared.money import Money
from gui.shared.formatters import formatPrice
from gui.shared.utils import decorators
from gui.doc_loaders.hw19_vehicle_settings import EventVehicleSettings
from constants import HE19EnergyPurposes, HE19_NO_ENERGY_TOKEN, HE19_ENERGY_FOR_USE_TOKEN, HE19_ENERGY_USED_FOR_TOKEN, HE19_NO_ENERGY_TOKEN_PREFIX, HE19_USE_ENERGY_TOKEN_PREFIX
from gui.ClientUpdateManager import g_clientUpdateManager
_logger = logging.getLogger(__name__)
_UPDATE_INTERVAL = 1
_DEFAULT_DISCOUNT_COEF = 1.0
_ZERO_TIMER_ERROR_CODE = -1
_ZERO_TIMER_ERROR_STR = 'has_energy'

class VehiclesController(object):
    INVALID_TIME = -1
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(VehiclesController, self).__init__()
        self._eventsManager = Event.EventManager()
        self.onTimeToRepairChanged = Event.Event(self._eventsManager)
        self.__vehiclesTime = {}
        self.__updateCB = None
        self.__eventVehicles = None
        self.__eventVehiclesWithoutEnergy = set()
        self.__vehicleSettings = None
        return

    @property
    def vehiclesTime(self):
        return self.__vehiclesTime

    def start(self):
        self.__updateCB = BigWorld.callback(_UPDATE_INTERVAL, self.__update)
        self.__eventVehicles = self.eventsCache.getGameEventData().get('vehicles', {})
        self.__vehicleSettings = EventVehicleSettings()
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__update()

    def stop(self):
        self._eventsManager.clear()
        if self.__updateCB:
            BigWorld.cancelCallback(self.__updateCB)
            self.__updateCB = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        return

    def isEnabled(self):
        return self._getEnergyConfig().get('enabled', False)

    def hasEnergyFor(self, purpose):
        return self._getTokenCount(HE19_ENERGY_FOR_USE_TOKEN.format(purpose)) > 0

    def getEnergyFor(self, purpose):
        return self._getTokenCount(HE19_ENERGY_FOR_USE_TOKEN.format(purpose))

    def hasEnergy(self, purpose, vehTypeCompDescr):
        return False if not self._isEventVehicleCanHaveEnergy(purpose, vehTypeCompDescr) else self._getTokenCount(HE19_NO_ENERGY_TOKEN.format(purpose, vehTypeCompDescr)) == 0

    def isEventVehicleCanHaveEnergy(self, purpose, vehTypeCompDescr):
        return self._isEventVehicleCanHaveEnergy(purpose, vehTypeCompDescr)

    def isEventVehicleHasToken(self, purpose, vehTypeCompDescr):
        return self._getTokenCount(HE19_NO_ENERGY_TOKEN.format(purpose, vehTypeCompDescr)) > 0

    def getVehiclesOrder(self):
        return [ veh['id'] for veh in sorted(self.__vehicleSettings.getVehiclesSettings().values(), key=lambda v: v['weight']) ]

    def getVehiclesForRent(self):
        eventsData = self.eventsCache.getGameEventData()
        return eventsData.get('vehiclesForRent', {})

    def getVehicleSettings(self):
        return self.__vehicleSettings

    def getTimeToRecharge(self, purpose, vehTypeCompDescr):
        expireTime = 0
        if self.isEnabled():
            expireTime = self.eventsCache.questsProgress.getTokenExpiryTime(HE19_NO_ENERGY_TOKEN.format(purpose, vehTypeCompDescr))
        return makeLocalServerTime(expireTime)

    def getEnergyPrice(self, purpose, vehTypeCompDescr):
        if not self.isEnabled():
            return (None, None)
        else:
            settings = self._getCurrentEnergySettings(purpose, vehTypeCompDescr)
            return (None, None) if settings is None else settings['price']

    def getCurrentEnergySettings(self, purpose, vehTypeCompDescr):
        return self._getEnergySettings(purpose, vehTypeCompDescr, self._getCurrentAttempt(vehTypeCompDescr) + 1)

    def getCurrentAttempt(self, purpose):
        return self._getTokenCount(HE19_ENERGY_USED_FOR_TOKEN.format(purpose))

    def getAllVehiclesInInventory(self):
        vehiclesAvailble = [ self.itemsCache.items.getItemByCD(cd) for cd in self.getVehiclesOrder() ]
        return [ v.intCD for v in vehiclesAvailble if v.isInInventory ]

    def getAvailableVehiclesInInventory(self):
        vehiclesInInventory = self.getAllVehiclesInInventory()
        return [ compDesc for compDesc in vehiclesInInventory if self.hasEnergy(purpose=HE19EnergyPurposes.healing.name, vehTypeCompDescr=compDesc) ]

    @async
    @decorators.process('buyEnergy')
    def buyEnergy(self, purpose, vehTypeCompDescr, callback):
        currency, amount = self.getEnergyPrice(purpose, vehTypeCompDescr)
        if currency is None or amount is None:
            callback(False)
            return
        else:
            result = yield BuyEnergyProcessor(self, purpose, currency, amount, vehTypeCompDescr).request()
            if result.userMsg:
                SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
            callback(result.success)
            return

    @decorators.process('updating')
    def applyCommanderHealing(self, purpose, vehTypeCompDescr):
        result = yield ExchangeToCommanderHealingProcessor(self, purpose, vehTypeCompDescr).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('updating')
    def applyCommanderBooster(self, purpose, vehTypeCompDescr):
        result = yield ExchangeToCommanderBoosterProcessor(self, purpose, vehTypeCompDescr).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def getUnlockTokenFor(self, vehTypeCompDescr):
        return None if vehTypeCompDescr not in self.getVehiclesForRent() else self.getVehiclesForRent()[vehTypeCompDescr].get('token', None)

    def getRentBonusQuest(self, vehTypeCompDescr):
        if vehTypeCompDescr not in self.getVehiclesForRent():
            return
        else:
            questID = self.getVehiclesForRent()[vehTypeCompDescr].get('bonusQuestId', None)
            return None if questID is None else self.eventsCache.getHiddenQuests().get(questID, None)

    def _isEventVehicleCanHaveEnergy(self, purpose, vehTypeCompDescr):
        return vehTypeCompDescr in self._getAttemptSettingsPerDayFor(purpose)

    def _getTokenCount(self, token):
        return 0 if not self.isEnabled() else self.eventsCache.questsProgress.getTokenCount(token)

    def _getEnergyConfig(self):
        return self.eventsCache.getGameEventData().get('energy', {})

    def _getCurrentEnergySettings(self, purpose, vehTypeCompDescr):
        attempt = self._getCurrentAttempt(purpose) + 1
        return self._getEnergySettings(purpose, vehTypeCompDescr, attempt)

    def _getCurrentAttempt(self, purpose):
        return self._getTokenCount(HE19_ENERGY_USED_FOR_TOKEN.format(purpose))

    def _getAttemptSettingsForVehicle(self, purpose, vehTypeCompDescr):
        return self._getAttemptSettingsPerDayFor(purpose).get(vehTypeCompDescr, [])

    def _getAttemptSettingsPerDayFor(self, purpose):
        config = self._getAttemptSettingsPerDay()
        return config.get(purpose, {})

    def _getAttemptSettingsPerDay(self):
        config = self._getEnergyConfig()
        return config.get('attemptSettingsPerDay', {})

    def _getEnergySettings(self, purpose, vehTypeCompDescr, attempt):
        if not self.isEnabled():
            return None
        else:
            settings = self._getAttemptSettingsForVehicle(purpose, vehTypeCompDescr)
            if not settings:
                return None
            return settings[-1] if attempt >= len(settings) else settings[attempt]

    def __onTokensUpdate(self, diff):
        if self._isEnergyTokensFounded(diff):
            self.__update()

    def _isEnergyTokensFounded(self, tokens):
        return any((True for token in tokens if token.startswith((HE19_NO_ENERGY_TOKEN_PREFIX, HE19_USE_ENERGY_TOKEN_PREFIX, 'img:{}'.format(HE19_USE_ENERGY_TOKEN_PREFIX)))))

    def __update(self, timerID=None):
        if timerID is None and self.__updateCB is not None:
            BigWorld.cancelCallback(self.__updateCB)
            self.__updateCB = None
        if not self.eventsCache.isEventEnabled():
            return
        else:
            if self.__vehiclesTime:
                self.__vehiclesTime = {}
            purpose = HE19EnergyPurposes.healing.name
            for vehicle in self.__eventVehicles:
                if not self.hasEnergy(purpose, vehicle):
                    self.__eventVehiclesWithoutEnergy.add(vehicle)
                    self.__vehiclesTime[vehicle] = getTimeDeltaFromNow(self.getTimeToRecharge(purpose, vehicle))
                if vehicle in self.__eventVehiclesWithoutEnergy:
                    self.__eventVehiclesWithoutEnergy.discard(vehicle)
                    self.__vehiclesTime[vehicle] = self.INVALID_TIME

            if self.__vehiclesTime:
                self.onTimeToRepairChanged(self.__vehiclesTime)
                if any((value > 0 for value in self.__vehiclesTime.itervalues())):
                    self.__updateCB = BigWorld.callback(_UPDATE_INTERVAL, self.__update)
            return


class BuyEnergyProcessor(Processor):
    _SM_TYPE_FOR_PURPOSES = {HE19EnergyPurposes.healing.name: SM_TYPE.EventRepair,
     HE19EnergyPurposes.booster.name: SM_TYPE.EventBooster}

    def __init__(self, controller, purpose, currency, money, vehTypeCompDescr):
        super(BuyEnergyProcessor, self).__init__(plugins=(plugins.MoneyValidator(Money(**{currency: money})), plugins.CheckEnergy(controller, purpose, vehTypeCompDescr), plugins.VehicleInBattle()))
        self._controller = controller
        self._purpose = purpose
        self._currency = currency
        self._money = money
        self._vehTypeCompDescr = vehTypeCompDescr

    def _request(self, callback):
        BigWorld.player().buyHalloweenEnergy(self._vehTypeCompDescr, lambda code, errorCode: self._response(code, callback, errorCode), purpose=self._purpose)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('hw19_buy_energy/%s' % errStr, defaultSysMsgKey='hw19_buy_energy/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('hw19_buy_energy/success', money=formatPrice(Money(**{self._currency: self._money}), reverse=True, useStyle=True, currency=self._currency, useIcon=True), type=self._SM_TYPE_FOR_PURPOSES[self._purpose])


class ExchangeToCommanderHealingProcessor(Processor):

    def __init__(self, controller, purpose, vehTypeCompDescr):
        super(ExchangeToCommanderHealingProcessor, self).__init__(plugins=(plugins.CheckEnergy(controller, purpose, vehTypeCompDescr), plugins.CheckEnergyItemsForExchange(controller, purpose), plugins.VehicleInBattle()))
        self._controller = controller
        self._vehTypeCompDescr = vehTypeCompDescr
        self._vehicleName = vehicles.getVehicleType(self._vehTypeCompDescr).shortUserString

    def _request(self, callback):
        BigWorld.player().exchangeToCommanderHealing(self._vehTypeCompDescr, lambda code, errorCode: self._response(code, callback, errorCode))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('hw19_draw_energy/%s' % errStr, defaultSysMsgKey='hw19_draw_energy/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('hw19_draw_energy/success', vehicle=self._vehicleName, type=SM_TYPE.EventRestore)


class ExchangeToCommanderBoosterProcessor(ExchangeToCommanderHealingProcessor):

    def _request(self, callback):
        BigWorld.player().exchangeToCommanderBooster(self._vehTypeCompDescr, lambda code, errorCode: self._response(code, callback, errorCode))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('hw19_lock_energy/%s' % errStr, defaultSysMsgKey='hw19_lock_energy/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('hw19_lock_energy/success', vehicle=self._vehicleName, type=SM_TYPE.EventBoosterActivated)


class VehicleItemBuyer(Processor):

    def __init__(self, vehTypeCompDescr, currency, price):
        super(VehicleItemBuyer, self).__init__(plugins=(plugins.MoneyValidator(Money(**{currency: price})),))
        self._vehTypeCompDescr = vehTypeCompDescr
        self._price = price

    def _request(self, callback):
        _logger.debug('Make server request to buy vehicle %d for: %d ', self._vehTypeCompDescr, self._price)
        BigWorld.player().rentHalloweenVehicle(self._vehTypeCompDescr, lambda code, errorCode: self._response(code, callback, errorCode))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('hw19_vehicle/%s' % errStr, defaultSysMsgKey='hw19/server_error')
