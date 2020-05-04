# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/hero_tank.py
from Event import Event
from gui.ClientUpdateManager import g_clientUpdateManager
from helpers import dependency
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_MAX_DISCOUNT = 100

class EventHeroTank(object):
    __slots__ = ('onDiscountChanged',)
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)
    tradeIn = dependency.descriptor(ITradeInController)

    def __init__(self):
        super(EventHeroTank, self).__init__()
        self.onDiscountChanged = Event()

    def getVehicleCD(self):
        return self._getHeroTankData().get('vehicleCD', None)

    def getDiscountTokens(self):
        return self._getHeroTankData().get('discounts', {})

    def getDiscount(self):
        discount = sum((min(self.getTokenCount(tokenID), discountInfo['maxCount']) * discountInfo['percent'] for tokenID, discountInfo in self.getDiscountTokens().iteritems()))
        return min(discount, _MAX_DISCOUNT)

    def getDefPrice(self):
        return self._getHeroTankData().get('price', {})

    def getCurrentPrice(self):
        currency, amount = self.getDefPrice()
        amount = int(round(amount * (1 - self.getDiscount() / float(_MAX_DISCOUNT))))
        return (currency, amount)

    def getMaxTokenCount(self, tokenID):
        return self.getDiscountTokens()[tokenID]['maxCount']

    def getTokenCount(self, tokenID):
        return self.eventsCache.questsProgress.getTokenCount(tokenID)

    def isEventHeroTank(self, vehicleCD):
        return vehicleCD == self.getVehicleCD()

    def isPurchased(self):
        return self.getInventoryItem().isPurchased

    def isRestore(self):
        return self.getInventoryItem().isRestorePossible()

    def getStockItem(self):
        return self.itemsCache.items.getStockVehicle(self.getVehicleCD(), useInventory=False)

    def getInventoryItem(self):
        return self.itemsCache.items.getItemByCD(self.getVehicleCD())

    def start(self):
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})

    def stop(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def wasBought(self):
        boughtTokenID = self._getHeroTankData().get('boughtTokenID', '')
        return self.getTokenCount(boughtTokenID) > 0

    def _getHeroTankData(self):
        eventData = self.eventsCache.getGameEventData()
        return eventData.get('heroVehicle', {})

    def __onTokensUpdate(self, diff):
        discountTokens = self.getDiscountTokens()
        for token in diff.iterkeys():
            if token in discountTokens:
                self.onDiscountChanged()
                return
