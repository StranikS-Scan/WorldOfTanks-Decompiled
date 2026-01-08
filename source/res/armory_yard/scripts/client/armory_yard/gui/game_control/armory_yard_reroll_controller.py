# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/game_control/armory_yard_reroll_controller.py
import itertools
import Event
from adisp import adisp_async, adisp_process
from armory_quests_common import armory_quests_cache
from armory_yard.gui.shared.armory_dynamic_quest import ArmoryDynamicQuest
from armory_yard_helpers import getNextFreeRerollUpdateTimestamp
from debug_utils import LOG_ERROR
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.gui_items.items_actions import factory
from gui.shared.money import Currency
from helpers import dependency, time_utils
from shared_utils import first
from skeletons.gui.game_control import IArmoryYardController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from armory_yard.gui.shared.gui_items.items_actions import REROLL_QUEST, ACCEPT_REROLL
from armory_yard.skeletons.armory_yard_reroll_controller import IArmoryYardRerollController
from armory_yard_constants import getFreeRerollToken, getDailyUserFreeRerolledToken, getConditionToken, getGroupName, getPostProgressionGroupName, PDATA_KEY_ARMORY_YARD, QUEST_CONDITION_OVERRIDE_PDATA_KEY, CONDITION_PREFIX, CURRENT_REROLL_PDATA_KEY, State

class ArmoryYardRerollController(IArmoryYardRerollController):
    __armoryYardController = dependency.descriptor(IArmoryYardController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        self.__eventManager = Event.EventManager()
        self.onQuestConditionUpdated = Event.Event(self.__eventManager)
        self.onPDataUpdated = Event.Event(self.__eventManager)
        self.onQuestConditionsReset = Event.Event(self.__eventManager)
        self.onFreeRerollTokensUpdated = Event.Event(self.__eventManager)
        self.onRerollQuest = Event.Event(self.__eventManager)
        self.onAcceptReroll = Event.Event(self.__eventManager)
        super(ArmoryYardRerollController, self).__init__()

    def onAccountBecomePlayer(self):
        g_clientUpdateManager.addCallbacks({PDATA_KEY_ARMORY_YARD: self.__onPdataUpdated,
         'tokens': self.__tokensUpdated})

    def onAccountBecomeNonPlayer(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def onLobbyInited(self, event):
        if self.__armoryYardController.isEnabled():
            armory_quests_cache.init(force=False)

    def fini(self):
        self.__eventManager.clear()

    def getConditionQuestsByTokenQuest(self, tokenQuest):
        conditionID = self.__itemsCache.items.armoryYard.overrideConditions.get(tokenQuest.getID(), None)
        if conditionID is None:
            conditionID = self.__armoryYardController.serverSettings.getDefaultConditionByQuestID(tokenQuest.getGroupID(), tokenQuest.getID())
        if conditionID is None:
            return []
        else:
            result = []
            reqToken = getConditionToken(conditionID)
            for quest in self.getConditionQuestsByID(reqToken):
                quest.setTokenQuestID(tokenQuest.getID())
                result.append(quest)

            return result

    def getArmoryTokenQuestByID(self, questID):
        return self.__eventsCache.getQuestByID(questID)

    def getConditionQuestsByID(self, reqToken):
        armory_quests_cache.init(force=False)
        questCache = armory_quests_cache.g_armory_quests_cache
        result = []
        if reqToken in questCache:
            for questID, questData in questCache[reqToken].iteritems():
                result.append(ArmoryDynamicQuest(questID, questData, self.__eventsCache.questsProgress.getQuestProgress(questID)))

        return result

    def getConditionQuestsByCondID(self, conditionId):
        armory_quests_cache.init(force=False)
        questCache = armory_quests_cache.g_armory_quests_cache
        _, condID, _ = conditionId.split(':')
        reqToken = getConditionToken(condID)
        return ArmoryDynamicQuest(conditionId, questCache[reqToken][conditionId], self.__eventsCache.questsProgress.getQuestProgress(conditionId)) if reqToken in questCache else None

    def getRerollCurrencies(self):
        currencies = self.__armoryYardController.serverSettings.getModeSettings().rerollPrices.keys()
        sortCurrencies = []
        for currency in Currency.BY_WEIGHT + (Currency.FREE_XP,):
            if currency in currencies:
                sortCurrencies.append(currency)

        return sortCurrencies

    def getRerollPrices(self):
        return self.__armoryYardController.serverSettings.getModeSettings().rerollPrices

    def getRerollCost(self, currency):
        rerollPrices = self.__armoryYardController.serverSettings.getModeSettings().rerollPrices
        return rerollPrices[currency] if currency is not None and currency in rerollPrices else 0

    def getFreeRerollsCount(self, groupName):
        freeRerollToken = self.__itemsCache.items.tokens.getTokenCount(getFreeRerollToken(groupName))
        if freeRerollToken > 0:
            return freeRerollToken
        dailyUserFreeRerolledToken = self.__itemsCache.items.tokens.getTokenCount(getDailyUserFreeRerolledToken(groupName))
        rerollSubsection = self.__armoryYardController.serverSettings.getModeSettings().rerollSubsection
        dailyFreeRerollsCount = rerollSubsection.get('dailyFreeRerollsCount', 0)
        return max(dailyFreeRerollsCount - dailyUserFreeRerolledToken, 0)

    def getFreeRerollsCountByCycleID(self, cycleID):
        currentSeason = self.__armoryYardController.serverSettings.getCurrentSeason()
        if currentSeason:
            if cycleID not in (cycle.ID for cycle in currentSeason.getAllCycles().values()):
                return self.getFreeRerollsCount(getPostProgressionGroupName(currentSeason.getSeasonID()))
        return self.getFreeRerollsCount(getGroupName(cycleID))

    def getNextFreeRerollTimestamp(self):
        if not self.isRerollEnabled():
            return 0
        rerollSubsection = self.__armoryYardController.serverSettings.getModeSettings().rerollSubsection
        dailyFreeRerollUpdate = rerollSubsection.get('dailyFreeRerollUpdate')
        if not dailyFreeRerollUpdate:
            return 0
        freeRerollDaysDelta = rerollSubsection.get('freeRerollDaysDelta')
        if not freeRerollDaysDelta:
            return 0
        currentDatetime = time_utils.getDateTimeInUTC(time_utils.getCurrentTimestamp())
        return getNextFreeRerollUpdateTimestamp(dailyFreeRerollUpdate, freeRerollDaysDelta, currentDatetime)

    def getFreeRerollCountdown(self):
        nextFreeRerollTimestamp = self.getNextFreeRerollTimestamp() or 0
        return int(max(nextFreeRerollTimestamp - time_utils.getCurrentLocalServerTimestamp(), 0))

    def isRerollEnabled(self):
        rerollSubsection = self.__armoryYardController.serverSettings.getModeSettings().rerollSubsection
        isArmoryYardPaused = self.__armoryYardController.isPaused
        isArmoryYardEnabled = self.__armoryYardController.isEnabled()
        return isArmoryYardEnabled and not isArmoryYardPaused and rerollSubsection.get('isEnabled', False)

    def getTokenQuestIDByConditionID(self, conditionID):
        for tokenQuestID, condID in itertools.chain(self.__itemsCache.items.armoryYard.overrideConditions.iteritems(), self.__armoryYardController.serverSettings.iterByDefaultRerollQuests()):
            if conditionID == condID:
                return tokenQuestID

        return None

    def validateRerollQuestID(self, questID):
        rerollSubsection = self.__armoryYardController.serverSettings.getModeSettings().rerollSubsection
        for questsData in rerollSubsection['defaultQuests'].itervalues():
            for tokenQuestID, _ in questsData:
                if tokenQuestID == questID:
                    return True

        return False

    def validateAcceptQuestID(self, questID):
        return questID in self.__itemsCache.items.armoryYard.currentReroll

    @adisp_async
    @adisp_process
    def rerollQuest(self, questID, rerollCurrency=None, callback=None):
        if not self.validateRerollQuestID(questID):
            LOG_ERROR('Not valid params for quest reroll, questID = %s' % questID)
            if callback:
                callback(None)
            return
        else:
            action = factory.getAction(REROLL_QUEST, questID, rerollCurrency)
            result = yield factory.asyncDoAction(action)
            if result.success:
                self.onRerollQuest(rerollCurrency)
            if callback:
                callback(result)
            return

    @adisp_async
    @adisp_process
    def acceptReroll(self, conditionID, questID, callback=None):
        if not self.validateAcceptQuestID(questID):
            LOG_ERROR('Not valid params to accept quest reroll, questID = %s' % questID)
            if callback:
                callback(None)
            return
        else:
            lastConditionID = self.__itemsCache.items.armoryYard.data.get(CURRENT_REROLL_PDATA_KEY, {}).get(questID, {}).get('currentCondition', None)
            action = factory.getAction(ACCEPT_REROLL, conditionID, questID)
            result = yield factory.asyncDoAction(action)
            if result:
                self.onAcceptReroll(lastConditionID, conditionID)
            if callback:
                callback(result)
            return

    def getReplacedTokenQuestID(self):
        questData = self.__itemsCache.items.armoryYard.data.get(CURRENT_REROLL_PDATA_KEY, None)
        return first(questData.keys()) if questData else None

    def getConditionIDsForReroll(self, replacedTokenQuestID):
        questData = self.__itemsCache.items.armoryYard.data.get(CURRENT_REROLL_PDATA_KEY, None)
        questID = self.getReplacedTokenQuestID()
        return questData.get(questID, {}).get('conditions') if questData and questID else []

    def __onPdataUpdated(self, diff):
        self.onPDataUpdated()
        if QUEST_CONDITION_OVERRIDE_PDATA_KEY in diff:
            condDiff = diff[QUEST_CONDITION_OVERRIDE_PDATA_KEY]
            for armoryCachedQuests in self.__eventsCache.getHiddenQuests(filterFunc=lambda q: q.getID().startswith(CONDITION_PREFIX)).values():
                armoryCachedQuests.resetConnection()

            for questID, conditionID in condDiff.iteritems():
                self.onQuestConditionUpdated(questID, conditionID)

            if not condDiff:
                self.onQuestConditionsReset()

    def __tokensUpdated(self, *args):
        self.onFreeRerollTokensUpdated()

    def getRerollContext(self):
        replacedQuestID = self.getReplacedTokenQuestID()
        questsToSelect = self.getConditionIDsForReroll(replacedQuestID)
        isPurchaseStage = self.__armoryYardController.getState() == State.PURCHASESTAGE
        context = None
        if replacedQuestID and questsToSelect and not isPurchaseStage:
            context = {'loadRerollView': {'questId': replacedQuestID,
                                'questsToSelect': questsToSelect}}
        return context
