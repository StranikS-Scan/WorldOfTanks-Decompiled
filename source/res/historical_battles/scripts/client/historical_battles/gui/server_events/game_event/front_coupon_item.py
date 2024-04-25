# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/server_events/game_event/front_coupon_item.py
import BigWorld
from Event import Event, EventManager
from helpers import dependency, time_utils
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles_common.hb_constants import FRONT_COUPON_RECHARGE_QUEST_GROUP_ID, RESERVED_FRONT_COUPON_SUFFIX
from historical_battles_common.helpers_common import getFrontCouponModifier
from shared_utils import first
from skeletons.gui.server_events import IEventsCache

class BaseFrontCoupon(object):

    def getLabel(self):
        raise NotImplementedError

    def getModifier(self):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def isDrawActive(self):
        raise NotImplementedError

    def isActive(self):
        raise NotImplementedError

    def getMaxCount(self):
        raise NotImplementedError

    def getCurrentCount(self):
        raise NotImplementedError

    def getNextRechargeTime(self):
        raise NotImplementedError

    def needToShowAnimation(self):
        raise NotImplementedError


class FrontCouponItem(BaseFrontCoupon):
    eventsCache = dependency.descriptor(IEventsCache)
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, frontCouponID):
        self._em = EventManager()
        self.onItemsUpdated = Event(self._em)
        self._frontCouponID = frontCouponID
        self._currentCount = 0
        self._modifier = getFrontCouponModifier(frontCouponID)

    def getFrontCouponID(self):
        return self._frontCouponID

    def getLabel(self):
        return 'x' + str(self._modifier)

    def getModifier(self):
        return self._modifier

    def init(self):
        self.eventsCache.onSyncCompleted += self._onSyncCompleted
        self._onSyncCompleted()

    def fini(self):
        self.eventsCache.onSyncCompleted -= self._onSyncCompleted
        self._em.clear()

    def isDrawActive(self):
        data = self._getFrontCouponConfig()
        return data.get('drawActive', False)

    def isActive(self):
        activeFrontCoupon = self.gameEventController.frontCoupons.getActiveFrontCoupon()
        return activeFrontCoupon is not None and self.getLabel() == activeFrontCoupon.getLabel()

    def getMaxCount(self):
        return self._getFrontCouponConfig().get('maxCount', 0)

    def getCurrentCount(self):
        if not self.isDrawActive():
            return 0
        count = self.eventsCache.questsProgress.getTokenCount(self._frontCouponID)
        reservedFrontCouponID = self._frontCouponID + RESERVED_FRONT_COUPON_SUFFIX
        reservedCount = self.eventsCache.questsProgress.getTokenCount(reservedFrontCouponID)
        currentCount = max(count - reservedCount, 0)
        return min(currentCount, self.getMaxCount())

    def getNextRechargeTime(self):
        quest = self._getFirstActiveDailyQuest()
        if quest is None:
            return 0
        else:
            currentDayUTC = time_utils.getServerTimeCurrentDay()
            dailyProgressResetTimeUTC = self._getDailyProgressResetTimeUTC()
            untilRest = (dailyProgressResetTimeUTC - currentDayUTC) % time_utils.ONE_DAY
            return untilRest

    def needToShowAnimation(self):
        viewedFrontCoupons = self.gameEventController.frontCoupons.getViewedFrontCoupons()
        viewedCount = viewedFrontCoupons.get(self.getFrontCouponID(), 0)
        return self.getCurrentCount() > viewedCount

    @classmethod
    def _getDailyProgressResetTimeUTC(cls):
        regionalSettings = BigWorld.player().serverSettings['regional_settings']
        if 'starting_time_of_a_new_game_day' in regionalSettings:
            newDayUTC = regionalSettings['starting_time_of_a_new_game_day']
        elif 'starting_time_of_a_new_day' in regionalSettings:
            newDayUTC = regionalSettings['starting_time_of_a_new_day']
        else:
            newDayUTC = 0
        return newDayUTC

    def _getFirstActiveDailyQuest(self):
        return first(self._getActiveDailyQuests())

    def _getActiveDailyQuests(self):
        return sorted(self.eventsCache.getHiddenQuests(filterFunc=self.__dailyBonusFilterFunc).itervalues(), key=lambda q: q.getStartTime())

    def _onSyncCompleted(self):
        curCount = self.getCurrentCount()
        if self._currentCount != curCount:
            self._currentCount = curCount
            self.onItemsUpdated()

    def _getFrontCouponConfig(self):
        return self.gameEventController.frontCoupons.getFrontCouponConfig(self._frontCouponID)

    def __dailyBonusFilterFunc(self, quest):
        if quest.getGroupID() != FRONT_COUPON_RECHARGE_QUEST_GROUP_ID and not quest.bonusCond.isDaily:
            return False
        bonuses = quest.getBonuses('tokens')
        for bonus in bonuses:
            for tokenID in bonus.getTokens():
                if tokenID == self._frontCouponID:
                    return True

        return False


class GroupedFrontCouponsItem(BaseFrontCoupon):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, frontCoupons):
        self._em = EventManager()
        self.onItemsUpdated = Event(self._em)
        self._modifier = getFrontCouponModifier(first(frontCoupons).getFrontCouponID())
        self._frontCoupons = frontCoupons

    def getLabel(self):
        return 'x' + str(self._modifier)

    def getModifier(self):
        return self._modifier

    def init(self):
        for frontCoupon in self._frontCoupons:
            frontCoupon.onItemsUpdated += self.onItemsUpdated

    def fini(self):
        self._em.clear()

    def isDrawActive(self):
        return any((frontCoupon.isDrawActive() for frontCoupon in self._frontCoupons))

    def isActive(self):
        return any((frontCoupon.isActive() for frontCoupon in self._frontCoupons))

    def getMaxCount(self):
        return sum((frontCoupon.getMaxCount() for frontCoupon in self._frontCoupons))

    def getCurrentCount(self):
        return sum((frontCoupon.getCurrentCount() for frontCoupon in self._frontCoupons))

    def getNextRechargeTime(self):
        recharges = [ frontCoupon.getNextRechargeTime() for frontCoupon in self._frontCoupons if frontCoupon.getNextRechargeTime() > 0 ]
        return min(recharges) if recharges else 0

    def needToShowAnimation(self):
        viewedFrontCoupons = self.gameEventController.frontCoupons.getViewedFrontCoupons()
        viewedCount, currentCount = (0, 0)
        for frontCoupon in self._frontCoupons:
            viewedCount += viewedFrontCoupons.get(frontCoupon.getFrontCouponID(), 0)
            currentCount += frontCoupon.getCurrentCount()

        return currentCount > viewedCount


def getGroupedItem(items):
    return GroupedFrontCouponsItem(items) if items and len(items) > 1 else first(items)
