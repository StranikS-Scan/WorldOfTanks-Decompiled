# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/EventsCache.py
import math
import sys
from collections import defaultdict, namedtuple
import typing
import BigWorld
import motivation_quests
import nations
from Event import Event, EventManager
from PlayerEvents import g_playerEvents
from adisp import async, process
from constants import EVENT_TYPE, EVENT_CLIENT_DATA, LOOTBOX_TOKEN_PREFIX, TWITCH_TOKEN_PREFIX, OFFER_TOKEN_PREFIX
from debug_utils import LOG_DEBUG
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK
from gui.server_events import caches as quests_caches
from gui.server_events.event_items import EventBattles, createQuest, createAction, MotiveQuest, ServerEventAbstract, Quest
from gui.server_events.events_helpers import isMarathon, isLinkedSet, isPremium, isRankedPlatform, isRankedDaily, isDailyEpic, isBattleRoyale, isMapsTraining
from gui.server_events.events_helpers import getRerollTimeout, getEventsData
from gui.server_events.formatters import getLinkedActionID
from gui.server_events.modifiers import ACTION_SECTION_TYPE, ACTION_MODIFIER_TYPE, clearModifiersCache
from gui.server_events.personal_missions_cache import PersonalMissionsCache
from gui.server_events.prefetcher import Prefetcher
from gui.shared.gui_items import GUI_ITEM_TYPE, ACTION_ENTITY_ITEM as aei
from gui.shared.utils.requesters.QuestsProgressRequester import QuestsProgressRequester
from helpers import dependency, time_utils
from items import getTypeOfCompactDescr
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from personal_missions import PERSONAL_MISSIONS_XML_PATH
from quest_cache_helpers import readQuestsFromFile
from shared_utils import first
from skeletons.gui.game_control import IRankedBattlesController, IEpicBattleMetaGameController, IBattleRoyaleController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IRaresCache
from skeletons.gui.linkedset import ILinkedSetController
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, Callable, Union
    from gui.server_events.event_items import DailyEpicTokenQuest, DailyQuest, PremiumQuest
NOT_FOR_PERSONAL_MISSIONS_TOKENS = (LOOTBOX_TOKEN_PREFIX,
 RECRUIT_TMAN_TOKEN_PREFIX,
 TWITCH_TOKEN_PREFIX,
 OFFER_TOKEN_PREFIX)
_ProgressiveReward = namedtuple('_ProgressiveReward', ('currentStep', 'probability', 'maxSteps'))

class _DailyQuestsData(object):
    __slots__ = ('_lastReroll',)

    def __init__(self, last_reroll=sys.maxint, **kwargs):
        self._lastReroll = last_reroll

    def getLastRerollTimestamp(self):
        return self._lastReroll

    def getNextAvailableRerollTimestamp(self):
        return self.getLastRerollTimestamp() + getRerollTimeout()

    def isRerollInCooldown(self):
        return self.getNextAvailableRerollTimestamp() > time_utils.getCurrentLocalServerTimestamp()


def _defaultQuestMaker(qID, qData, progressRequester):
    return createQuest(qData.get('type', 0), qID, qData, progressRequester.getQuestProgress(qID), progressRequester.getTokenExpiryTime(qData.get('requiredToken')))


def _motiveQuestMaker(qID, qData, progress):
    return MotiveQuest(qID, qData, progress.getQuestProgress(qID))


class EventsCache(IEventsCache):
    USER_QUESTS = (EVENT_TYPE.BATTLE_QUEST,
     EVENT_TYPE.TOKEN_QUEST,
     EVENT_TYPE.PERSONAL_QUEST,
     EVENT_TYPE.PERSONAL_MISSION)
    lobbyContext = dependency.descriptor(ILobbyContext)
    rareAchievesCache = dependency.descriptor(IRaresCache)
    linkedSet = dependency.descriptor(ILinkedSetController)
    rankedController = dependency.descriptor(IRankedBattlesController)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self):
        self.__waitForSync = False
        self.__invalidateCbID = None
        self.__cache = defaultdict(dict)
        self.__personalMissionsHidden = {}
        self.__actionsCache = defaultdict(lambda : defaultdict(dict))
        self.__actions2quests = {}
        self.__quests2actions = {}
        self.__questsDossierBonuses = defaultdict(set)
        self.__compensations = {}
        self.__personalMissions = PersonalMissionsCache()
        self.__questsProgressRequester = QuestsProgressRequester()
        self.__em = EventManager()
        self.__prefetcher = Prefetcher(self)
        self.onSyncStarted = Event(self.__em)
        self.onSyncCompleted = Event(self.__em)
        self.onProgressUpdated = Event(self.__em)
        self.onMissionVisited = Event(self.__em)
        self.onEventsVisited = Event(self.__em)
        self.onProfileVisited = Event(self.__em)
        self.onPersonalQuestsVisited = Event(self.__em)
        self.__lockedQuestIds = {}
        self.__dailyQuests = None
        return

    def init(self):
        self.__personalMissions.init()
        self.__prefetcher.init()

    def fini(self):
        self.__personalMissions.fini()
        self.__prefetcher.fini()
        self.__em.clear()
        self.__actions2quests.clear()
        self.__quests2actions.clear()
        self.__compensations.clear()
        self.__clearInvalidateCallback()

    def start(self):
        self.__onLockedQuestsChanged()
        self.__onDailyQuestsInfoChange()
        g_playerEvents.onPMLocksChanged += self.__onLockedQuestsChanged
        g_playerEvents.onDailyQuestsInfoChange += self.__onDailyQuestsInfoChange
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def stop(self, isDisconnected=False):
        if isDisconnected:
            self.__questsProgressRequester.clear()
        self.__dailyQuests = None
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        g_playerEvents.onDailyQuestsInfoChange -= self.__onDailyQuestsInfoChange
        g_playerEvents.onPMLocksChanged -= self.__onLockedQuestsChanged
        self.__clearQuestsItemsCache()
        self.__actions2quests.clear()
        self.__quests2actions.clear()
        self.__compensations.clear()
        self.__clearCache()
        self.__clearInvalidateCallback()
        return

    def clear(self):
        self.stop(isDisconnected=True)
        quests_caches.clearNavInfo()

    @property
    def waitForSync(self):
        return self.__waitForSync

    @property
    def questsProgress(self):
        return self.__questsProgressRequester

    def getPersonalMissions(self):
        return self.__personalMissions

    @property
    def prefetcher(self):
        return self.__prefetcher

    @property
    def dailyQuests(self):
        return self.__dailyQuests

    def getLockedQuestTypes(self, branch):
        questIDs = set()
        result = set()
        allQuests = self.getPersonalMissions().getQuestsForBranch(branch)
        for lockedList in self.__lockedQuestIds.values():
            if lockedList is not None:
                questIDs.update(lockedList)

        for questID in questIDs:
            if questID in allQuests:
                result.add(allQuests[questID].getMajorTag())

        return result

    @async
    @process
    def update(self, diff=None, callback=None):
        clearModifiersCache()
        yield self.getPersonalMissions().questsProgressRequest()
        if not self.getPersonalMissions().isQuestsProgressSynced():
            callback(False)
            return
        else:
            yield self.__questsProgressRequester.request()
            if not self.__questsProgressRequester.isSynced():
                callback(False)
                return
            isNeedToInvalidate = True
            isNeedToClearItemsCaches = False
            isQPUpdated = False

            def _cbWrapper(*args):
                callback(*args)
                self.__personalMissions.update(self, diff)

            if diff is not None:
                isQPUpdated = 'quests' in diff or 'potapovQuests' in diff or 'pm2_progress' in diff
                if not isQPUpdated and 'tokens' in diff:
                    for tokenID in diff['tokens'].iterkeys():
                        if all((not tokenID.startswith(t) for t in NOT_FOR_PERSONAL_MISSIONS_TOKENS)):
                            isQPUpdated = True
                            break

                isEventsDataUpdated = ('eventsData', '_r') in diff or diff.get('eventsData', {})
                isNeedToInvalidate = isQPUpdated or isEventsDataUpdated
                hasVehicleUnlocks = False
                for intCD in diff.get('stats', {}).get('unlocks', set()):
                    if getTypeOfCompactDescr(intCD) == GUI_ITEM_TYPE.VEHICLE:
                        hasVehicleUnlocks = True
                        break

                isNeedToClearItemsCaches = hasVehicleUnlocks or 'inventory' in diff and GUI_ITEM_TYPE.VEHICLE in diff['inventory']
            if isNeedToInvalidate:
                self.__invalidateData(_cbWrapper)
            else:
                if isNeedToClearItemsCaches:
                    self.__clearQuestsItemsCache()
                if isQPUpdated:
                    _cbWrapper(True)
                else:
                    callback(True)
            return

    def getQuests(self, filterFunc=None):
        filterFunc = filterFunc or (lambda a: True)

        def userFilterFunc(q):
            return not q.isHidden() and filterFunc(q)

        return self._getQuests(userFilterFunc)

    def getActiveQuests(self, filterFunc=None):
        filterFunc = filterFunc or (lambda a: True)
        isPremiumQuestsEnable = self.lobbyContext.getServerSettings().getPremQuestsConfig().get('enabled', False)

        def userFilterFunc(q):
            if isLinkedSet(q.getGroupID()) and not self.linkedSet.isLinkedSetEnabled():
                return False
            return False if not isPremiumQuestsEnable and isPremium(q.getGroupID()) else q.getFinishTimeLeft() and filterFunc(q)

        return self.getQuests(userFilterFunc)

    def getAdvisableQuests(self, filterFunc=None):
        filterFunc = filterFunc or (lambda a: True)
        isRankedSeasonOff = self.rankedController.getCurrentSeason() is None
        isEpicBattleEnabled = self.__epicController.isEnabled()

        def userFilterFunc(q):
            qGroup = q.getGroupID()
            qIsValid = q.isAvailable().isValid
            qID = q.getID()
            if q.getType() == EVENT_TYPE.MOTIVE_QUEST and not qIsValid:
                return False
            if q.getType() == EVENT_TYPE.TOKEN_QUEST and isMarathon(qID):
                return False
            if isLinkedSet(qGroup) or isPremium(qGroup) and not qIsValid:
                return False
            if not isEpicBattleEnabled and isDailyEpic(qGroup):
                return False
            if isBattleRoyale(qGroup):
                quests = self.__battleRoyaleController.getQuests()
                if qID not in quests:
                    return False
            if isMapsTraining(qGroup):
                return q.shouldBeShown()
            return False if isRankedSeasonOff and (isRankedDaily(qGroup) or isRankedPlatform(qGroup)) else filterFunc(q)

        return self.getActiveQuests(userFilterFunc)

    def getMotiveQuests(self, filterFunc=None):
        filterFunc = filterFunc or (lambda a: True)

        def userFilterFunc(q):
            return q.getType() == EVENT_TYPE.MOTIVE_QUEST and filterFunc(q)

        return self.getQuests(userFilterFunc)

    def getLinkedSetQuests(self, filterFunc=None):
        filterFunc = filterFunc or (lambda a: True)

        def userFilterFunc(q):
            return isLinkedSet(q.getGroupID()) and filterFunc(q)

        return self.getQuests(userFilterFunc)

    def getPremiumQuests(self, filterFunc=None):
        filterFunc = filterFunc or (lambda a: True)

        def userFilterFunc(q):
            return isPremium(q.getGroupID()) and filterFunc(q)

        return self.getQuests(userFilterFunc)

    def getDailyQuests(self, filterFunc=None, includeEpic=False):
        filterFunc = filterFunc or (lambda a: True)

        def userFilterFunc(q):
            return False if not includeEpic and q.getType() == EVENT_TYPE.TOKEN_QUEST else filterFunc(q)

        return self._getDailyQuests(userFilterFunc)

    def getDailyEpicQuest(self):
        dailyQuests = self._getDailyQuests()
        for q in dailyQuests.values():
            if q.getType() == EVENT_TYPE.TOKEN_QUEST and not q.isCompleted():
                return q

    def getBattleQuests(self, filterFunc=None):
        filterFunc = filterFunc or (lambda a: True)

        def userFilterFunc(q):
            return q.getType() == EVENT_TYPE.BATTLE_QUEST and filterFunc(q)

        return self.getQuests(userFilterFunc)

    def getGroups(self, filterFunc=None):
        svrGroups = self._getQuestsGroups(filterFunc)
        svrGroups.update(self._getActionsGroups(filterFunc))
        return svrGroups

    def getHiddenQuests(self, filterFunc=None):
        filterFunc = filterFunc or (lambda a: True)

        def hiddenFilterFunc(q):
            return q.isHidden() and filterFunc(q)

        return self._getQuests(hiddenFilterFunc)

    def getRankedQuests(self, filterFunc=None):
        filterFunc = filterFunc or (lambda a: True)

        def rankedFilterFunc(q):
            return q.getType() == EVENT_TYPE.RANKED_QUEST and filterFunc(q)

        return self._getQuests(rankedFilterFunc)

    def getAllQuests(self, filterFunc=None, includePersonalMissions=False):
        return self._getQuests(filterFunc, includePersonalMissions)

    def getActions(self, filterFunc=None):
        filterFunc = filterFunc or (lambda a: True)

        def userFilterFunc(q):
            return filterFunc(q) and q.getType() != EVENT_TYPE.GROUP

        return self._getActions(userFilterFunc)

    def getActionEntities(self):
        return self.__getActionsEntitiesData()

    def getAnnouncedActions(self):
        return self.__getAnnouncedActions()

    def getEventBattles(self):
        battles = self.__getEventBattles()
        return EventBattles(battles.get('vehicleTags', set()), battles.get('vehicles', []), bool(battles.get('enabled', 0)), battles.get('arenaTypeID')) if battles else EventBattles(set(), [], 0, None)

    def isEventEnabled(self):
        return self.getEventBattles().enabled

    @dependency.replace_none_kwargs(itemsCache=IItemsCache)
    def getEventVehicles(self, itemsCache=None):
        result = []
        if itemsCache is None:
            return result
        else:
            for v in self.getEventBattles().vehicles:
                item = itemsCache.items.getItemByCD(v)
                if item.isInInventory:
                    result.append(item)

            return sorted(result)

    def getEvents(self, filterFunc=None):
        svrEvents = self.getQuests(filterFunc)
        svrEvents.update(self.getActions(filterFunc))
        return svrEvents

    def getCurrentEvents(self):
        return self.getEvents(lambda q: q.getStartTimeLeft() <= 0 < q.getFinishTimeLeft())

    def getFutureEvents(self):
        return self.getEvents(lambda q: q.getStartTimeLeft() > 0)

    def getAffectedAction(self, item):
        actionEntities = self.getActionEntities()
        if actionEntities:
            entities = actionEntities[aei.ENTITIES_SECTION_NAME]
            actions = actionEntities[aei.ACTIONS_SECTION_NAME]
            steps = actionEntities[aei.STEPS_SECTION_NAME]
            if item in entities:
                entity = entities[item]
                actionNameIdx = entity[aei.ACTION_NAME_IDX]
                actionName = actions[actionNameIdx]
                stepNameIdx = entity[aei.ACTION_STEP_IDX]
                actionStep = steps[stepNameIdx]
                intersectedActions = entity[aei.AFFECTED_ACTIONS_IDX]
                return [actionName, actionStep, intersectedActions]
        return []

    def getItemAction(self, item, isBuying=True, forCredits=False):
        result = []
        actionType = ACTION_MODIFIER_TYPE.DISCOUNT if isBuying else ACTION_MODIFIER_TYPE.SELLING
        itemTypeID = item.itemTypeID
        nationID = item.nationID
        intCD = item.intCD
        values = self.__actionsCache[ACTION_SECTION_TYPE.ALL][actionType].get(itemTypeID, {}).get(nationID, [])
        values += self.__actionsCache[ACTION_SECTION_TYPE.ALL][actionType].get(itemTypeID, {}).get(15, [])
        for (_, value), actionID in values:
            if item.isPremium and value in ('creditsPrice', 'creditsPriceMultiplier') and not forCredits:
                continue
            result.append((value, actionID))

        result.extend(self.__actionsCache[ACTION_SECTION_TYPE.ITEM][actionType].get(itemTypeID, {}).get(intCD, tuple()))
        return result

    def getBoosterAction(self, booster, isBuying=True, forCredits=False):
        result = []
        actionType = ACTION_MODIFIER_TYPE.DISCOUNT if isBuying else ACTION_MODIFIER_TYPE.SELLING
        boosterID = booster.boosterID
        values = self.__actionsCache[ACTION_SECTION_TYPE.ALL_BOOSTERS][actionType].get(nations.NONE_INDEX, [])
        for (key, value), actionID in values:
            if forCredits and key == 'creditsPriceMultiplier':
                result.append((value, actionID))
            if not forCredits and key == 'goldPriceMultiplier':
                result.append((value, actionID))

        result.extend(self.__actionsCache[ACTION_SECTION_TYPE.BOOSTER][actionType].get(boosterID, tuple()))
        return result

    def getRentAction(self, item, rentPackage):
        result = []
        actionType = ACTION_MODIFIER_TYPE.RENT
        itemTypeID = item.itemTypeID
        nationID = item.nationID
        intCD = item.intCD
        values = self.__actionsCache[ACTION_SECTION_TYPE.ALL][actionType].get(itemTypeID, {}).get(nationID, [])
        values += self.__actionsCache[ACTION_SECTION_TYPE.ALL][actionType].get(itemTypeID, {}).get(15, [])
        for (_, value), actionID in values:
            result.append((value, actionID))

        result.extend(self.__actionsCache[ACTION_SECTION_TYPE.ITEM][actionType].get(itemTypeID, {}).get((intCD, rentPackage), tuple()))
        return result

    def getEconomicsAction(self, name):
        result = self.__actionsCache[ACTION_SECTION_TYPE.ECONOMICS][ACTION_MODIFIER_TYPE.DISCOUNT].get(name, [])
        resultMult = self.__actionsCache[ACTION_SECTION_TYPE.ECONOMICS][ACTION_MODIFIER_TYPE.DISCOUNT].get('%sMultiplier' % name, [])
        return tuple(result + resultMult)

    def getHeroTankAdventCalendarRedirectAction(self):
        isEnabled = False
        start, finish = (0, 0)

        def containsHeroToAdvent(a):
            return any((step.get('name') == 'HeroTankAdventCalendarRedirect' for step in a.getData().get('steps', [])))

        action = first(self.getActions(containsHeroToAdvent).values())
        if action is not None:
            start = action.getStartTimeRaw()
            finish = action.getFinishTimeRaw()
            isEnabled = any((m.getIsEnabled() for m in action.getModifiers()))
        return {'isEnabled': isEnabled,
         'start': start,
         'finish': finish}

    def getTradeInActions(self):

        def containsTradeIn(a):
            return any((step.get('name') == 'set_TradeInParams' for step in a.getData().get('steps', [])))

        return self.getActions(containsTradeIn).values()

    def getYearHareAffairAction(self):

        def containsYearHareAffair(a):
            return any((step.get('name') == 'set_YearHareAffair' for step in a.getData().get('steps', [])))

        return first(self.getActions(containsYearHareAffair).values())

    def isBalancedSquadEnabled(self):
        return bool(self.__getUnitRestrictions().get('enabled', False))

    def getBalancedSquadBounds(self):
        return (self.__getUnitRestrictions().get('lowerBound', 0), self.__getUnitRestrictions().get('upperBound', 0))

    def isSquadXpFactorsEnabled(self):
        return bool(self.__getUnitXpFactors().get('enabled', False))

    def getSquadBonusLevelDistance(self):
        return set(self.__getUnitXpFactors().get('levelDistanceWithBonuses', ()))

    def getSquadPenaltyLevelDistance(self):
        return set(self.__getUnitXpFactors().get('levelDistanceWithPenalties', ()))

    def getSquadZeroBonuses(self):
        return set(self.__getUnitXpFactors().get('zeroBonusesFor', ()))

    def getSquadXPFactor(self):
        return self.__getUnitXpFactors().get('factor', 0)

    def getQuestsDossierBonuses(self):
        return self.__questsDossierBonuses

    def getQuestsByTokenRequirement(self, token):
        result = []
        for q in self._getQuests(includePersonalMissions=False).itervalues():
            if token in [ t.getID() for t in q.accountReqs.getTokens() ]:
                result.append(q)

        return result

    def getQuestsByTokenBonus(self, token):
        result = []
        for q in self._getQuests(includePersonalMissions=True).itervalues():
            for t in q.getBonuses('tokens'):
                if token in t.getTokens().keys():
                    result.append(q)
                    break

        return result

    def getCompensation(self, tokenID):
        return self.__compensations.get(tokenID)

    def hasQuestDelayedRewards(self, questID):
        return self.__questsProgressRequester.hasQuestDelayedRewards(questID)

    def getProgressiveReward(self):
        progressiveConfig = self.lobbyContext.getServerSettings().getProgressiveRewardConfig()
        if not progressiveConfig.isEnabled:
            return None
        else:
            maxSteps = progressiveConfig.maxLevel
            currentStep = self.questsProgress.getTokenCount(progressiveConfig.levelTokenID)
            probability = self.questsProgress.getTokenCount(progressiveConfig.probabilityTokenID) / 100
            return _ProgressiveReward(currentStep, probability, maxSteps)

    def _getDailyQuests(self, filterFunc=None):
        result = {}
        filterFunc = filterFunc or (lambda a: True)
        for qID, q in self.__getDailyQuestsIterator():
            if filterFunc(q):
                result[qID] = q

        return result

    def getLobbyHeaderTabCounter(self):
        counterValue = None
        alias = None

        def containsLobbyHeaderTabCounter(a):
            return any((step.get('name') == 'LobbyHeaderTabCounterModification' for step in a.getData().get('steps', [])))

        action = first(self.getActions(containsLobbyHeaderTabCounter).values())
        if action is not None:
            counterValue = first((m.getCounterValue() for m in action.getModifiers()))
            alias = first((m.getAlias() for m in action.getModifiers()))
        return (alias, counterValue)

    def _getQuests(self, filterFunc=None, includePersonalMissions=False):
        result = {}
        groups = {}
        filterFunc = filterFunc or (lambda a: True)
        for qID, q in self.__getCommonQuestsIterator():
            if qID in self.__quests2actions:
                q.linkedActions = self.__quests2actions[qID]
            if q.getType() == EVENT_TYPE.GROUP:
                groups[qID] = q
                continue
            if q.getFinishTimeLeft() <= 0:
                continue
            if not filterFunc(q):
                continue
            result[qID] = q

        if includePersonalMissions:
            for qID, q in self.getPersonalMissions().getAllQuests().iteritems():
                if filterFunc(q):
                    result[qID] = q

        for gID, group in groups.iteritems():
            for qID in group.getGroupEvents():
                if qID in result:
                    result[qID].setGroupID(gID)

        children, parents, parentsName = self._makeQuestsRelations(result)
        for qID, q in result.iteritems():
            if qID in children:
                q.setChildren(children[qID])
            if qID in parents:
                q.setParents(parents[qID])
            if qID in parentsName:
                q.setParentsName(parentsName[qID])

        return result

    def _getQuestsGroups(self, filterFunc=None):
        filterFunc = filterFunc or (lambda a: True)
        result = {}
        for qID, q in self.__getCommonQuestsIterator():
            if q.getType() != EVENT_TYPE.GROUP:
                continue
            if not filterFunc(q):
                continue
            result[qID] = q

        return result

    def _getActions(self, filterFunc=None):
        filterFunc = filterFunc or (lambda a: True)
        actions = self.__getActionsData()
        result = {}
        groups = {}
        for aData in actions:
            if 'id' in aData:
                a = self._makeAction(aData['id'], aData)
                actionID = a.getID()
                if actionID in self.__actions2quests:
                    a.linkedQuests = self.__actions2quests[actionID]
                if a.getType() == EVENT_TYPE.GROUP:
                    groups[actionID] = a
                    continue
                if not filterFunc(a):
                    continue
                result[actionID] = a

        for gID, group in groups.iteritems():
            for aID in group.getGroupEvents():
                if aID in result:
                    result[aID].setGroupID(gID)

        return result

    def _getActionsGroups(self, filterFunc=None):
        actions = self.__getActionsData()
        filterFunc = filterFunc or (lambda a: True)
        result = {}
        for aData in actions:
            if 'id' in aData:
                a = self._makeAction(aData['id'], aData)
                if a.getType() != EVENT_TYPE.GROUP:
                    continue
                if not filterFunc(a):
                    continue
                result[a.getID()] = a

        return result

    def _makeQuest(self, qID, qData, maker=_defaultQuestMaker, **kwargs):
        storage = self.__cache['quests']
        if qID in storage:
            return storage[qID]
        q = storage[qID] = maker(qID, qData, self.__questsProgressRequester)
        return q

    def _makeAction(self, aID, aData):
        storage = self.__cache['actions']
        if aID in storage:
            return storage[aID]
        a = storage[aID] = createAction(aData.get('type', 0), aID, aData)
        return a

    @classmethod
    def _makeQuestsRelations(cls, quests):
        makeTokens = defaultdict(list)
        needTokens = defaultdict(list)
        for qID, q in quests.iteritems():
            if q.getType() not in (EVENT_TYPE.GROUP, EVENT_TYPE.PERSONAL_MISSION):
                for tokenBonus in q.getBonuses('tokens'):
                    for t in tokenBonus.getTokens():
                        makeTokens[t].append(qID)

                for t in q.accountReqs.getTokens():
                    needTokens[qID].append(t.getID())

        children = defaultdict(dict)
        for parentID, tokensIDs in needTokens.iteritems():
            for tokenID in tokensIDs:
                children[parentID][tokenID] = makeTokens.get(tokenID, [])

        parents = defaultdict(lambda : defaultdict(list))
        parentsName = defaultdict(lambda : defaultdict(list))
        for parentID, tokens in children.iteritems():
            for tokenID, chn in tokens.iteritems():
                for childID in chn:
                    parents[childID][tokenID].append(parentID)
                    parentsName[childID][tokenID].append(quests[parentID].getUserName())

        return (children, parents, parentsName)

    def __invalidateData(self, callback=lambda *args: None):
        self.__clearCache()
        self.__clearInvalidateCallback()
        self.__waitForSync = True
        self.onSyncStarted()
        for action in self.getActions().itervalues():
            for modifier in action.getModifiers():
                section = modifier.getSection()
                mType = modifier.getType()
                itemType = modifier.getItemType()
                values = modifier.getValues(action)
                currentSection = self.__actionsCache[section][mType]
                if itemType is not None:
                    currentSection = currentSection.setdefault(itemType, {})
                for k in values:
                    if k in currentSection:
                        currentSection[k] += values[k]
                    currentSection[k] = values[k]

        rareAchieves = set()
        invalidateTimeLeft = sys.maxint
        for q in self.getCurrentEvents().itervalues():
            dossierBonuses = q.getBonuses('dossier')
            if dossierBonuses:
                storage = self.__questsDossierBonuses[q.getID()]
                for bonus in dossierBonuses:
                    records = bonus.getRecords()
                    storage.update(set(bonus.getRecords().keys()))
                    rareAchieves |= set((rId for r, rId in records.iteritems() if r[0] == ACHIEVEMENT_BLOCK.RARE))

            timeLeftInfo = q.getNearestActivityTimeLeft()
            if timeLeftInfo is not None:
                isAvailable, errorMsg = q.isAvailable()
                if not isAvailable:
                    if errorMsg in ('invalid_weekday', 'invalid_time_interval'):
                        invalidateTimeLeft = min(invalidateTimeLeft, timeLeftInfo[0])
                else:
                    intervalBeginTimeLeft, (intervalStart, intervalEnd) = timeLeftInfo
                    invalidateTimeLeft = min(invalidateTimeLeft, intervalBeginTimeLeft + intervalEnd - intervalStart)
            invalidateTimeLeft = min(invalidateTimeLeft, q.getFinishTimeLeft())

        self.rareAchievesCache.request(rareAchieves)
        for q in self.getFutureEvents().itervalues():
            timeLeftInfo = q.getNearestActivityTimeLeft()
            if timeLeftInfo is None:
                startTime = q.getStartTimeLeft()
            else:
                startTime = timeLeftInfo[0]
            invalidateTimeLeft = min(invalidateTimeLeft, startTime)

        if invalidateTimeLeft != sys.maxint:
            self.__loadInvalidateCallback(invalidateTimeLeft)
        self.__waitForSync = False
        self.__prefetcher.ask()
        self.__syncActionsWithQuests()
        self.__invalidateCompensations()
        self.onSyncCompleted()
        callback(True)
        return

    def __invalidateCompensations(self):
        self.__compensations.clear()
        for q in self.getHiddenQuests(lambda q: isMarathon(q.getGroupID())).itervalues():
            self.__compensations.update(q.getCompensation())

    def __clearQuestsItemsCache(self):
        for _, q in self._getQuests().iteritems():
            q.accountReqs.clearItemsCache()
            q.vehicleReqs.clearItemsCache()

    def __syncActionsWithQuests(self):
        self.__actions2quests.clear()
        self.__quests2actions.clear()
        quests = self.__cache['quests']
        actions = [ item for item in self.__cache['actions'] ]
        self.__actions2quests = {k:[] for k in actions}
        for questID, questData in quests.iteritems():
            groupId = questData.getGroupID()
            linkedActionID = getLinkedActionID(groupId, actions)
            if linkedActionID is not None:
                self.__actions2quests[linkedActionID].append(questID)

        self.__convertQuests2actions()
        return

    def __convertQuests2actions(self):
        for action, quests in self.__actions2quests.iteritems():
            for quest in quests:
                if quest in self.__quests2actions:
                    self.__quests2actions[quest].append(action)
                self.__quests2actions[quest] = [action]

    @classmethod
    def __getEventsData(cls, eventsTypeName):
        return getEventsData(eventsTypeName)

    def __getQuestsData(self):
        return self.__getEventsData(EVENT_CLIENT_DATA.QUEST)

    def __getPersonalQuestsData(self):
        return self.__getEventsData(EVENT_CLIENT_DATA.PERSONAL_QUEST)

    def __getDailyQuestsData(self):
        return self.__getEventsData(EVENT_CLIENT_DATA.DAILY_QUESTS)

    def __getActionsData(self):
        return self.__getEventsData(EVENT_CLIENT_DATA.ACTION)

    def __getActionsEntitiesData(self):
        return self.__getEventsData(EVENT_CLIENT_DATA.ACTION_ENTITIES)

    def __getAnnouncedActions(self):
        return self.__getEventsData(EVENT_CLIENT_DATA.ANNOUNCED_ACTION_DATA)

    def __getIngameEventsData(self):
        return self.__getEventsData(EVENT_CLIENT_DATA.INGAME_EVENTS)

    def __getEventBattles(self):
        return self.__getIngameEventsData().get('eventBattles', {})

    def __getUnitRestrictions(self):
        return self.__getUnitData().get('restrictions', {})

    def __getUnitXpFactors(self):
        return self.__getUnitData().get('xpFactors', {})

    def __getUnitData(self):
        return self.__getEventsData(EVENT_CLIENT_DATA.SQUAD_BONUSES)

    def __getDailyQuestsIterator(self):
        for qID, qData in self.__getDailyQuestsData().iteritems():
            yield (qID, self._makeQuest(qID, qData))

    def __getCommonQuestsIterator(self):
        questsData = self.__getQuestsData()
        questsData.update(self.__getPersonalQuestsData())
        questsData.update(self.__getPersonalMissionsHiddenQuests())
        questsData.update(self.__getDailyQuestsData())
        for qID, qData in questsData.iteritems():
            yield (qID, self._makeQuest(qID, qData))

        motiveQuests = motivation_quests.g_cache.getAllQuests() or []
        for questDescr in motiveQuests:
            yield (questDescr.questID, self._makeQuest(questDescr.questID, questDescr.questData, maker=_motiveQuestMaker))

    def __loadInvalidateCallback(self, duration):
        LOG_DEBUG('load quest window invalidation callback (secs)', duration)
        self.__clearInvalidateCallback()
        self.__invalidateCbID = BigWorld.callback(math.ceil(duration), self.__onInvalidateNearestQuests)

    def __onInvalidateNearestQuests(self):
        if BigWorld.player() is not None:
            self.__invalidateData()
        return

    def __clearInvalidateCallback(self):
        if self.__invalidateCbID is not None:
            BigWorld.cancelCallback(self.__invalidateCbID)
            self.__invalidateCbID = None
        return

    def __clearCache(self):
        self.__questsDossierBonuses.clear()
        self.__actionsCache.clear()
        for storage in self.__cache.itervalues():
            storage.clear()

        clearModifiersCache()

    def __getPersonalMissionsHiddenQuests(self):
        if not self.__personalMissionsHidden:
            xmlPath = PERSONAL_MISSIONS_XML_PATH + '/tiles.xml'
            for quest in readQuestsFromFile(xmlPath, EVENT_TYPE.TOKEN_QUEST):
                self.__personalMissionsHidden[quest[0]] = quest[3]

        return self.__personalMissionsHidden.copy()

    def __onLockedQuestsChanged(self):
        self.__lockedQuestIds = BigWorld.player().personalMissionsLock

    def __onDailyQuestsInfoChange(self):
        self.__dailyQuests = _DailyQuestsData(**BigWorld.player().dailyQuests)

    def __onServerSettingsChange(self, *args, **kwargs):
        self.__personalMissions.updateDisabledStateForQuests()
