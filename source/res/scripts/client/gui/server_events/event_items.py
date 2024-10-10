# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/event_items.py
import operator
import time
from abc import ABCMeta
from collections import namedtuple
import typing
import constants
import nations
from debug_utils import LOG_ERROR
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.ranked_helpers import getQualificationBattlesCountFromID, isQualificationQuestID
from gui.server_events import events_helpers, finders
from gui.server_events.events_constants import BATTLE_MATTERS_QUEST_ID, BATTLE_MATTERS_INTERMEDIATE_QUEST_ID, BATTLE_MATTERS_COMPENSATION_QUEST_ID
from gui.server_events.bonuses import compareBonuses, getBonuses
from gui.server_events.events_constants import WT_BOSS_GROUP_ID, WT_QUEST_UNAVAILABLE_NOT_ENOUGH_TICKETS_REASON
from gui.server_events.events_helpers import isDailyQuest, isPremium, getIdxFromQuestID, isWtQuest
from gui.server_events.formatters import getLinkedActionID
from gui.server_events.modifiers import compareModifiers, getModifierObj
from gui.server_events.parsers import AccountRequirements, BonusConditions, PostBattleConditions, PreBattleConditions, TokenQuestAccountRequirements, VehicleRequirements
from gui.shared.gui_items import Vehicle
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
from gui.shared.system_factory import registerQuestBuilders
from gui.shared.utils import ValidationResult
from gui.shared.utils.requesters.QuestsProgressRequester import PersonalMissionsProgressRequester
from helpers import dependency, getLocalizedData, i18n, time_utils
from personal_missions import PM_BRANCH, PM_BRANCH_TO_FINAL_PAWN_COST, PM_FLAG, PM_STATE as _PMS
from personal_missions_config import getQuestConfig
from personal_missions_constants import DISPLAY_TYPE
from shared_utils import findFirst, first
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IWhiteTigerController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.server_events.bonuses import SimpleBonus
if typing.TYPE_CHECKING:
    from typing import Dict, Callable, List, Optional, Tuple, Union
    from gui.Scaleform.daapi.view.lobby.server_events.events_helpers import EventPostBattleInfo
    import potapov_quests

class DEFAULTS_GROUPS(object):
    FOR_CURRENT_VEHICLE = 'currentlyAvailable'
    UNGROUPED_ACTIONS = 'ungroupedActions'
    UNGROUPED_QUESTS = 'ungroupedQuests'
    REGULAR_GROUPED_QUESTS = 'regularGroupedQuests'
    MOTIVE_QUESTS = 'motiveQuests'
    MARATHON_QUESTS = 'marathonQuests'
    PREMIUM_QUESTS = 'premiumQuests'


def getGroupTypeByID(groupID):
    if groupID in (DEFAULTS_GROUPS.UNGROUPED_QUESTS, DEFAULTS_GROUPS.MOTIVE_QUESTS):
        return groupID
    if events_helpers.isMarathon(groupID):
        return DEFAULTS_GROUPS.MARATHON_QUESTS
    return DEFAULTS_GROUPS.PREMIUM_QUESTS if events_helpers.isPremium(groupID) else DEFAULTS_GROUPS.REGULAR_GROUPED_QUESTS


class CONTITIONS_SCOPE(object):
    MAIN = 'main'
    FULL = 'full'
    DIFF = 'add'


class TOKEN_SHOP(object):
    SHOW = 'show'
    HIDE = 'hide'
    WEB = 'web'


class ServerEventAbstract(object):
    __metaclass__ = ABCMeta
    __slots__ = ('_id', '_data', '_groupID')
    _connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, eID, data):
        self._id = eID
        self._data = dict(data)
        self._groupID = None
        return

    def isGuiDisabled(self):
        return self._data.get('disableGui', False)

    def isHidden(self):
        return self._data.get('hidden', False) or not self.__isForCurrentPeriphery()

    def isShowedPostBattle(self):
        return self._data.get('showPostBattleStat', False)

    def getWeekDays(self):
        return self._data.get('weekDays', set())

    def getActiveTimeIntervals(self):
        if 'activeTimeIntervals' in self._data:
            return [ (l[0] * 3600 + l[1] * 60, h[0] * 3600 + h[1] * 60) for l, h in self._data['activeTimeIntervals'] ]
        return []

    def getID(self):
        return self._id

    def getIconID(self):
        return self._data.get('uiDecoration', None)

    def setGroupID(self, groupID):
        self._groupID = groupID

    def getGroupID(self):
        return self._groupID

    def getPriority(self):
        return self._data.get('priority', 0)

    def getData(self):
        return self._data

    def getType(self):
        return self._data.get('type', 0)

    def getStartTimeRaw(self):
        return self._data['startTime'] if 'startTime' in self._data else time.time()

    def getFinishTimeRaw(self):
        return self._data['finishTime'] if 'finishTime' in self._data else time.time()

    def getStartTime(self):
        return time_utils.makeLocalServerTime(self._data['startTime']) if 'startTime' in self._data else time.time()

    def getFinishTime(self):
        return time_utils.makeLocalServerTime(self._data['finishTime']) if 'finishTime' in self._data else time.time()

    def getUserName(self):
        return getLocalizedData(self._data, 'name')

    def getDescription(self):
        return getLocalizedData(self._data, 'description')

    def getNotificationText(self):
        return getLocalizedData(self._data, 'notificationText')

    def getTimeFromStartTillNow(self):
        return time_utils.getTimeDeltaTillNow(self.getStartTime())

    def getStartTimeLeft(self):
        return time_utils.getTimeDeltaFromNowInLocal(self.getStartTime())

    def getFinishTimeLeft(self):
        return time_utils.getTimeDeltaFromNowInLocal(self.getFinishTime())

    def isOutOfDate(self):
        return self.getFinishTimeLeft() <= 0

    def isStarted(self):
        return self.getStartTimeLeft() <= 0

    def getUserType(self):
        pass

    def isIGR(self):
        return self._data.get('isIGR', False)

    def isCompleted(self, progress=None):
        return False

    def isTokensOnSale(self):
        state = self._getTokenSaleState()
        return state == TOKEN_SHOP.SHOW

    def isTokensOnSaleDynamic(self):
        return self._getTokenSaleState() == TOKEN_SHOP.WEB

    def getNearestActivityTimeLeft(self):
        timeLeft = None
        if self.getStartTimeLeft() > 0:
            timeLeft = (self.getStartTimeLeft(), (0, time_utils.ONE_DAY))
        else:
            weekDays, timeIntervals = self.getWeekDays(), self.getActiveTimeIntervals()
            if weekDays or timeIntervals:
                timeLeft = next(time_utils.ActivityIntervalsIterator(time_utils.getServerTimeCurrentDay(), time_utils.getServerRegionalWeekDay(), weekDays, timeIntervals))
        return timeLeft

    def hasPremIGRVehBonus(self):
        return False

    def isAvailable(self):
        if self.getStartTimeLeft() > 0:
            return ValidationResult(False, 'in_future')
        if self.isOutOfDate():
            return ValidationResult(False, 'out_of_date')
        weekDays = self.getWeekDays()
        if weekDays and time_utils.getServerRegionalWeekDay() not in weekDays:
            return ValidationResult(False, 'invalid_weekday')
        intervals = self.getActiveTimeIntervals()
        serverTime = time_utils.getServerTimeCurrentDay()
        if intervals:
            for low, high in intervals:
                if low <= serverTime <= high:
                    break
            else:
                return ValidationResult(False, 'invalid_time_interval')

        return ValidationResult(False, 'requirements') if not self._checkConditions() else ValidationResult(True, '')

    def isRawAvailable(self, now=None):
        now = now or time.time()
        return self.getStartTimeRaw() <= now < self.getFinishTimeRaw()

    def isValidVehicleCondition(self, vehicle):
        return self._checkVehicleConditions(vehicle)

    def getBonuses(self, bonusName=None, isCompensation=False):
        return []

    def getLevel(self):
        pass

    def getParents(self):
        return []

    def getParentsName(self):
        return []

    def _checkConditions(self):
        return True

    def _checkVehicleConditions(self, vehicle):
        return True

    def _getTokenSaleState(self):
        return self._data.get('shopButton', TOKEN_SHOP.HIDE)

    def __isForCurrentPeriphery(self):
        peripheryIDs = self._data.get('peripheryIDs')
        return True if not peripheryIDs else self._connectionMgr.peripheryID in peripheryIDs

    def __repr__(self):
        return '%s(qID = %s, groupID = %s)' % (self.__class__.__name__, self._id, self._groupID)


class Group(ServerEventAbstract):

    def getGroupEvents(self):
        return self._data.get('groupContent', [])

    def getGroupContent(self, srvEvents):
        groupQuests = []
        for questID in self.getGroupEvents():
            quest = srvEvents.get(questID)
            if quest is not None:
                groupQuests.append(quest)

        return groupQuests

    def isMarathon(self):
        return events_helpers.isMarathon(self.getID())

    def isPremium(self):
        return events_helpers.isPremium(self.getID())

    def isRegularQuest(self):
        return events_helpers.isRegularQuest(self.getID())

    def getLinkedAction(self, actions):
        return getLinkedActionID(self.getID(), actions)

    def getMainQuest(self, events):
        if not self.isMarathon():
            LOG_ERROR('Trying to find main quest in non-marathon group', self.getID())
            return None
        else:
            for quest in events:
                if events_helpers.isMarathon(quest.getID()):
                    return quest

            LOG_ERROR('There is no main token quest in the marathon', self.getID())
            return None

    def withManyTokenSources(self, svrEvents):
        uniqueTokens = set()
        uniqueChildren = set()
        for qID in self.getGroupEvents():
            quest = svrEvents.get(qID)
            if quest is not None:
                children = quest.getChildren()
                if children:
                    for key, value in children.iteritems():
                        uniqueChildren |= set(value)
                        uniqueTokens.add(key)

        return len(uniqueTokens) == 1 and len(uniqueChildren) > 1


class Quest(ServerEventAbstract):
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ServerEventAbstract.__slots__ + ('_progress', '_children', '_parents', '_parentsName', 'accountReqs', 'vehicleReqs', 'preBattleCond', 'bonusCond', 'postBattleCond', '__linkedActions', '_meta')

    def __init__(self, qID, data, progress=None):
        super(Quest, self).__init__(qID, data)
        self._progress = progress
        self._children, self._parents, self._parentsName = {}, {}, {}
        self._meta = data.get('meta', {})
        conds = dict(data['conditions'])
        preBattle = dict(conds['preBattle'])
        self.accountReqs = AccountRequirements(preBattle['account'])
        self.vehicleReqs = VehicleRequirements(preBattle['vehicle'])
        self.preBattleCond = PreBattleConditions(preBattle['battle'])
        self.bonusCond = BonusConditions(conds['common'], self.getProgressData(), self.preBattleCond)
        self.postBattleCond = PostBattleConditions(conds['postBattle'], self.preBattleCond)
        self._groupID = DEFAULTS_GROUPS.UNGROUPED_QUESTS
        self.__linkedActions = []

    @classmethod
    def postBattleInfo(cls):
        return None

    @classmethod
    def showMissionAction(cls):
        return None

    def getArenaTypes(self):
        arenaTypes = None
        battleCond = self.preBattleCond.getConditions()
        if battleCond:
            bonusTypes = battleCond.find('bonusTypes')
            if bonusTypes:
                arenaTypes = bonusTypes.getValue()
        return arenaTypes

    def isEventBattlesQuest(self):
        arenaTypes = self.getArenaTypes()
        return set(arenaTypes) == set(constants.ARENA_BONUS_TYPE.WT_BATTLES_RANGE) if arenaTypes else False

    def isQuestForBattleRoyale(self):
        arenaTypes = self.getArenaTypes()
        return set(arenaTypes) == set(constants.ARENA_BONUS_TYPE.BATTLE_ROYALE_REGULAR_RANGE) if arenaTypes else False

    def isCompensationPossible(self):
        return events_helpers.isMarathon(self.getGroupID()) and bool(self.getBonuses('tokens'))

    def shouldBeShown(self):
        return self.isAvailable().isValid and self.lobbyContext.getServerSettings().isMapsTrainingEnabled() if events_helpers.isMapsTraining(self.getGroupID()) else True

    def getGroupType(self):
        return getGroupTypeByID(self.getGroupID())

    def isAvailable(self):
        return ValidationResult(False, 'dailyComplete') if self.bonusCond.getBonusLimit() is not None and self.bonusCond.isDaily() and self.isCompleted() else super(Quest, self).isAvailable()

    @property
    def linkedActions(self):
        return self.__linkedActions

    @linkedActions.setter
    def linkedActions(self, value):
        self.__linkedActions = value

    def getUserType(self):
        return i18n.makeString(QUESTS.ITEM_TYPE_QUEST)

    def getProgressExpiryTime(self):
        return self._data.get('progressExpiryTime', time.time())

    def isCompletedByGroup(self, groupByKey):
        bonusLimit = self.bonusCond.getBonusLimit()
        if bonusLimit is not None:
            if self.bonusCond.getGroupByValue() is None:
                return self.isCompleted()
            if self._progress is not None:
                return bonusLimit <= self.getBonusCount(groupByKey)
        return False

    def isCompleted(self, progress=None):
        progress = progress or self._progress
        bonusLimit = self.bonusCond.getBonusLimit()
        if bonusLimit is not None:
            groupBy = self.bonusCond.getGroupByValue()
            if groupBy is None:
                return self.getBonusCount(progress=progress) >= bonusLimit
            if progress is not None:
                if groupBy == 'nation':
                    return self.__checkGroupedCompletion(nations.AVAILABLE_NAMES, progress, bonusLimit)
                if groupBy == 'level':
                    return self.__checkGroupedCompletion(xrange(1, constants.MAX_VEHICLE_LEVEL + 1), progress, bonusLimit, keyMaker=lambda lvl: 'level %d' % lvl)
                if groupBy == 'class':
                    return self.__checkGroupedCompletion(constants.VEHICLE_CLASSES, progress, bonusLimit)
                if groupBy == 'vehicle':
                    pass
        return super(Quest, self).isCompleted()

    def setChildren(self, children):
        self._children = children

    def getChildren(self):
        return self._children

    def setParents(self, parents):
        self._parents = parents

    def getParents(self):
        return self._parents

    def setParentsName(self, parentsName):
        self._parentsName = parentsName

    def getParentsName(self):
        return self._parentsName

    def getBonusCount(self, groupByKey=None, progress=None):
        progress = progress or self._progress
        if progress is not None:
            groupBy = self.bonusCond.getGroupByValue()
            if groupBy is None:
                return progress.get(None, {}).get('bonusCount', 0)
            if groupByKey is not None:
                return progress.get(groupByKey, {}).get('bonusCount', 0)
            return sum((p.get('bonusCount', 0) for p in progress.itervalues()))
        else:
            return 0

    def getProgressData(self):
        return self._progress or {}

    def getRawBonuses(self):
        return self.getData().get('bonus', {})

    def getBonuses(self, bonusName=None, isCompensation=False, bonusData=None, ctx=None):
        result = []
        bonusData = bonusData or self.getRawBonuses()
        if bonusName is None:
            for name, value in bonusData.iteritems():
                for bonus in getBonuses(self, name, value, isCompensation, ctx=ctx):
                    result.append(self._bonusDecorator(bonus))

                if name == 'vehicles':
                    stylesData = self.__getVehicleStyleBonuses(value)
                    if stylesData:
                        for bonus in getBonuses(self, 'customizations', stylesData, isCompensation, ctx=ctx):
                            result.append(self._bonusDecorator(bonus))

        elif bonusName in bonusData:
            for bonus in getBonuses(self, bonusName, bonusData[bonusName], isCompensation, ctx=ctx):
                result.append(self._bonusDecorator(bonus))

        return sorted(result, cmp=compareBonuses, key=operator.methodcaller('getName'))

    @staticmethod
    def __getVehicleStyleBonuses(vehiclesData):
        stylesData = []
        for vehData in vehiclesData.itervalues():
            customization = vehData.get('customization', None)
            if customization is not None:
                styleData = {'value': 1,
                 'custType': 'style',
                 'id': customization.get('styleId', -1),
                 'customCompensation': customization.get('customCompensation', None)}
                stylesData.append(styleData)

        return stylesData

    def getCompensation(self):
        compensatedToken = findFirst(lambda t: t.isDisplayable(), self.accountReqs.getTokens())
        return {compensatedToken.getID(): self.getBonuses(isCompensation=True)} if compensatedToken else {}

    def hasPremIGRVehBonus(self):
        vehBonuses = self.getBonuses('vehicles')
        for vehBonus in vehBonuses:
            vehicles = vehBonus.getValue()
            for intCD, data in vehicles.iteritems():
                item = self.itemsCache.items.getItemByCD(intCD)
                if item.isPremiumIGR and data.get('rent', None) is not None:
                    return True

        return False

    def getSuitableVehicles(self):
        return self.vehicleReqs.getSuitableVehicles()

    def hasBonusType(self, bonusType):
        bonusTypesCond = self.preBattleCond.getConditions().find('bonusTypes')
        return bonusTypesCond is None or bonusType in bonusTypesCond.getValue()

    @staticmethod
    def _bonusDecorator(bonus):
        return bonus

    def __checkGroupedCompletion(self, values, progress, bonusLimit=None, keyMaker=lambda v: v):
        bonusLimit = bonusLimit or self.bonusCond.getBonusLimit()
        for value in values:
            if bonusLimit > self.getBonusCount(groupByKey=keyMaker(value), progress=progress):
                return False

        return True

    def _checkConditions(self):
        return self.accountReqs.isAvailable() and (self.vehicleReqs.isAnyVehicleAcceptable() or self.vehicleReqs.getSuitableVehicles())

    def _checkVehicleConditions(self, vehicle):
        return self.vehicleReqs.isAnyVehicleAcceptable() or vehicle.intCD in self.vehicleReqs.getSuitableVehicles()


class TokenQuest(Quest):

    def __init__(self, qID, data, progress=None):
        super(TokenQuest, self).__init__(qID, data, progress)
        self.accountReqs = TokenQuestAccountRequirements(self.accountReqs.getSection())

    def _checkConditions(self):
        return self.accountReqs.isAvailable()


class BattleMattersTokenQuest(TokenQuest):

    def _checkConditions(self):
        res = _isBattleMattersQuestAvailable(self)
        if res is None:
            res = super(BattleMattersTokenQuest, self)._checkConditions()
        return res

    def getOrder(self):
        return getIdxFromQuestID(self.getID())

    def getConditionLbl(self):
        return _getConditionLbl(self._data)


class BattleMattersQuest(Quest):

    def _checkConditions(self):
        res = _isBattleMattersQuestAvailable(self)
        if res is None:
            res = super(BattleMattersQuest, self)._checkConditions()
        return res

    def getOrder(self):
        return getIdxFromQuestID(self.getID())

    def getConditionLbl(self):
        return _getConditionLbl(self._data)


def _getConditionLbl(data):
    descriptionLbl = 'description'
    conditions = data.get('conditions')
    for itemName, itemData in conditions:
        if itemName == descriptionLbl:
            return i18n.makeString(getLocalizedData({descriptionLbl: itemData}, descriptionLbl))


class PremiumQuest(Quest):

    def getUserName(self):
        return backport.text(R.strings.quests.premiumQuests.quests.dyn(self.getID()).title())


class DailyQuest(Quest):

    def getLevel(self):
        return self._meta and self._meta.get('level')

    def isSimple(self):
        return self.getLevel() in constants.DailyQuestsLevels.DAILY_SIMPLE

    def isBonus(self):
        return self.getLevel() == constants.DailyQuestsLevels.BONUS

    def isEpic(self):
        return self.getLevel() == constants.DailyQuestsLevels.EPIC

    def getSortKey(self):
        return constants.DailyQuestsLevels.DAILY.index(self.getLevel())

    def getUserName(self):
        return backport.text(R.strings.quests.dailyQuests.postBattle.dyn('genericTitle_%s' % self.getLevel())())


class DailyTokenQuest(TokenQuest):

    def getLevel(self):
        return self._meta and self._meta.get('level')

    def isBonus(self):
        return self.getLevel() == constants.DailyQuestsLevels.BONUS_SUBS

    def getSortKey(self):
        return constants.DailyQuestsLevels.SUBS.index(self.getLevel())

    def getUserName(self):
        return backport.text(R.strings.quests.dailyQuests.postBattle.dyn('genericTitle_%s' % self.getLevel())())


class PersonalQuest(Quest):
    __slots__ = Quest.__slots__ + ('expiryTime',)

    def __init__(self, qID, data, progress=None, expiryTime=None):
        super(PersonalQuest, self).__init__(qID, data, progress)
        self.expiryTime = expiryTime

    def getFinishTime(self):
        return min(super(PersonalQuest, self).getFinishTime(), self.expiryTime) if self.expiryTime is not None else super(PersonalQuest, self).getFinishTime()

    def getRequiredToken(self):
        return self._data.get('requiredToken', None)


class RankedQuest(Quest):
    __slots__ = Quest.__slots__ + ('__rankedData', '__qualificationBattlesCount', '__isQualificationQuest')

    def __init__(self, qID, data, progress=None):
        super(RankedQuest, self).__init__(qID, data, progress)
        self.__rankedData = self.__parseRankSeasonData(data)
        self.__isQualificationQuest = isQualificationQuestID(qID)
        self.__qualificationBattlesCount = getQualificationBattlesCountFromID(qID) if self.__isQualificationQuest else 0

    def getRank(self):
        return self.__rankedData.get('rank')

    def getSeasonID(self):
        return self.__rankedData.get('season')

    def getCycleID(self):
        return self.__rankedData.get('cycle')

    def isProcessedAtCycleEnd(self):
        return self.__rankedData['subtype'] == 'cycle'

    def isForRank(self):
        return self.__rankedData['subtype'] == 'rank'

    def isQualificationQuest(self):
        return self.__isQualificationQuest

    def getQualificationBattlesCount(self):
        return self.__qualificationBattlesCount

    @classmethod
    def __parseRankSeasonData(cls, data):
        conditionsDict = cls.__dictMaker(data.get('conditions', {}))
        rankedData = conditionsDict.get('common', {})
        result = {}
        if rankedData:
            for key in ('season', 'cycle'):
                if key in rankedData:
                    result[key] = rankedData[key]['value']

            if 'maxRank' in rankedData:
                rank = rankedData['maxRank']
                if 'and' in rank:
                    rankBounds = rank['and']
                    result['rank'] = int(first(rankBounds.values())['value'])
                else:
                    result['rank'] = int(rank['greaterOrEqual']['value'])
        result['subtype'] = data.get('subtype')
        return result

    @classmethod
    def __dictMaker(cls, kVList):
        result = {}
        for key, value in dict(kVList).iteritems():
            if isinstance(value, (list, tuple)) and value:
                result[key] = cls.__dictMaker(value)
            result[key] = value

        return result


ActionData = namedtuple('ActionData', 'discountObj priority uiDecoration')

class Action(ServerEventAbstract):
    __slots__ = ServerEventAbstract.__slots__ + ('__linkedQuests',)

    def __init__(self, qID, data):
        super(Action, self).__init__(qID, data)
        self._groupID = DEFAULTS_GROUPS.UNGROUPED_ACTIONS
        self.__linkedQuests = []

    @property
    def linkedQuests(self):
        return self.__linkedQuests

    @linkedQuests.setter
    def linkedQuests(self, value):
        self.__linkedQuests = value

    def getUserType(self):
        return i18n.makeString(QUESTS.ITEM_TYPE_ACTION)

    def getActions(self):
        result = {}
        if 'steps' not in self._data:
            return result
        else:
            for stepData in self._data['steps']:
                if 'name' in stepData:
                    mName = stepData['name']
                else:
                    mName = None
                if 'priority' in stepData:
                    priority = stepData['priority']
                else:
                    priority = None
                if 'params' in stepData:
                    params = stepData['params']
                else:
                    params = None
                if 'uiDecoration' in stepData:
                    uiDecoration = stepData['uiDecoration']
                else:
                    uiDecoration = None
                m = getModifierObj(mName, params)
                if m is None:
                    continue
                modifiers = m.splitModifiers()
                for modifier in modifiers:
                    if mName in result:
                        result[mName].append(ActionData(modifier, priority, uiDecoration))
                    result[mName] = [ActionData(modifier, priority, uiDecoration)]

            return result

    def getModifiers(self):
        result = {}
        for stepData in self._data.get('steps'):
            mName = stepData.get('name')
            m = getModifierObj(mName, stepData.get('params'))
            if m is None:
                continue
            if mName in result:
                result[mName].update(m)
            result[mName] = m

        return sorted(result.itervalues(), key=operator.methodcaller('getName'), cmp=compareModifiers)


class PMCampaign(object):
    __slots__ = ('__id', '__info', '__operations', '__isUnlocked')

    def __init__(self, campaignID, info):
        self.__id = campaignID
        self.__info = info
        self.__operations = {}
        self.__isUnlocked = False

    def getID(self):
        return self.__id

    def getName(self):
        return self.__info['name']

    def getUserName(self):
        return self.__info['userString']

    def getUserDescription(self):
        return self.__info['description']

    def getOperations(self):
        return self.__operations

    def isUnlocked(self):
        return self.__isUnlocked

    def updateProgress(self):
        for tile in self.__operations.itervalues():
            if tile.isUnlocked():
                self.__isUnlocked = True
                break

    def addOperation(self, operation):
        if operation.getID() not in self.__operations:
            self.__operations[operation.getID()] = operation


class PMOperation(object):
    __slots__ = ('__id', '__info', '__quests', '__initialQuests', '__finalQuests', '__isUnlocked', '__hasRequiredVehicles', '__achievements', '__tokens', '__bonuses', '__isAwardAchieved', '__freeTokensCount', '__freeTokensTotalCount', '__branch', '__disabled')

    def __init__(self, tileID, info, branch=0):
        self.__id = tileID
        self.__info = info
        self.__quests = {}
        self.__initialQuests = {}
        self.__finalQuests = {}
        self.__isUnlocked = False
        self.__hasRequiredVehicles = False
        self.__achievements = dict(((chID, (ACHIEVEMENT_BLOCK.TOTAL, aName)) for chID, aName in self.__info['achievements'].iteritems()))
        self.__tokens = {}
        self.__bonuses = {}
        self.__isAwardAchieved = False
        self.__freeTokensCount = 0
        self.__freeTokensTotalCount = 0
        self.__branch = branch
        self.__disabled = False

    def getID(self):
        return self.__id

    def getBranch(self):
        return self.__branch

    def getNextOperationIDs(self):
        return self.__info['nextTileIDs']

    def getName(self):
        return self.__info['name']

    def getUserName(self):
        return self.__info['userString']

    def getShortUserName(self):
        return i18n.makeString('#personal_missions:operations/title%d' % self.getID())

    def getUserDescription(self):
        return self.__info['description']

    def getChainClassifier(self, chainID):
        firstQuest = first(self.__quests.get(chainID, {}).itervalues())
        return firstQuest.getQuestClassifier() if firstQuest is not None else None

    def getChainByClassifierAttr(self, classifier):
        return findFirst(lambda (chainID, chain): self.getChainClassifier(chainID).classificationAttr == classifier, self.getQuests().iteritems(), (None, None))

    def getIterationChain(self):
        if self.__branch == PM_BRANCH.REGULAR:
            return VEHICLE_TYPES_ORDER
        return nations.ALLIANCES_TAGS_ORDER if self.__branch == PM_BRANCH.PERSONAL_MISSION_2 else ()

    def getChainName(self, chainID):
        classifier = self.getChainClassifier(chainID).classificationAttr
        if self.__branch == PM_BRANCH.REGULAR:
            return PERSONAL_MISSIONS.chainNameByVehicleType(classifier)
        if self.__branch == PM_BRANCH.PERSONAL_MISSION_2:
            allianceId = nations.ALLIANCE_IDS[classifier]
            return PERSONAL_MISSIONS.getAllianceName(allianceId)

    def getAllianceID(self, chainID):
        if self.__branch == PM_BRANCH.PERSONAL_MISSION_2:
            classifier = self.getChainClassifier(chainID).classificationAttr
            return nations.ALLIANCE_IDS[classifier]

    def getChainDescription(self, chainID):
        if self.__branch == PM_BRANCH.PERSONAL_MISSION_2:
            classifier = self.getChainClassifier(chainID).classificationAttr
            allianceId = nations.ALLIANCE_IDS[classifier]
            return PERSONAL_MISSIONS.getAllianceDetails(allianceId)

    def getChainIcon(self, chainID):
        classifier = self.getChainClassifier(chainID).classificationAttr
        if self.__branch == PM_BRANCH.REGULAR:
            return Vehicle.getTypeBigIconPath(classifier)
        if self.__branch == PM_BRANCH.PERSONAL_MISSION_2:
            allianceId = nations.ALLIANCE_IDS[classifier]
            return RES_ICONS.getAllianceIcon(allianceId)

    def getSmallChainIcon(self, chainID):
        classifier = self.getChainClassifier(chainID).classificationAttr
        if self.__branch == PM_BRANCH.REGULAR:
            return Vehicle.getTypeSmallIconPath(classifier, False)
        return RES_ICONS.getAlliance17x19Icon(classifier) if self.__branch == PM_BRANCH.PERSONAL_MISSION_2 else ''

    def getChainMajorTag(self, chainID):
        firstQuest = first(self.__quests.get(chainID, {}).itervalues())
        return firstQuest.getMajorTag() if firstQuest is not None else None

    def getChainSortKey(self, chainID):
        return self.getChainMajorTag(chainID)

    def getChainTotalTokensCount(self, chainID, isMainBonuses=None):
        result = 0
        for tokenID in self.__info['tokens']:
            for q in self.__quests[chainID].itervalues():
                for tokenBonus in q.getBonuses('tokens', isMainBonuses):
                    tokens = tokenBonus.getTokens()
                    if tokenID in tokens:
                        result += tokens[tokenID].count

        return result

    def getIconID(self):
        return self.__info['iconID']

    def getCampaignID(self):
        return self.__info['seasonID']

    def getChainSize(self):
        return self.__info['questsInChain']

    def getQuestsCount(self):
        return self.__info['chainsCount'] * self.getChainSize()

    def getPrice(self):
        return self.__info['price']

    def getQuests(self):
        return self.__quests

    def getQuestsInChainByFilter(self, chainID, filterFunc=lambda v: True):
        result = {}
        for qID, q in self.__quests[chainID].iteritems():
            if filterFunc(q):
                result[qID] = q

        return result

    def getQuestsByFilter(self, filterFunc=lambda v: True):
        result = {}
        for _, quests in self.__quests.iteritems():
            for qID, q in quests.iteritems():
                if filterFunc(q):
                    result[qID] = q

        return result

    def getInProgressQuests(self):
        return self.getQuestsByFilter(lambda quest: quest.isInProgress())

    def getCompletedQuests(self, isRewardReceived=None):
        return self.getQuestsByFilter(lambda quest: quest.isCompleted(isRewardReceived=isRewardReceived))

    def getFullCompletedQuests(self, isRewardReceived=None):
        return self.getQuestsByFilter(lambda quest: quest.isFullCompleted(isRewardReceived=isRewardReceived))

    def getPawnedQuests(self):
        return self.getQuestsByFilter(operator.methodcaller('areTokensPawned'))

    def isCompleted(self, isRewardReceived=None):
        return len(self.getCompletedQuests(isRewardReceived)) == self.getQuestsCount()

    def isInProgress(self):
        return len(self.getInProgressQuests()) > 0

    def isFullCompleted(self, isRewardReceived=None):
        return len(self.getFullCompletedQuests(isRewardReceived)) == self.getQuestsCount()

    def isAwardAchieved(self):
        return self.__isAwardAchieved

    def getCompletedFinalQuests(self, isRewardReceived=None):
        return self.getQuestsByFilter(lambda quest: quest.isCompleted(isRewardReceived=isRewardReceived) and quest.isFinal())

    def getInitialQuests(self):
        return self.__initialQuests

    def getFinalQuests(self):
        return self.__finalQuests

    def isAvailable(self):
        if self.isDisabled():
            return ValidationResult(False, 'disabled')
        if not self.isUnlocked():
            return ValidationResult(False, 'isLocked')
        return ValidationResult(False, 'noVehicle') if not self.hasRequiredVehicles() else ValidationResult(True, '')

    def isUnlocked(self):
        return self.__isUnlocked

    def setDisabledState(self, value):
        self.__disabled = value
        for _, questsInChain in self.__quests.iteritems():
            for _, q in questsInChain.iteritems():
                q.setDisabledState(value)

    def isDisabled(self):
        return self.__disabled

    def hasRequiredVehicles(self):
        return bool(self.getQuestsByFilter(operator.methodcaller('hasRequiredVehicles')))

    def getAchievements(self):
        return self.__achievements

    def getTokens(self):
        return self.__tokens

    def getTokensCount(self):
        return tuple([ sum(tokensCount) for tokensCount in zip(*self.__tokens.values()) ])

    def getTotalTokensCount(self):
        result = 0
        for chainID in self.__quests.iterkeys():
            result += self.getChainTotalTokensCount(chainID)

        return result

    def getTokensPawnedCount(self):
        result = 0
        for quest in self.getPawnedQuests().itervalues():
            result += quest.getPawnCost()

        return result

    def getFreeTokensCount(self):
        return self.__freeTokensCount

    def getFreeTokensTotalCount(self):
        return self.__freeTokensTotalCount

    def getBonuses(self):
        return self.__bonuses

    def getVehicleBonus(self):
        for bonuses in self.getBonuses().itervalues():
            for bonus in bonuses:
                if bonus.getName() == 'vehicles':
                    for vehicle, _ in bonus.getVehicles():
                        return vehicle

        return None

    def updateProgress(self, eventsCache):
        qp = eventsCache.questsProgress
        self.__isUnlocked = False
        for quest in self.__initialQuests.itervalues():
            if quest.isUnlocked():
                self.__isUnlocked = True
                break

        hiddenQuests = eventsCache.getHiddenQuests()
        operationTokensFinder = finders.multipleTokenFinder(self.__info['tokens'])
        self.__tokens, self.__bonuses = {}, {}
        quest = finders.getQuestByTokenAndBonus(hiddenQuests, operationTokensFinder, finders.operationCompletionBonusFinder(self))
        if quest is not None:
            for token in quest.accountReqs.getTokens():
                if token.getID() in self.__info['tokens']:
                    self.__tokens[token.getID()] = (qp.getTokenCount(token.getID()), token.getNeededCount())
                    self.__bonuses.setdefault(token.getID(), []).extend(quest.getBonuses())

        else:
            LOG_ERROR('Main token quest was not found for Personal missions operation!', self.getID())
        self.__hasRequiredVehicles = False
        self.__freeTokensCount = 0
        self.__freeTokensTotalCount = 0
        for quests in self.__quests.itervalues():
            for quest in quests.itervalues():
                tokenBonuses = quest.getBonuses('tokens')
                for bonus in tokenBonuses:
                    if bonus.getName() == 'freeTokens':
                        bonusCount = bonus.getCount()
                        self.__freeTokensTotalCount += bonusCount
                        if quest.isFullCompleted():
                            self.__freeTokensCount += bonusCount

        tokenCount = qp.getTokenCount(finders.PERSONAL_MISSION_COMPLETE_TOKEN % (self.getCampaignID(), self.getID()))
        self.__isAwardAchieved = tokenCount > 0
        return

    def addQuest(self, quest):
        questID = quest.getID()
        chain = self.__quests.setdefault(quest.getChainID(), {})
        if questID not in chain:
            chain[questID] = quest
            if quest.isInitial():
                self.__initialQuests[questID] = quest
            elif quest.isFinal():
                self.__finalQuests[quest.getChainID()] = quest


class PersonalMission(ServerEventAbstract):
    __slots__ = ServerEventAbstract.__slots__ + ('__pmType', '__pqProgress', '__campaignID', '__hasRequiredVehicles', '__canBePawned', '__conditionsProgress', '__disabled', '__conditionsConfig')
    ONE_BATTLE_OPERATIONS_IDS = (1, 2, 3, 4, 6)
    _TankmanBonus = namedtuple('_TankmanBonus', ('tankman', 'isMain'))

    def __init__(self, qID, pmType, progress=None, campaignID=None):
        super(PersonalMission, self).__init__(qID, pmType.mainQuestInfo)
        self.__pmType = pmType
        self.__pqProgress = progress
        self.__campaignID = campaignID
        self.__hasRequiredVehicles = False
        self.__canBePawned = False
        self.__conditionsProgress = None
        self.__disabled = False
        self.__conditionsConfig = getQuestConfig(self.__pmType.generalQuestID)
        return

    def isAvailable(self):
        if self.isDisabled():
            return ValidationResult(False, 'disabled')
        if not self.isUnlocked():
            return ValidationResult(False, 'isLocked')
        return ValidationResult(False, 'noVehicle') if not self.hasRequiredVehicles() else ValidationResult(True, '')

    def getDummyHeaderType(self):
        return DISPLAY_TYPE.NONE if self.getOperationID() in self.ONE_BATTLE_OPERATIONS_IDS else DISPLAY_TYPE.SIMPLE

    def isOneBattleQuest(self):
        return self.getOperationID() in self.ONE_BATTLE_OPERATIONS_IDS

    def getConditionsProgress(self):
        return self.__conditionsProgress

    def getConditionsConfig(self):
        return self.__conditionsConfig or {}

    def setRequiredVehiclesPresence(self, hasRequiredVehicles):
        self.__hasRequiredVehicles = hasRequiredVehicles

    def setCanBePawned(self, canBePawned):
        self.__canBePawned = canBePawned

    def hasRequiredVehicles(self):
        return self.__hasRequiredVehicles

    def getPMType(self):
        return self.__pmType

    def getMainQuestID(self):
        return self.__pmType.mainQuestInfo['id']

    def getAddQuestID(self):
        return self.__pmType.addQuestInfo['id']

    def getInternalID(self):
        return self.__pmType.internalID

    def getChainID(self):
        return self.__pmType.chainID

    def getOperationID(self):
        return self.__pmType.tileID

    def getCampaignID(self):
        return self.__campaignID

    def getUserType(self):
        return i18n.makeString(QUESTS.ITEM_TYPE_PERSONALMISSION)

    def getUserName(self):
        return self.__pmType.userString

    def getShortUserName(self):
        return self.__pmType.shortUserString

    def getUserDescription(self):
        return self.__pmType.description

    def getUserAdvice(self):
        return self.__pmType.advice

    def getGeneralQuestID(self):
        return self.__pmType.generalQuestID

    def getVehMinLevel(self):
        return self.__pmType.minLevel

    def getVehMaxLevel(self):
        return self.__pmType.maxLevel

    def getQuestBranch(self):
        return self.__pmType.branch

    def getQuestBranchName(self):
        return PM_BRANCH.TYPE_TO_NAME[self.getQuestBranch()]

    def setDisabledState(self, value):
        self.__disabled = value

    def isDisabled(self):
        return self.__disabled

    def isUnlocked(self):
        return self.__pqProgress is not None and self.__pqProgress.unlocked

    def isInProgress(self):
        return self.__pqProgress is not None and self.__pqProgress.selected

    def isAvailableToPerform(self):
        return self.__pqProgress is not None and self.__pqProgress.unlocked and self.__pqProgress.state <= _PMS.UNLOCKED and not self.isDisabled()

    def hasProgress(self):
        return self.__pqProgress.state > _PMS.NONE

    def isInitial(self):
        return self.__pmType.isInitial

    def isFinal(self):
        return self.__pmType.isFinal

    @property
    def isOnPause(self):
        return self.__checkForFlags(PM_FLAG.PAUSE)

    def getQuestClassifier(self):
        return self.__pmType.classifier

    def getMajorTag(self):
        return self.__pmType.getMajorTag()

    def isMainCompleted(self, isRewardReceived=None):
        if isRewardReceived is True:
            states = (_PMS.MAIN_REWARD_GOTTEN, _PMS.ALL_REWARDS_GOTTEN)
        elif isRewardReceived is False:
            states = (_PMS.NEED_GET_MAIN_REWARD, _PMS.NEED_GET_ALL_REWARDS)
        else:
            states = (_PMS.MAIN_REWARD_GOTTEN,
             _PMS.ALL_REWARDS_GOTTEN,
             _PMS.NEED_GET_MAIN_REWARD,
             _PMS.NEED_GET_ALL_REWARDS)
        return self.__checkForStates(*states)

    def isFullCompleted(self, isRewardReceived=None):
        if isRewardReceived is True:
            states = (_PMS.ALL_REWARDS_GOTTEN,)
        elif isRewardReceived is False:
            states = (_PMS.NEED_GET_ALL_REWARDS,)
        else:
            states = _PMS.COMPLETED
        return self.__checkForStates(*states)

    def isCompleted(self, progress=None, isRewardReceived=None):
        return self.isMainCompleted(isRewardReceived) or self.isFullCompleted(isRewardReceived)

    def areTokensPawned(self):
        return self.isMainCompleted() and self.__pqProgress is not None and self.__pqProgress.pawned

    def getPawnCost(self):
        if self.isFinal():
            pawnCost = PM_BRANCH_TO_FINAL_PAWN_COST[self.getQuestBranch()]
        else:
            pawnCost = constants.PERSONAL_MISSION_PAWN_COST
        return pawnCost

    def canBeSelected(self):
        return self.isUnlocked() and not self.isFullCompleted() and not self.isInProgress()

    def canBePawned(self):
        return self.__canBePawned and not self.isMainCompleted()

    def isDone(self):
        return self.__checkForStates(_PMS.ALL_REWARDS_GOTTEN)

    def needToGetMainReward(self):
        return self.__checkForStates(_PMS.NEED_GET_ALL_REWARDS, _PMS.NEED_GET_MAIN_REWARD)

    def needToGetAddReward(self):
        return self.__checkForStates(_PMS.NEED_GET_ALL_REWARDS, _PMS.NEED_GET_ADD_REWARD)

    def needToGetAllReward(self):
        return self.__checkForStates(_PMS.NEED_GET_ALL_REWARDS)

    def needToGetReward(self):
        return self.__checkForStates(*_PMS.NEED_GET_REWARD)

    def updateProgress(self, questsProgress):
        self.__pqProgress = questsProgress.getPersonalMissionProgress(self.__pmType, self._id)
        self.__conditionsProgress = questsProgress.getConditionsProgress(self.__pmType.generalQuestID)

    def updatePqStateInBattle(self, pqState):
        if self.__pqProgress:
            self.__pqProgress = PersonalMissionsProgressRequester.PersonalMissionProgress(state=pqState, flags=self.__pqProgress.flags, selected=self.__pqProgress.selected, unlocked=self.__pqProgress.unlocked, pawned=self.__pqProgress.pawned)
        else:
            self.__pqProgress = PersonalMissionsProgressRequester.PersonalMissionProgress(state=pqState, flags=PM_FLAG.NONE, selected=(), unlocked=0, pawned=False)

    def getBonuses(self, bonusName=None, filterFunc=None, isMain=None, returnAwardList=False, isDelayed=False, ctx=None):
        if isMain is None:
            data = (self.__pmType.mainQuestInfo, self.__pmType.addQuestInfo)
        elif isMain:
            data = (self.__pmType.mainQuestInfo,)
        else:
            data = (self.__pmType.addQuestInfo,)
        if returnAwardList:
            data = (self.__pmType.addAwardListQuestInfo,)
        result = []
        for d in data:
            if isDelayed:
                bonuses = d.get('bonusDelayed', {}).iteritems()
            else:
                bonuses = d.get('bonus', {}).iteritems()
            for n, v in bonuses:
                if bonusName is not None and n != bonusName:
                    continue
                if filterFunc is not None and not filterFunc(n, v):
                    continue
                result.extend(getBonuses(self, n, v, ctx=ctx))

        return sorted(result, cmp=compareBonuses, key=operator.methodcaller('getName'))

    def getTankmanBonus(self):
        for isMainBonus in (True, False):
            for bonus in self.getBonuses(isMain=isMainBonus, isDelayed=True):
                if bonus.getName() == 'tankwomanBonus':
                    return self._TankmanBonus(bonus, isMainBonus)

        return self._TankmanBonus(None, None)

    @staticmethod
    def needToGetTankWoman(quest):
        bonus = quest.getTankmanBonus()
        return bonus.tankman and (quest.needToGetAddReward() and not bonus.isMain or quest.needToGetMainReward() and bonus.isMain)

    def __checkForStates(self, *statesToCheck):
        return self.__pqProgress is not None and self.__pqProgress.state in statesToCheck

    def __checkForFlags(self, flagsToCheck):
        return self.__pqProgress is not None and self.__pqProgress.flags & flagsToCheck == flagsToCheck

    def __repr__(self):
        return 'PQuest<id=%d; state=%s; flags=%s unlocked=%s>' % (self._id,
         self.__pqProgress.state,
         self.__pqProgress.flags,
         self.isUnlocked())


class MotiveQuest(Quest):

    def getUserName(self):
        return i18n.makeString(Quest.getUserName(self))

    def getGroupID(self):
        return DEFAULTS_GROUPS.MOTIVE_QUESTS

    def getDescription(self):
        return i18n.makeString(Quest.getDescription(self))

    def getParents(self):
        return {}

    def getTips(self):
        return getLocalizedData(self._data, 'advice')

    def getAwardMsg(self):
        return getLocalizedData(self._data, 'congratulation')

    def getRequirementsStr(self):
        return getLocalizedData(self._data, 'requirements')


class WtQuest(Quest):
    gameEventController = dependency.descriptor(IWhiteTigerController)

    @property
    def isBossQuest(self):
        return self.getGroupID().startswith(WT_BOSS_GROUP_ID)

    def isAvailable(self):
        return ValidationResult(False, WT_QUEST_UNAVAILABLE_NOT_ENOUGH_TICKETS_REASON) if self.isBossQuest and not self.gameEventController.hasEnoughTickets() and not self.gameEventController.hasSpecialBoss() else super(WtQuest, self).isAvailable()

    def isHidden(self):
        return super(WtQuest, self).isHidden() or not self._checkConditions()


def _getTileIconPath(tileIconID, prefix, state):
    return '../maps/icons/quests/tiles/%s_%s_%s.png' % (tileIconID, prefix, state)


def getTileNormalUpIconPath(tileIconID):
    return _getTileIconPath(tileIconID, 'color', 'up')


def getTileNormalOverIconPath(tileIconID):
    return _getTileIconPath(tileIconID, 'color', 'over')


def getTileGrayUpIconPath(tileIconID):
    return _getTileIconPath(tileIconID, 'gray', 'up')


def getTileGrayOverIconPath(tileIconID):
    return _getTileIconPath(tileIconID, 'gray', 'over')


class IQuestBuilder(object):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        raise NotImplementedError

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        raise NotImplementedError


class PersonalQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return questType == constants.EVENT_TYPE.PERSONAL_QUEST

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        return PersonalQuest(qID, data, progress, expiryTime)


class GroupQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return questType == constants.EVENT_TYPE.GROUP

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        return Group(qID, data)


class MotiveQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return questType == constants.EVENT_TYPE.MOTIVE_QUEST

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        return MotiveQuest(qID, data, progress)


class RankedQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return questType == constants.EVENT_TYPE.RANKED_QUEST

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        return RankedQuest(qID, data, progress)


class BattleMattersTokenQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return False if questType != constants.EVENT_TYPE.TOKEN_QUEST else qID.startswith(BATTLE_MATTERS_QUEST_ID) or qID.startswith(BATTLE_MATTERS_INTERMEDIATE_QUEST_ID) or qID.startswith(BATTLE_MATTERS_COMPENSATION_QUEST_ID)

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        return BattleMattersTokenQuest(qID, data, progress)


class DailyTokenQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return questType == constants.EVENT_TYPE.TOKEN_QUEST and isDailyQuest(qID)

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        return DailyTokenQuest(qID, data, progress)


class TokenQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return questType == constants.EVENT_TYPE.TOKEN_QUEST

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        return TokenQuest(qID, data, progress)


class BattleMattersQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return qID.startswith(BATTLE_MATTERS_QUEST_ID) or qID.startswith(BATTLE_MATTERS_COMPENSATION_QUEST_ID)

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        return BattleMattersQuest(qID, data, progress)


class PremiumQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return isPremium(qID)

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        return PremiumQuest(qID, data, progress)


class DailyQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return isDailyQuest(qID)

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        return DailyQuest(qID, data, progress)


class WtQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return isWtQuest(qID)

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        return WtQuest(qID, data, progress)


registerQuestBuilders((PersonalQuestBuilder,
 GroupQuestBuilder,
 MotiveQuestBuilder,
 RankedQuestBuilder,
 BattleMattersTokenQuestBuilder,
 DailyTokenQuestBuilder,
 TokenQuestBuilder,
 BattleMattersQuestBuilder,
 PremiumQuestBuilder,
 DailyQuestBuilder,
 WtQuestBuilder))

def createQuest(builders, questType, qID, data, progress=None, expiryTime=None):
    for builder in builders:
        if builder.isSuitableQuest(questType, qID):
            return builder.buildQuest(questType, qID, data, progress, expiryTime)

    return Quest(qID, data, progress)


def createAction(eventType, aID, data):
    return Group(aID, data) if eventType == constants.EVENT_TYPE.GROUP else Action(aID, data)


def _isBattleMattersQuestAvailable(quest):
    if quest.isCompleted():
        return True
    else:
        if isinstance(quest, BattleMattersTokenQuest):
            if super(BattleMattersTokenQuest, quest).isCompleted():
                return True
        for item in quest.accountReqs.getConditions().items:
            if item.getName() == 'token' and item.getID() == '{}_unlock'.format(quest.getID()):
                return item.getReceivedCount() >= item.getNeededCount()

        return None
