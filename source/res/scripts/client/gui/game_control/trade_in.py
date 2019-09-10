# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/trade_in.py
import logging
from collections import namedtuple
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared import g_eventBus
from gui.shared.events import VehicleBuyEvent
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.money import Currency
from helpers import dependency
from items import UNDEFINED_ITEM_CD
from shared_utils import first
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class TradeInInfo(namedtuple('TradeInInfo', ['minDiscountVehicleCD',
 'minDiscountPrice',
 'maxDiscountVehicleCD',
 'maxDiscountPrice'])):

    @property
    def hasMultipleTradeOffs(self):
        return self.minDiscountVehicleCD is not None and self.maxDiscountVehicleCD is not None and self.minDiscountVehicleCD != self.maxDiscountVehicleCD


class TradeInController(ITradeInController):
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(TradeInController, self).__init__()
        self.__cache = {}
        self.__config = None
        self.__minLevel = 0
        self.__activeTradeOffCD = UNDEFINED_ITEM_CD
        return

    def init(self):
        self.itemsCache.onSyncCompleted += self.__onSync
        g_clientUpdateManager.addCallbacks({'inventory.1': self.__onVehicleUpdate})

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.itemsCache.onSyncCompleted -= self.__onSync

    def onLobbyInited(self, event):
        self.__fillConfig()
        self.__fillCache()

    def onAvatarBecomePlayer(self):
        self.__clearConfig()
        self.__clearCache()

    def onDisconnected(self):
        self.__clearConfig()
        self.__clearCache()
        self.__activeTradeOffCD = UNDEFINED_ITEM_CD

    def getActiveTradeOffVehicle(self):
        return first(self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.IN_CD_LIST([self.__activeTradeOffCD])).values()) if self.__activeTradeOffCD else None

    def getActiveTradeOffVehicleCD(self):
        return self.__activeTradeOffCD

    def setActiveTradeOffVehicleCD(self, value):
        intCD = int(value)
        oldCD = self.__activeTradeOffCD
        if self.__canSetActiveTradeOffVehicle(intCD):
            self.__activeTradeOffCD = intCD
            if self.__activeTradeOffCD != oldCD:
                g_eventBus.handleEvent(VehicleBuyEvent(VehicleBuyEvent.VEHICLE_SELECTED))
        else:
            _logger.error('%s, can not be set as active trade-off vehicle compact descriptor', intCD)

    def getActiveTradeOffVehicleState(self):
        activeTradeOffVehicle = self.getActiveTradeOffVehicle()
        return (None, None) if activeTradeOffVehicle is None else activeTradeOffVehicle.getState()

    def getTradeInInfo(self, vehicle):
        if not vehicle.canTradeIn:
            return None
        else:
            level = vehicle.level
            return self.__cache[level]

    def getStartEndTimestamps(self):
        if self.isEnabled():
            actions = self.eventsCache.getTradeInActions()
            if actions:
                return (min((a.getStartTimeRaw() for a in actions)), max((a.getFinishTimeRaw() for a in actions)))

    def getMinAcceptableSellPrice(self):
        return self.__config.minAcceptableSellPrice if self.isEnabled() else 0

    def getAllowedVehicleLevels(self, maxLevel=None):
        levels = tuple(self.__config.allowedVehicleLevels)
        minLevel = min(levels)
        if maxLevel is None:
            maxLevel = max(levels)
        elif maxLevel < minLevel:
            maxLevel = minLevel
        return sorted((level for level in levels if minLevel <= level <= maxLevel))

    def getTradeOffVehicles(self, maxLevel=None):
        tradeInLevels = self.getAllowedVehicleLevels(maxLevel)
        return self.itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.CAN_TRADE_OFF | REQ_CRITERIA.VEHICLE.LEVELS(tradeInLevels) | REQ_CRITERIA.VEHICLE.ACTIVE_IN_NATION_GROUP)

    def tradeOffSelectedApplicableForLevel(self, maxLevel):
        return self.__activeTradeOffCD != UNDEFINED_ITEM_CD and self.__activeTradeOffCD in (self.getTradeOffVehicles(maxLevel) or [])

    def isEnabled(self):
        return self.__config.isEnabled

    def getTradeInPrice(self, vehicle):
        price = vehicle.buyPrices.itemPrice.price
        defPrice = vehicle.buyPrices.itemPrice.defPrice
        if self.isEnabled() and self.__activeTradeOffCD in self.getTradeOffVehicles(vehicle.level):
            price = defPrice - self.getActiveTradeOffVehicle().tradeOffPrice
        return ItemPrice(price, defPrice)

    def addTradeInPriceIfNeeded(self, vehicle, money):
        if vehicle.canTradeIn:
            tradeInInfo = self.getTradeInInfo(vehicle)
            if tradeInInfo is not None:
                money += tradeInInfo.maxDiscountPrice
        return money

    def __fillConfig(self):
        self.__config = self.itemsCache.items.shop.tradeIn

    def __clearConfig(self):
        self.__config = None
        return

    def __clearCache(self):
        self.__cache = {}

    def __fillCache(self):
        self.__clearCache()
        if self.isEnabled():
            for level in self.__config.allowedVehicleLevels:
                vehicles = self.getTradeOffVehicles(level)
                if not vehicles:
                    self.__cache[level] = None

                def goldGetter(item):
                    return item.tradeOffPrice.getSignValue(Currency.GOLD)

                minVehicle = min(vehicles.itervalues(), key=goldGetter)
                maxVehicle = max(vehicles.itervalues(), key=goldGetter)
                self.__cache[level] = TradeInInfo(minVehicle.intCD, minVehicle.tradeOffPrice, maxVehicle.intCD, maxVehicle.tradeOffPrice)

        return

    def __resetActiveTradeOffIfNeeded(self):
        active = self.getActiveTradeOffVehicle()
        if not self.isEnabled() or active is None or active.intCD not in self.getTradeOffVehicles():
            self.setActiveTradeOffVehicleCD(UNDEFINED_ITEM_CD)
        return

    def __onSync(self, updateReason, _=None):
        if updateReason in (CACHE_SYNC_REASON.SHOP_RESYNC, CACHE_SYNC_REASON.INVENTORY_RESYNC):
            self.__fillConfig()
            self.__fillCache()
            self.__resetActiveTradeOffIfNeeded()

    def __onVehicleUpdate(self, _=None):
        self.__fillConfig()
        self.__fillCache()
        self.__resetActiveTradeOffIfNeeded()

    def __canSetActiveTradeOffVehicle(self, newTradeOffCD):
        return newTradeOffCD == UNDEFINED_ITEM_CD or newTradeOffCD in self.getTradeOffVehicles()
