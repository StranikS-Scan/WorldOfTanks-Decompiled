# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/energy.py
import logging
import BigWorld
from Event import Event, EventManager
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from gui.SystemMessages import SM_TYPE
from gui import SystemMessages
from gui.shared.money import Money
from gui.shared.formatters import formatGoldPrice
from gui.shared.gui_items.processors import Processor, plugins, makeI18nError, makeI18nSuccess
from gui.shared.utils import decorators
_logger = logging.getLogger(__name__)

class GameEventEnergy(object):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, energyID, dailyQuestsGroupID=None):
        super(GameEventEnergy, self).__init__()
        self._em = EventManager()
        self.onEnergyChanged = Event(self._em)
        self._energyID = energyID
        self._currentCount = 0
        self._dailyQuestsGroupID = dailyQuestsGroupID

    def getID(self):
        return self._energyID

    def start(self):
        self.eventsCache.onSyncCompleted += self._onSyncCompleted
        self._currentCount = self.getCurrentCount()

    def stop(self):
        self.eventsCache.onSyncCompleted -= self._onSyncCompleted
        self._em.clear()

    def getMaxCount(self):
        return self._getEnergyData().get('maxCount', 0)

    def getCurrentCount(self):
        return min(self.eventsCache.questsProgress.getTokenCount(self._energyID), self.getMaxCount())

    def getPrice(self):
        return self._getEnergyData().get('price', 0)

    def isFull(self):
        return self.getCurrentCount() >= self.getMaxCount()

    def getExpectedEnergyOnNextDay(self):
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

    @decorators.process('buyEnergy')
    def buy(self):
        cost = self.getPrice()
        if cost is None:
            return
        else:
            result = yield EnergyBuyer(self.getID(), cost).request()
            if result.userMsg:
                SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
            self._onSyncCompleted()
            return

    def getTimeLeftToRecharge(self):
        quest = self._getFirstActiveDailyQuest()
        return 0 if quest is None else quest.getStartTimeLeft()

    def _getFirstActiveDailyQuest(self):
        quests = self._getActiveDailyQuests()
        return quests[0] if quests else None

    def _getActiveDailyQuests(self):
        return [] if self._dailyQuestsGroupID is None else sorted(self.eventsCache.getHiddenQuests(filterFunc=lambda q: q.getGroupID() == self._dailyQuestsGroupID and not q.isCompleted()).itervalues(), key=lambda q: q.getStartTime())

    def _onSyncCompleted(self):
        curCount = self.getCurrentCount()
        if self._currentCount != curCount:
            self._currentCount = curCount
            self.onEnergyChanged(curCount)

    def _getEnergyData(self):
        eventData = self.eventsCache.getGameEventData()
        return eventData.get('energies', {}).get(self._energyID, {})


class EnergyBuyer(Processor):

    def __init__(self, energyID, money):
        super(EnergyBuyer, self).__init__(plugins=(plugins.MessageConfirmator('seApril2019ShopBuyEnergy', isEnabled=True, ctx={'money': money}), plugins.MoneyValidator(Money(gold=money))))
        self._money = money
        self._energyID = energyID

    def _request(self, callback):
        _logger.debug('Make server request to buy energy %s for: %d', self._energyID, self._money)
        BigWorld.player().buyEnergy(self._energyID, lambda code, errorCode: self._response(code, callback, errorCode))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('se_april_2019/{}'.format(errStr), defaultSysMsgKey='se_april_2019/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('se_april_2019/buy_energy_success', gold=formatGoldPrice(self._money), type=SM_TYPE.PurchaseForGold)
