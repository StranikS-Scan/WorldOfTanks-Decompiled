# Embedded file name: scripts/client/gui/shared/server_events/EventsCache.py
import math
import sys
import zlib
import cPickle as pickle
from collections import defaultdict
import BigWorld
from Event import Event
from adisp import async
from constants import EVENT_TYPE
from gui.shared.utils import prettyPrint
from helpers import isPlayerAccount
from items import getTypeOfCompactDescr
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_DEBUG
from gui.shared import events
from gui.shared.server_events.modifiers import ACTION_SECTION_TYPE, ACTION_MODIFIER_TYPE
from gui.shared.utils.RareAchievementsCache import g_rareAchievesCache
from gui.shared.utils.requesters.QuestsProgressRequester import QuestsProgressRequester
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.server_events.event_items import Quest, Action, EventBattles, HistoricalBattle

class _EventsCache(object):
    USER_QUESTS = (EVENT_TYPE.BATTLE_QUEST,
     EVENT_TYPE.TOKEN_QUEST,
     EVENT_TYPE.FORT_QUEST,
     EVENT_TYPE.PERSONAL_QUEST,
     EVENT_TYPE.POTAPOV_QUEST)
    SYSTEM_QUESTS = (EVENT_TYPE.REF_SYSTEM_QUEST,)

    def __init__(self):
        self.__progress = QuestsProgressRequester()
        self.__waitForSync = False
        self.__invalidateCbID = None
        self.__cache = defaultdict(dict)
        self.__actionsCache = defaultdict(lambda : defaultdict(dict))
        self.__questsDossierBonuses = defaultdict(set)
        self.onSyncStarted = Event()
        self.onSyncCompleted = Event()
        return

    def init(self):
        pass

    def fini(self):
        self.onSyncStarted.clear()
        self.onSyncCompleted.clear()
        self.__clearInvalidateCallback()

    @property
    def waitForSync(self):
        return self.__waitForSync

    @property
    def questsProgress(self):
        return self.__progress

    @async
    def update(self, diff = None, callback = None):
        isNeedToInvalidate = True
        isQPUpdated = False
        isNeedToClearItemsCaches = False
        if diff is not None:
            isNeedToInvalidate = 'cache' in diff and (('eventsData', '_r') in diff['cache'] or 'eventsData' in diff['cache'])
            isQPUpdated = 'quests' in diff
            hasVehicleUnlocks = False
            for intCD in diff.get('stats', {}).get('unlocks', set()):
                if getTypeOfCompactDescr(intCD) == GUI_ITEM_TYPE.VEHICLE:
                    hasVehicleUnlocks = True
                    break

            isNeedToClearItemsCaches = 'inventory' in diff and GUI_ITEM_TYPE.VEHICLE in diff['inventory'] or hasVehicleUnlocks
        if isNeedToInvalidate:
            self.__invalidateData(callback)
            return
        else:
            if isNeedToClearItemsCaches:
                self.__clearQuestsItemsCache()
            if isQPUpdated:
                self.__updateQuestProgress(diff, callback)
            else:
                callback(True)
            return

    def getQuests(self, filterFunc = None):
        filterFunc = filterFunc or (lambda a: True)

        def userFilterFunc(q):
            return q.getType() in self.USER_QUESTS and filterFunc(q)

        return self._getQuests(userFilterFunc)

    def getSystemQuests(self, filterFunc = None):
        filterFunc = filterFunc or (lambda a: True)

        def systemFilterFunc(q):
            return q.getType() in self.SYSTEM_QUESTS and filterFunc(q)

        return self._getQuests(systemFilterFunc)

    def getActions(self, filterFunc = None):
        actions = self.__getActionsData()
        filterFunc = filterFunc or (lambda a: True)
        result = {}
        for aData in actions:
            if 'id' in aData:
                a = self._makeAction(aData['id'], aData)
                if not filterFunc(a):
                    continue
                result[a.getID()] = a

        return result

    def getEventBattles(self):
        battles = self.__getEventBattles()
        if len(battles):
            return EventBattles(battles.get('vehicleTags', set()), battles.get('vehicles', []), bool(battles.get('enabled', 0)), battles.get('arenaTypeID'))
        else:
            return None

    def getEvents(self, filterFunc = None):
        svrEvents = self.getQuests(filterFunc)
        svrEvents.update(self.getActions(filterFunc))
        return svrEvents

    def getCurrentEvents(self):
        return self.getEvents(lambda q: q.getStartTimeLeft() <= 0 < q.getFinishTimeLeft())

    def getFutureEvents(self):
        return self.getEvents(lambda q: q.getStartTimeLeft() > 0)

    def getHistoricalBattles(self, hideExpired = True, filterFunc = None):
        battles = self.__getHistoricalBattlesData()
        filterFunc = filterFunc or (lambda a: True)
        result = {}
        for bID, bData in battles.iteritems():
            b = self._makeHistoricalBattle(bID, bData)
            if hideExpired and b.isOutOfDate():
                continue
            if not filterFunc(b):
                continue
            result[bID] = b

        return result

    def getItemAction(self, item, isBuying = True, forCredits = False):
        result = []
        type = ACTION_MODIFIER_TYPE.DISCOUNT if isBuying else ACTION_MODIFIER_TYPE.SELLING
        itemTypeID = item.itemTypeID
        nationID = item.nationID
        intCD = item.intCD
        values = self.__actionsCache[ACTION_SECTION_TYPE.ALL][type].get(itemTypeID, {}).get(nationID, [])
        values += self.__actionsCache[ACTION_SECTION_TYPE.ALL][type].get(itemTypeID, {}).get(15, [])
        for (key, value), actionID in values:
            if item.isPremium and key in ('creditsPrice', 'creditsPriceMultiplier') and not forCredits:
                continue
            result.append((value, actionID))

        result.extend(self.__actionsCache[ACTION_SECTION_TYPE.ITEM][type].get(itemTypeID, {}).get(intCD, tuple()))
        return result

    def getEconomicsAction(self, name):
        result = self.__actionsCache[ACTION_SECTION_TYPE.ECONOMICS][ACTION_MODIFIER_TYPE.DISCOUNT].get(name, [])
        resultMult = self.__actionsCache[ACTION_SECTION_TYPE.ECONOMICS][ACTION_MODIFIER_TYPE.DISCOUNT].get('%sMultiplier' % name, [])
        return tuple(result + resultMult)

    def getCamouflageAction(self, vehicleIntCD):
        return self.__actionsCache[ACTION_SECTION_TYPE.CUSTOMIZATION][ACTION_MODIFIER_TYPE.DISCOUNT].get(vehicleIntCD, tuple())

    def getEmblemsAction(self, group):
        return self.__actionsCache[ACTION_SECTION_TYPE.CUSTOMIZATION][ACTION_MODIFIER_TYPE.DISCOUNT].get(group, tuple())

    def getQuestsDossierBonuses(self):
        return self.__questsDossierBonuses

    def _getQuests(self, filterFunc = None):
        quests = self.__getQuestsData()
        quests.update(self.__getFortQuestsData())
        quests.update(self.__getPersonalQuestsData())
        filterFunc = filterFunc or (lambda a: True)
        result = {}
        for qID, qData in quests.iteritems():
            q = self._makeQuest(qID, qData)
            if q.getDestroyingTimeLeft() <= 0:
                continue
            if not filterFunc(q):
                continue
            result[qID] = q

        children, parents = self._makeQuestsRelations(result)
        for qID, q in result.iteritems():
            if qID in children:
                q.setChildren(children[qID])
            if qID in parents:
                q.setParents(parents[qID])

        return result

    def _onResync(self, *args):
        self.__invalidateData()

    def _makeQuest(self, qID, qData):
        storage = self.__cache['quests']
        if qID in storage:
            return storage[qID]
        q = storage[qID] = Quest(qID, qData, self.__progress.getQuestProgress(qID))
        return q

    def _makeAction(self, aID, aData):
        storage = self.__cache['actions']
        if aID in storage:
            return storage[aID]
        a = storage[aID] = Action(aID, aData)
        return a

    def _makeHistoricalBattle(self, bID, bData):
        storage = self.__cache['historicalBattles']
        if bID in storage:
            return storage[bID]
        b = storage[bID] = HistoricalBattle(bID, bData)
        return b

    @classmethod
    def _makeQuestsRelations(cls, quests):
        makeTokens = defaultdict(list)
        needTokens = defaultdict(list)
        for qID, q in quests.iteritems():
            tokens = q.getBonuses('tokens')
            if len(tokens):
                for t in tokens[0].getTokens():
                    makeTokens[t].append(qID)

            for t in q.accountReqs.getTokens():
                needTokens[qID].append(t.getID())

        children = defaultdict(dict)
        for parentID, tokensIDs in needTokens.iteritems():
            for tokenID in tokensIDs:
                children[parentID][tokenID] = makeTokens.get(tokenID, [])

        parents = defaultdict(dict)
        for parentID, tokens in children.iteritems():
            for tokenID, chn in tokens.iteritems():
                for childID in chn:
                    parents[childID][tokenID] = [parentID]

        return (children, parents)

    def __invalidateData(self, callback = lambda *args: None):

        def cbWrapper(*args):
            self.__waitForSync = False
            self.onSyncCompleted()
            callback(*args)

        self.__clearCache()
        self.__clearInvalidateCallback()
        self.__waitForSync = True
        self.onSyncStarted()

        def mergeValues(a, b):
            result = list(a)
            result.extend(b)
            return result

        for action in self.getActions().itervalues():
            for modifier in action.getModifiers():
                section = modifier.getSection()
                type = modifier.getType()
                itemType = modifier.getItemType()
                values = modifier.getValues(action)
                currentSection = self.__actionsCache[section][type]
                if itemType is not None:
                    currentSection = currentSection.setdefault(itemType, {})
                for k in values:
                    if k in currentSection:
                        currentSection[k] = mergeValues(currentSection[k], values[k])
                    else:
                        currentSection[k] = values[k]

        self.__progress.request()(cbWrapper)
        rareAchieves = set()
        invalidateTimeLeft = sys.maxint
        for q in self.getCurrentEvents().itervalues():
            dossierBonuses = q.getBonuses('dossier')
            if len(dossierBonuses):
                storage = self.__questsDossierBonuses[q.getID()]
                for bonus in dossierBonuses:
                    records = bonus.getRecords()
                    storage.update(records)
                    rareAchieves |= set((r for r in records if r[0] == ACHIEVEMENT_BLOCK.RARE))

            timeLeftInfo = q.getNearestActivityTimeLeft()
            if timeLeftInfo is not None:
                isAvailable, errorMsg = q.isAvailable()
                if not isAvailable:
                    if errorMsg in ('invalid_weekday', 'invalid_time_interval'):
                        invalidateTimeLeft = min(invalidateTimeLeft, timeLeftInfo[0])
                else:
                    intervalBeginTimeLeft, (intervalStart, intervalEnd) = timeLeftInfo
                    invalidateTimeLeft = min(invalidateTimeLeft, intervalBeginTimeLeft + intervalEnd - intervalStart)
            else:
                invalidateTimeLeft = min(invalidateTimeLeft, q.getFinishTimeLeft())

        g_rareAchievesCache.request(rareAchieves)
        for q in self.getFutureEvents().itervalues():
            timeLeftInfo = q.getNearestActivityTimeLeft()
            if timeLeftInfo is None:
                startTime = q.getStartTimeLeft()
            else:
                startTime = timeLeftInfo[0]
            invalidateTimeLeft = min(invalidateTimeLeft, startTime)

        for hb in self.getHistoricalBattles().itervalues():
            timeLeftInfo = hb.getNearestActivityTimeLeft()
            if timeLeftInfo is None:
                startTime = hb.getFinishTimeLeft()
            else:
                startTime = timeLeftInfo[0]
            invalidateTimeLeft = min(invalidateTimeLeft, startTime)

        if invalidateTimeLeft != sys.maxint:
            self.__loadInvalidateCallback(invalidateTimeLeft)
        from gui.shared import g_eventBus
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.EVENTS_UPDATED))
        return

    def __updateQuestProgress(self, diff, callback = lambda *args: None):
        if 'quests' not in diff:
            return
        else:
            self.__waitForSync = True
            self.onSyncStarted()
            quests = self.__cache['quests']
            qDiff = diff['quests']
            for qID in qDiff.iterkeys():
                quests.pop(qID, None)

            def cbWrapper(*args):
                self.__waitForSync = False
                self.onSyncCompleted()
                callback(*args)

            self.__progress.request()(cbWrapper)
            return

    def __clearQuestsItemsCache(self):
        for qID, q in self.getQuests().iteritems():
            q.accountReqs.clearItemsCache()
            q.vehicleReqs.clearItemsCache()

    @classmethod
    def __getEventsData(cls, eventsTypeName):
        try:
            if isPlayerAccount():
                if eventsTypeName in BigWorld.player().eventsData:
                    return pickle.loads(zlib.decompress(BigWorld.player().eventsData[eventsTypeName]))
                return {}
            LOG_ERROR('Trying to get quests data from not account player', eventsTypeName, BigWorld.player())
        except Exception:
            LOG_CURRENT_EXCEPTION()

        return {}

    def __getQuestsData(self):
        return self.__getEventsData('questsClientData')

    def __getFortQuestsData(self):
        return self.__getEventsData('fortQuestsClientData')

    def __getPersonalQuestsData(self):
        return self.__getEventsData('personalQuestsClientData')

    def __getActionsData(self):
        return self.__getEventsData('actionsClientData')

    def __getEventBattles(self):
        return self.__getEventsData('eventBattlesClientData')

    def __getHistoricalBattlesData(self):
        return self.__getEventsData('historicalBattlesClientData')

    def __loadInvalidateCallback(self, duration):
        LOG_DEBUG('load quest window invalidation callback (secs)', duration)
        self.__clearInvalidateCallback()
        self.__invalidateCbID = BigWorld.callback(math.ceil(duration), self.__invalidateData)

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


g_eventsCache = _EventsCache()
