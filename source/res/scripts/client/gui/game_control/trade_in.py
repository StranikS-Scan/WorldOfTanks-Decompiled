# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/trade_in.py
import logging
from contextlib import contextmanager
import typing
from enum import Enum
from cache import cached_property
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus
from gui.shared.events import VehicleBuyEvent
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.money import Money, Currency, MONEY_ZERO_GOLD
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items import UNDEFINED_ITEM_CD
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from trade_in_common.constants_types import TradeInInfo, ConversionRule, CONFIG_NAME as TRADE_IN_CONFIG_NAME
if typing.TYPE_CHECKING:
    from typing import List, Set, Optional, Dict
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.server_events.event_items import Action
_logger = logging.getLogger(__name__)

class TradeInState(Enum):
    UNDEFINED = 0
    AVAILABLE = 1
    UNAVAILABLE = 2


class TradeInDiscounts(object):

    def __init__(self, minDiscountVehicleCD, minDiscountPrice, maxDiscountVehicleCD, maxDiscountPrice, freeExchange):
        self.minDiscountVehicleCD = minDiscountVehicleCD
        self.minDiscountPrice = minDiscountPrice
        self.maxDiscountVehicleCD = maxDiscountVehicleCD
        self.maxDiscountPrice = maxDiscountPrice
        self.freeExchange = freeExchange

    @property
    def hasMultipleTradeOffs(self):
        return self.minDiscountVehicleCD is not None and self.maxDiscountVehicleCD is not None and self.minDiscountVehicleCD != self.maxDiscountVehicleCD

    def __str__(self):
        return 'TradeInDiscounts [{}, {}, {}, {}, {}]'.format(self.minDiscountVehicleCD, self.minDiscountPrice, self.maxDiscountVehicleCD, self.maxDiscountPrice, self.freeExchange)

    def __eq__(self, other):
        return self.minDiscountVehicleCD == other.minDiscountVehicleCD and self.minDiscountPrice == other.minDiscountPrice and self.maxDiscountVehicleCD == other.maxDiscountVehicleCD and self.maxDiscountPrice == other.maxDiscountPrice and self.freeExchange == other.freeExchange


class TradeInConfig(object):
    lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self._config = self.lobbyContext.getServerSettings().getTradeInConfig()

    @cached_property
    def tradeInInfoList(self):
        tokens = self.itemsCache.items.tokens.getTokens()

        def tokenSatisfied(info):
            token = info.conversionRule.accessToken
            return True if not token else token in tokens

        rules = self._config.get('conversionRules', {})
        infos = (TradeInInfo(sellGroupId, buyGroupId, ConversionRule(*conversionRule)) for (sellGroupId, buyGroupId), conversionRule in rules.iteritems())
        return [ ti for ti in infos if tokenSatisfied(ti) ]

    @cached_property
    def allAccessTokenSet(self):
        rules = self._config.get('conversionRules', {})
        tokens = set()
        for conversionRule in rules.itervalues():
            token = ConversionRule(*conversionRule).accessToken
            if token:
                tokens.add(token)

        return tokens

    @cached_property
    def hasOfferVisibleForEveryone(self):
        rules = self._config.get('conversionRules', {})
        for conversionRule in rules.itervalues():
            if ConversionRule(*conversionRule).visibleToEveryone:
                return True

        return False

    def getVehiclesInGroup(self, groupId):
        groups = self._config.get('vehicleGroups', {})
        return groups.get(groupId, set())

    def getTradeInInfoByVehicleToSell(self, vehCD):
        for tradeInInfo in self.tradeInInfoList:
            sellGroupId = tradeInInfo.sellGroupId
            if vehCD in self.getVehiclesInGroup(sellGroupId):
                return tradeInInfo

        return None

    def getTradeInInfosByVehicleToBuy(self, vehCD):
        tradeInInfos = []
        for tradeInInfo in self.tradeInInfoList:
            buyGroupId = tradeInInfo.buyGroupId
            if vehCD in self.getVehiclesInGroup(buyGroupId):
                tradeInInfos.append(tradeInInfo)

        return tradeInInfos

    def getSellPriceFactorFor(self, vehCD):
        tradeInInfo = self.getTradeInInfoByVehicleToSell(vehCD)
        if tradeInInfo:
            if tradeInInfo.conversionRule.freeExchange:
                return 1.0
            return tradeInInfo.conversionRule.sellPriceFactor


class _TradeInInfoWithVehicles(object):

    def __init__(self, tradeInInfo, vehiclesCDs=None):
        if vehiclesCDs is None:
            vehiclesCDs = set()
        self.tradeInInfo = tradeInInfo
        self.vehiclesCDs = vehiclesCDs
        return


class _TradeInVehicle(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicleCD=UNDEFINED_ITEM_CD, possibleVehiclesToTradeInCDs=None):
        self.vehicleCD = vehicleCD
        self.possibleVehiclesToTradeInCDs = possibleVehiclesToTradeInCDs or set()

    def isSelected(self):
        return bool(self.vehicleCD)

    @property
    def vehicle(self):
        return None if not self.isSelected() else self.itemsCache.items.getItemByCD(self.vehicleCD)


class _TradeInVehicleToBuy(_TradeInVehicle):
    pass


class _TradeInVehicleToSell(_TradeInVehicle):

    def __init__(self, vehicleCD=UNDEFINED_ITEM_CD, possibleVehiclesToTradeInCDs=None, conversionRule=None):
        super(_TradeInVehicleToSell, self).__init__(vehicleCD, possibleVehiclesToTradeInCDs)
        self.conversionRule = conversionRule


class _TradeInEventBus(object):

    def __init__(self):
        self.events = set()
        self.lockLevel = 0

    @contextmanager
    def getTransaction(self):
        self.startTransaction()
        yield
        self.commitTransaction()

    def startTransaction(self):
        self.lockLevel += 1

    def commitTransaction(self, force=False):
        if self.lockLevel > 0:
            self.lockLevel -= 1
        if self.lockLevel == 0 or force:
            for ev in self.events:
                g_eventBus.handleEvent(ev)

            self.events.clear()
            self.lockLevel = 0

    def call(self, event):
        if self.lockLevel == 0:
            g_eventBus.handleEvent(event)
        else:
            self.events.add(event)


class TradeInController(ITradeInController):
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(TradeInController, self).__init__()
        self.__cache = {}
        self.__config = None
        self._vehicleToSellInfo = _TradeInVehicleToSell()
        self._vehicleToBuyInfo = _TradeInVehicleToBuy()
        self._cachedState = TradeInState.UNDEFINED
        self._eventBus = _TradeInEventBus()
        return

    def selectVehicleToBuy(self, vehCD):
        intCD = int(vehCD)
        oldCD = self._vehicleToBuyInfo.vehicleCD
        if not self.__canSetVehicleToBuy(intCD):
            _logger.error('%s, can not be set as active trade-in buy vehicle compact descriptor', intCD)
            return
        possibleVehiclesToSell = set()
        if intCD in self.getVehiclesToBuy(False):
            buyToSellConversionCache = self.__cache.get('buyToSellConversionCache', {})
            for _, vehToSell in buyToSellConversionCache.get(intCD, []):
                possibleVehiclesToSell.add(vehToSell.intCD)

        self._vehicleToBuyInfo = _TradeInVehicleToBuy(intCD, possibleVehiclesToSell)
        if intCD != oldCD:
            self._eventBus.call(VehicleBuyEvent(VehicleBuyEvent.VEHICLE_SELECTED))

    def getSelectedVehicleToBuy(self):
        return self._vehicleToBuyInfo.vehicle

    def selectVehicleToSell(self, vehCD):
        intCD = int(vehCD)
        oldCD = self._vehicleToSellInfo.vehicleCD
        if not self.__canSetVehicleToSell(intCD):
            _logger.error('%s, can not be set as active trade-off vehicle compact descriptor', intCD)
            return
        else:
            possibleVehiclesToBuyCDs = set()
            conversionRule = None
            if intCD in self.getVehiclesToSell(False):
                sellToBuyConversionCache = self.__cache.get('sellToBuyConversionCache', {})
                conversionRule, possibleVehiclesToBuy = sellToBuyConversionCache.get(intCD, (None, []))
                possibleVehiclesToBuyCDs = {v.intCD for v in possibleVehiclesToBuy}
            self._vehicleToSellInfo = _TradeInVehicleToSell(intCD, possibleVehiclesToBuyCDs, conversionRule)
            if intCD != oldCD:
                self._eventBus.call(VehicleBuyEvent(VehicleBuyEvent.VEHICLE_SELECTED))
            return

    def getSelectedVehicleToSell(self):
        return self._vehicleToSellInfo.vehicle

    def isEnabled(self):
        return bool(self.__config and self.__config.tradeInInfoList)

    def getActionExpirationTime(self):

        def tradeInActionFilter(act):
            return any((mod.getName() == 'tradein' for mod in act.getModifiers()))

        actions = self.eventsCache.getActions(tradeInActionFilter).values()
        for action in actions:
            return action.getFinishTime()

    def getTokenExpirationTime(self):
        tokens = self.getConfig().allAccessTokenSet
        availableTokens = [ token for token in tokens if self.itemsCache.items.tokens.isTokenAvailable(token) ]
        if not availableTokens:
            return 0
        minExpireTime = min((self.itemsCache.items.tokens.getTokenExpiryTime(token) for token in availableTokens))
        return minExpireTime

    def getExpirationTime(self):
        tokenExpirationTime = self.getTokenExpirationTime()
        actionExpirationTime = self.getActionExpirationTime()
        expirationTime = min(tokenExpirationTime, actionExpirationTime) or actionExpirationTime
        _logger.debug('TradeIn:getExpirationTime: %d', expirationTime)
        return expirationTime

    def getConfig(self):
        return self.__config

    def init(self):
        self.itemsCache.onSyncCompleted += self.__onSync
        g_clientUpdateManager.addCallbacks({'tokens': self._onTokensUpdated})

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.itemsCache.onSyncCompleted -= self.__onSync

    def onLobbyInited(self, event):
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__fillConfig()
        self.__fillCache()

    def onAvatarBecomePlayer(self):
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__clearConfig()
        self.__clearCache()

    def onDisconnected(self):
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__clearConfig()
        self.__clearCache()
        self._vehicleToBuyInfo = _TradeInVehicleToBuy()
        self._vehicleToSellInfo = _TradeInVehicleToSell()
        self._cachedState = TradeInState.UNDEFINED

    def getTradeInDiscounts(self, vehicle):
        if not vehicle.canTradeIn:
            return
        tradeInDiscountsCache = self.__cache.get('tradeInDiscounts', {})
        if vehicle.intCD in tradeInDiscountsCache:
            return tradeInDiscountsCache[vehicle.intCD]

        def goldGetter(price):
            return price.getSignValue(Currency.GOLD)

        vehToBuyPrice = Money(gold=int(vehicle.buyPrices.itemPrice.defPrice.gold))
        tradeInDiscounts = None
        buyToSellConversionCache = self.__cache.get('buyToSellConversionCache', {})
        for conversionRule, vehToSell in buyToSellConversionCache.get(vehicle.intCD, []):
            if not vehToSell.canTradeOff:
                continue
            vehToSellCD = vehToSell.intCD
            vehToSellPrice = min(vehToSell.tradeOffPrice, vehToBuyPrice, key=goldGetter)
            if conversionRule.freeExchange:
                vehToSellPrice = vehToBuyPrice
            if tradeInDiscounts is None:
                tradeInDiscounts = TradeInDiscounts(vehToSellCD, vehToSellPrice, vehToSellCD, vehToSellPrice, conversionRule.freeExchange)
                continue
            if goldGetter(tradeInDiscounts.minDiscountPrice) > goldGetter(vehToSellPrice):
                tradeInDiscounts.minDiscountPrice = vehToSellPrice
                tradeInDiscounts.minDiscountVehicleCD = vehToSellCD
            if goldGetter(tradeInDiscounts.maxDiscountPrice) < goldGetter(vehToSellPrice):
                tradeInDiscounts.maxDiscountPrice = vehToSellPrice
                tradeInDiscounts.maxDiscountVehicleCD = vehToSellCD
            tradeInDiscounts.freeExchange |= conversionRule.freeExchange

        if tradeInDiscounts:
            tradeInDiscountsCache[vehicle.intCD] = tradeInDiscounts
            return tradeInDiscounts
        else:
            return

    def getAllPossibleVehiclesToSell(self):
        return self.__cache.get('allVehiclesToSell', set())

    def getAllPossibleVehiclesToBuy(self):
        return self.__cache.get('allVehiclesToBuy', set())

    def getPossibleVehiclesToBuy(self):
        return self.__cache.get('possibleVehiclesToBuy', set())

    def getVehiclesToSell(self, respectSelectedVehicleToBuy):
        return self.itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.CAN_TRADE_OFF | REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(self._vehicleToBuyInfo.possibleVehiclesToTradeInCDs) | REQ_CRITERIA.VEHICLE.ACTIVE_IN_NATION_GROUP) if respectSelectedVehicleToBuy and self._vehicleToBuyInfo.isSelected() else self.itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.CAN_TRADE_OFF | REQ_CRITERIA.VEHICLE.ACTIVE_IN_NATION_GROUP)

    def getVehiclesToBuy(self, respectSelectedVehicleToSell):
        return self.itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.CAN_TRADE_IN | REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(self._vehicleToSellInfo.possibleVehiclesToTradeInCDs) | REQ_CRITERIA.VEHICLE.ACTIVE_IN_NATION_GROUP) if respectSelectedVehicleToSell and self._vehicleToSellInfo.isSelected() else self.itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.CAN_TRADE_IN | REQ_CRITERIA.VEHICLE.ACTIVE_IN_NATION_GROUP | REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(self.getPossibleVehiclesToBuy()))

    def validatePossibleVehicleToBuy(self, vehicle):
        return vehicle.intCD in self._vehicleToSellInfo.possibleVehiclesToTradeInCDs

    def getTradeInPrice(self, veh):
        price = veh.buyPrices.itemPrice.price
        defPrice = veh.buyPrices.itemPrice.defPrice
        if self.validatePossibleVehicleToBuy(veh):
            if self._vehicleToSellInfo.conversionRule.freeExchange:
                price = MONEY_ZERO_GOLD
            else:
                price = max(MONEY_ZERO_GOLD, defPrice - self.getSelectedVehicleToSell().tradeOffPrice)
        return ItemPrice(price, defPrice)

    def addTradeInPriceIfNeeded(self, vehicle, money):
        tradeInDiscounts = self.getTradeInDiscounts(vehicle)
        if tradeInDiscounts is not None:
            if tradeInDiscounts.freeExchange:
                return vehicle.buyPrices.itemPrice.price
            money += tradeInDiscounts.maxDiscountPrice
        return money

    def __changeCachedState(self, newState):
        if self._cachedState != newState:
            showSystemMessage = self._cachedState != TradeInState.UNDEFINED
            self._cachedState = newState
            if not showSystemMessage:
                return
            if newState == TradeInState.AVAILABLE:
                _logger.info('Trade-in offer found. You can now trade-in available vehicles.')
                SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.vehicle_trade_in.offer_available()), type=SystemMessages.SM_TYPE.Information, priority=NotificationPriorityLevel.MEDIUM)
            else:
                _logger.info('Trade-in offers are no longer available.')
                SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.vehicle_trade_in.offer_unavailable()), type=SystemMessages.SM_TYPE.Information, priority=NotificationPriorityLevel.MEDIUM)

    def __fillConfig(self):
        self.__config = TradeInConfig()

    def __clearConfig(self):
        self.__config = None
        return

    def __clearCache(self):
        self.__cache = {}

    def __fillCache(self):
        _logger.info('Trade-in cache is rebuilt')
        self.__clearCache()
        if not self.isEnabled():
            self.__changeCachedState(TradeInState.UNAVAILABLE)
            return
        else:
            self.__cache['tradeInDiscounts'] = {}
            self.__cache['allVehiclesToSell'] = allVehiclesToSell = set()
            self.__cache['allVehiclesToBuy'] = allVehiclesToBuy = set()
            self.__cache['possibleVehiclesToBuy'] = possibleVehiclesToBuy = set()
            self.__cache['sellToBuyConversionCache'] = sellToBuyConversionCache = {}
            self.__cache['buyToSellConversionCache'] = buyToSellConversionCache = {}
            for tradeInInfo in self.__config.tradeInInfoList:
                vehiclesToSellCDs = self.__config.getVehiclesInGroup(tradeInInfo.sellGroupId)
                allVehiclesToSell |= vehiclesToSellCDs
                vehicleToSellItems = self.itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(vehiclesToSellCDs))
                vehicleToBuyCDs = self.__config.getVehiclesInGroup(tradeInInfo.buyGroupId)
                if tradeInInfo.conversionRule.allowToBuyNotInShopVehicles:
                    vehicleToBuyItems = self.itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(vehicleToBuyCDs))
                else:
                    vehicleToBuyItems = self.itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(vehicleToBuyCDs) | ~REQ_CRITERIA.HIDDEN)
                vehicleToBuyCDs = set(vehicleToBuyItems.keys())
                if tradeInInfo.conversionRule.visibleToEveryone:
                    allVehiclesToBuy |= vehicleToBuyCDs
                for vehToSell in vehicleToSellItems.itervalues():
                    vehsToBuy = []
                    for vehToBuy in vehicleToBuyItems.itervalues():
                        if tradeInInfo.conversionRule.checkVehicleAscendingLevels:
                            if vehToSell.level > vehToBuy.level:
                                continue
                        buyToSellConversion = buyToSellConversionCache.setdefault(vehToBuy.intCD, [])
                        buyToSellConversion.append((tradeInInfo.conversionRule, vehToSell))
                        vehsToBuy.append(vehToBuy)

                    if vehsToBuy:
                        sellToBuyConversionCache[vehToSell.intCD] = (tradeInInfo.conversionRule, vehsToBuy)

            for intCD in self.getVehiclesToSell(False):
                _, vehiclesToBuy = sellToBuyConversionCache.get(intCD, (None, []))
                possibleVehiclesToBuy |= {v.intCD for v in vehiclesToBuy}

            allVehiclesToBuy |= possibleVehiclesToBuy
            self.__changeCachedState(TradeInState.AVAILABLE if self.hasAvailableOffer() else TradeInState.UNAVAILABLE)
            return

    def __resetSelectedVehiclesIfNeeded(self):
        with self._eventBus.getTransaction():
            vehToSell = self.getSelectedVehicleToSell()
            if vehToSell is not None and self.__canSetVehicleToSell(vehToSell.intCD):
                self.selectVehicleToSell(vehToSell.intCD)
            if not self.isEnabled() or vehToSell is None or vehToSell.intCD not in self.getVehiclesToSell(False):
                self.selectVehicleToSell(UNDEFINED_ITEM_CD)
            vehToBuy = self.getSelectedVehicleToBuy()
            if vehToBuy is not None and self.__canSetVehicleToBuy(vehToBuy.intCD):
                self.selectVehicleToBuy(vehToBuy.intCD)
            if not self.isEnabled() or vehToBuy is None or vehToBuy.intCD not in self.getVehiclesToBuy(False):
                self.selectVehicleToBuy(UNDEFINED_ITEM_CD)
        return

    def hasAvailableOffer(self):
        return bool(self.getConfig().hasOfferVisibleForEveryone or self.getVehiclesToSell(False))

    def __onServerSettingsChanged(self, diff):
        if TRADE_IN_CONFIG_NAME in diff:
            with self._eventBus.getTransaction():
                self.__fillConfig()
                self.__fillCache()
                self.__resetSelectedVehiclesIfNeeded()
                self._eventBus.call(VehicleBuyEvent(VehicleBuyEvent.VEHICLE_SELECTED))

    def __onSync(self, updateReason, diff):
        if updateReason == CACHE_SYNC_REASON.CLIENT_UPDATE:
            if diff is not None and GUI_ITEM_TYPE.VEHICLE in diff:
                with self._eventBus.getTransaction():
                    self.__fillConfig()
                    self.__fillCache()
                    self.__resetSelectedVehiclesIfNeeded()
                    self._eventBus.call(VehicleBuyEvent(VehicleBuyEvent.VEHICLE_SELECTED))
        return

    def _onTokensUpdated(self, diff):
        if not self.isEnabled():
            return
        modifiedTokens = set(diff.iterkeys())
        accessTokens = self.getConfig().allAccessTokenSet
        if accessTokens & modifiedTokens:
            with self._eventBus.getTransaction():
                self.__fillConfig()
                self.__fillCache()
                self.__resetSelectedVehiclesIfNeeded()
                self._eventBus.call(VehicleBuyEvent(VehicleBuyEvent.VEHICLE_SELECTED))

    def __canSetVehicleToSell(self, newVehicleToSellCD):
        return newVehicleToSellCD == UNDEFINED_ITEM_CD or newVehicleToSellCD in self.getVehiclesToSell(False)

    def __canSetVehicleToBuy(self, newVehicleToBuyCD):
        return newVehicleToBuyCD == UNDEFINED_ITEM_CD or newVehicleToBuyCD in self.getVehiclesToBuy(False)
