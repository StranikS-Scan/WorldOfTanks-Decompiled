# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/trade_in.py
from collections import namedtuple
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.shared import IItemsCache

class TradeInInfo(namedtuple('TradeInInfo', ['minDiscountVehicleCD',
 'minDiscountPrice',
 'maxDiscountVehicleCD',
 'maxDiscountPrice'])):
    """
    Vehicle trade in info:
    - vehicle to trade off with min discount price
    - vehicle to trade off with max discount price
    """

    @property
    def hasMultipleTradeOffs(self):
        """
        Has this trade in info sever vehicles to trade off
        """
        return self.minDiscountVehicleCD is not None and self.maxDiscountVehicleCD is not None and self.minDiscountVehicleCD != self.maxDiscountVehicleCD


class TradeInController(ITradeInController):
    """
    Controller is used to store information about Trade In and
    handle events from shop
    """
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(TradeInController, self).__init__()
        self.__cache = {}
        self.__config = None
        self.__minLevel = 0
        return

    def init(self):
        self.itemsCache.onSyncCompleted += self.__onSync
        g_clientUpdateManager.addCallbacks({'inventory.1': self.__onVehicleUpdate})

    def fini(self):
        self.itemsCache.onSyncCompleted -= self.__onSync
        g_clientUpdateManager.removeObjectCallbacks(self)

    def onLobbyInited(self, event):
        self.__fillConfig()
        self.__fillCache()

    def onAvatarBecomePlayer(self):
        self.__clearConfig()
        self.__clearCache()

    def onDisconnected(self):
        self.__clearConfig()
        self.__clearCache()

    def getTradeInInfo(self, vehicle):
        """
        Gets information about trade in for given vehicle.
        :param vehicle: vehicle item
        :return: trade in info
        """
        if not vehicle.canTradeIn:
            return None
        else:
            level = vehicle.level
            return self.__cache[level]

    def getTradeOffVehicles(self, level):
        """
        Gets vehicles available to trade off to given level.
        """
        levels = self.__config.allowedVehicleLevels
        tradeInLevels = range(min(levels), level + 1)
        return self.itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.CAN_TRADE_OFF | REQ_CRITERIA.VEHICLE.LEVELS(tradeInLevels))

    def isEnabled(self):
        return self.__config.isEnabled

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
        """
        Fills cache with trade in infos by vehicle levels
        """
        self.__clearCache()
        if self.isEnabled():
            for level in self.__config.allowedVehicleLevels:
                vehicles = self.getTradeOffVehicles(level)
                if not vehicles:
                    self.__cache[level] = None

                def goldGetter(item):
                    return item.tradeOffPrice.gold

                minVehicle = min(vehicles.itervalues(), key=goldGetter)
                maxVehicle = max(vehicles.itervalues(), key=goldGetter)
                self.__cache[level] = TradeInInfo(minVehicle.intCD, minVehicle.tradeOffPrice, maxVehicle.intCD, maxVehicle.tradeOffPrice)

        return

    def __onSync(self, updateReason, invalidItems):
        if updateReason == CACHE_SYNC_REASON.SHOP_RESYNC:
            self.__fillConfig()
            self.__fillCache()

    def __onVehicleUpdate(self, diff):
        self.__fillConfig()
        self.__fillCache()
