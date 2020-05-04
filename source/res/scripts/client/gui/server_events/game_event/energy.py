# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/energy.py
import logging
import time
import BigWorld
from Event import Event, EventManager
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency, time_utils
from helpers.i18n import makeString
from skeletons.gui.server_events import IEventsCache
from gui import SystemMessages
_logger = logging.getLogger(__name__)

class GameEventEnergy(object):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, dailyQuestsGroupID=None, energyID=None):
        super(GameEventEnergy, self).__init__()
        self._em = EventManager()
        self.onEnergyChanged = Event(self._em)
        self._energyID = energyID
        self._currentCount = 0
        self._dailyQuestsGroupID = dailyQuestsGroupID
        self.__storageName = 'energies'

    @property
    def energyID(self):
        if self._energyID is None:
            self._energyID = self._getEnergyData().get('id')
        return self._energyID

    def start(self):
        self.eventsCache.onSyncCompleted += self._onSyncCompleted
        self._currentCount = self.getCurrentCount()

    def stop(self):
        self.eventsCache.onSyncCompleted -= self._onSyncCompleted
        self._em.clear()

    def isDrawActive(self):
        data = self._getEnergyData()
        return data.get('drawActive', False)

    def isBuyAvailable(self):
        data = self._getEnergyData()
        return data.get('buyAvailable', False)

    def getMaxCount(self):
        return self._getEnergyData().get('maxCount', 0)

    def getCurrentCount(self):
        return 0 if not self.isDrawActive() else min(self.eventsCache.questsProgress.getTokenCount(self.energyID), self.getMaxCount())

    def getPrice(self):
        price = self._getEnergyData()['price']
        return (price.get('currency'), price.get('amount'))

    def getDefPrice(self):
        price = self._getEnergyData()['price']
        return (price.get('currency'), price.get('oldAmount'))

    def getDiscount(self):
        _, amount = self.getPrice()
        oldAmount = self._getEnergyData()['price'].get('oldAmount')
        return int((1 - float(amount) / oldAmount) * 100) if amount and oldAmount and amount < oldAmount else 0

    def isFull(self):
        return self.getCurrentCount() >= self.getMaxCount()

    def getTimeLeftToRecharge(self):
        quest = self._getFirstActiveDailyQuest()
        return 0 if quest is None else quest.getStartTimeLeft()

    def getNextRechargeCount(self):
        quest = self._getFirstActiveDailyQuest()
        if quest is None:
            return 0
        else:
            bonuses = quest.getBonuses('tokens')
            for bonus in bonuses:
                for tokenID, token in bonus.getTokens().iteritems():
                    if tokenID == self._energyID:
                        return token.count

            return 0

    def getNextRechargeTime(self):
        quest = self._getFirstActiveDailyQuest()
        if quest is None:
            return 0
        else:
            currentDayUTC = time_utils.getServerTimeCurrentDay()
            dailyProgressResetTimeUTC = self._getDailyProgressResetTimeUTC()
            untilRest = dailyProgressResetTimeUTC - currentDayUTC
            if untilRest < 0:
                untilRest += time_utils.ONE_DAY
            return untilRest + time.time()

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
        quests = self._getActiveDailyQuests()
        return quests[0] if quests else None

    def _getActiveDailyQuests(self):
        return [] if self._dailyQuestsGroupID is None else sorted(self.eventsCache.getHiddenQuests(filterFunc=self.__dailyBonusFilterFunc).itervalues(), key=lambda q: q.getStartTime())

    def __dailyBonusFilterFunc(self, quest):
        if quest.getGroupID() != self._dailyQuestsGroupID or quest.isCompleted() and not quest.bonusCond.isDaily:
            return False
        bonuses = quest.getBonuses('tokens')
        for bonus in bonuses:
            for tokenID in bonus.getTokens():
                if tokenID == self._energyID:
                    return True

        return False

    def _onSyncCompleted(self):
        curCount = self.getCurrentCount()
        if self._currentCount != curCount:
            self._currentCount = curCount
            self.onEnergyChanged(curCount)

    def _getEnergyData(self):
        eventData = self.eventsCache.getGameEventData()
        data = eventData.get(self.__storageName, {})
        return data.get(self._energyID)


class GameEventPremiumEnergy(GameEventEnergy):
    PREMIUM = 'premium'
    _EXCLUDED_ORDERS = ['x10_premium', 'x10']

    def __init__(self, generalID, dailyQuestsGroupID=None, energyID=None, order=None, modifier=1):
        super(GameEventPremiumEnergy, self).__init__(dailyQuestsGroupID, energyID)
        self.order = order
        self.modifier = modifier
        self._premiumID = None
        self._generalID = generalID
        return

    def addID(self, energyID):
        currentID = self._energyID
        if self.PREMIUM in energyID:
            self._premiumID = energyID
        else:
            self._energyID = energyID
            self._premiumID = currentID
        logging.debug('Energy with 2 ids: premium %s, usual %s', self._premiumID, self._energyID)

    def getCurrentCount(self):
        count = super(GameEventPremiumEnergy, self).getCurrentCount()
        count += self.eventsCache.questsProgress.getTokenCount(self._premiumID)
        return min(count, self.getMaxCount())

    def getLabel(self):
        return 'x' + str(self.modifier)

    def _onSyncCompleted(self):
        curCount = self.getCurrentCount()
        if self._currentCount != curCount:
            delta = curCount - self._currentCount
            self._currentCount = curCount
            self.onEnergyChanged(curCount)
            if not self.eventsCache.isEventEnabled() or any((excluded in self._energyID for excluded in self._EXCLUDED_ORDERS)):
                return
            division = backport.text(R.strings.event.unit.name.num(self._generalID)())
            if delta > 0:
                msg = makeString(backport.text(R.strings.system_messages.se20.dyn('general_orders_receive')()), order=self.getLabel(), division=division, count=delta)
                SystemMessages.pushMessage(msg, type=SystemMessages.SM_TYPE.Information)
