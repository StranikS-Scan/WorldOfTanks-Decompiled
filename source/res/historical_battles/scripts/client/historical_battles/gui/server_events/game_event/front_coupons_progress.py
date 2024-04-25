# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/server_events/game_event/front_coupons_progress.py
from collections import defaultdict
from historical_battles.gui.server_events.game_event.game_event_progress import ProgressItemsController
from helpers import dependency
from historical_battles.gui.server_events.game_event.front_coupon_item import getGroupedItem, FrontCouponItem
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from shared_utils import findFirst, first

class FrontCouponsProgressItemsController(ProgressItemsController):
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        super(FrontCouponsProgressItemsController, self).__init__()
        self._groupedItems = []

    def stop(self):
        super(FrontCouponsProgressItemsController, self).stop()
        self._groupedItems[:] = []

    def getInstanceClass(self):
        return FrontCouponItem

    def getActiveItemIDs(self):
        return self._gameEventController.frontCoupons.getFrontCouponsConfig().keys()

    def getGroupedFrontCoupons(self):
        return self._groupedItems

    def getActiveFrontCoupon(self):
        return findFirst(lambda frontCoupon: frontCoupon.getCurrentCount() > 0, self._groupedItems[::-1])

    def getRechargeableFrontCoupon(self):
        frontCoupons = [ frontCoupon for frontCoupon in self._groupedItems if frontCoupon.getNextRechargeTime() > 0 ]
        return first(sorted(frontCoupons, key=lambda e: e.getNextRechargeTime()))

    def _onSyncCompleted(self):
        super(FrontCouponsProgressItemsController, self)._onSyncCompleted()
        self._rebuildGroupedItems()

    def _rebuildGroupedItems(self):
        self._groupedItems[:] = []
        items = defaultdict(list)
        for item in self._getSortedItems():
            modifier = item.getModifier()
            if modifier:
                items[modifier].append(item)

        for modifier in sorted(items.keys()):
            if items.get(modifier):
                self._groupedItems.append(getGroupedItem(items.get(modifier)))

    def _getSortedItems(self):
        return sorted((frontCoupon for frontCoupon in self.getItems().values()), key=self._getOrder)

    def _getOrder(self, frontCoupon):
        usageOrder = self._gameEventController.frontCoupons.getUsageOrder()
        return usageOrder.index(frontCoupon.getFrontCouponID())
