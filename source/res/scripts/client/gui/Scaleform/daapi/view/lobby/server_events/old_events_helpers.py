# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/old_events_helpers.py
import operator
from collections import namedtuple, defaultdict
from functools import partial
import constants
from adisp import async
from constants import EVENT_TYPE
from debug_utils import LOG_ERROR
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.server_events.conditions_formatters.bonus import QuestsBonusConditionsFormatter
from gui.Scaleform.daapi.view.lobby.server_events.conditions_formatters.postbattle import QuestsPostBattleConditionsFormatter
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events import formatters, conditions, settings as quest_settings, caches
from gui.server_events.bonuses import getTutorialBonusObj
from gui.server_events.events_helpers import EventInfoModel, EVENT_STATUS, QuestInfoModel
from gui.shared.formatters import text_styles
from gui.shared.gui_items import Vehicle
from gui.shared.gui_items.processors import quests as quests_proc
from gui.shared.utils.decorators import process
from gui.shared.utils.requesters.ItemsRequester import FALLOUT_QUESTS_CRITERIA
from helpers import i18n, int2roman, time_utils, dependency
from potapov_quests import PQ_BRANCH
from quest_xml_source import MAX_BONUS_LIMIT
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_AWARDS_PER_PAGE = 3
FINISH_TIME_LEFT_TO_SHOW = time_utils.ONE_DAY
START_TIME_LIMIT = 5 * time_utils.ONE_DAY
bonusCondFormatter = QuestsBonusConditionsFormatter()
postBattleConditionFormatter = QuestsPostBattleConditionsFormatter()

class _EventInfo(EventInfoModel):

    def getInfo(self, svrEvents, pCur=None, pPrev=None, noProgressInfo=False):
        if noProgressInfo:
            status, statusMsg = EVENT_STATUS.NONE, self._getStatus()[1]
            bonusCount = self.NO_BONUS_COUNT
            qProgCur, qProgTot, qProgbarType, tooltip = (0,
             0,
             formatters.PROGRESS_BAR_TYPE.NONE,
             None)
        else:
            bonusCount = self._getBonusCount(pCur)
            status, statusMsg = self._getStatus(pCur)
            qProgCur, qProgTot, qProgbarType, tooltip = self._getProgressValues(svrEvents, pCur, pPrev)
        isAvailable, _ = self.event.isAvailable()
        return {'questID': str(self.event.getID()),
         'eventType': self.event.getType(),
         'IGR': self.event.isIGR(),
         'taskType': self.event.getUserType(),
         'tasksCount': bonusCount,
         'progrBarType': qProgbarType,
         'progrTooltip': tooltip,
         'maxProgrVal': qProgTot,
         'currentProgrVal': qProgCur,
         'rendererType': QUESTS_ALIASES.RENDERER_TYPE_QUEST,
         'timerDescription': self.getTimerMsg(),
         'status': status,
         'description': self.event.getUserName(),
         'tooltip': TOOLTIPS.QUESTS_RENDERER_LABEL,
         'isSelectable': True,
         'isNew': quest_settings.isNewCommonEvent(self.event),
         'isAvailable': isAvailable}

    def getConditions(self, svrEvents):
        return self._getConditions(svrEvents)

    def getPostBattleInfo(self, svrEvents, pCur, pPrev, isProgressReset, isCompleted):
        index = 0
        progresses = []
        if not isProgressReset and not isCompleted:
            for cond in self.event.bonusCond.getConditions().items:
                if isinstance(cond, conditions._Cumulativable):
                    for groupByKey, (curProg, totalProg, diff, _) in cond.getProgressPerGroup(pCur, pPrev).iteritems():
                        label = cond.getUserString(battleTypeName=self.event.getBattleTypeName())
                        if not diff or not label:
                            continue
                        index += 1
                        progresses.append({'progrTooltip': None,
                         'progrBarType': formatters.PROGRESS_BAR_TYPE.SIMPLE,
                         'maxProgrVal': totalProg,
                         'currentProgrVal': curProg,
                         'description': '%d. %s' % (index, label),
                         'progressDiff': '+ %s' % diff})

            if not len(progresses):
                return
        alertMsg = ''
        if isProgressReset:
            alertMsg = i18n.makeString('#quests:postBattle/progressReset')
        diffStr, awards = ('', None)
        if not isProgressReset and isCompleted:
            awards = self._getBonuses(svrEvents, useIconFormat=False)
        return {'title': self.event.getUserName(),
         'awards': awards,
         'progressList': progresses,
         'alertMsg': alertMsg,
         'questInfo': self.getInfo(svrEvents, pCur, pPrev),
         'personalInfo': [],
         'questType': self.event.getType()}

    @classmethod
    def _getEventsByIDs(cls, ids, svrEvents):
        result = {}
        for eID in ids:
            if eID in svrEvents:
                result[eID] = svrEvents[eID]

        return result

    def _getBonusCount(self, pCur=None):
        return self.NO_BONUS_COUNT

    def _getProgressValues(self, svrEvents=None, pCur=None, pPrev=None):
        return (0,
         0,
         formatters.PROGRESS_BAR_TYPE.NONE,
         None)

    def _getBonuses(self, svrEvents, bonuses=None, useIconFormat=False):
        bonuses = bonuses or self.event.getBonuses()
        result = []
        for b in bonuses:
            if b.isShowInGUI():
                result.append(b.format())

        return formatters.todict([formatters.packTextBlock(', '.join(result))]) if len(result) else []

    def _getConditions(self, svrEvents):
        return []


class _QuestInfo(_EventInfo, QuestInfoModel):
    PROGRESS_TOOLTIP_MAX_ITEMS = 4
    SIMPLE_BONUSES_MAX_ITEMS = 5
    itemsCache = dependency.descriptor(IItemsCache)

    def _getStatus(self, pCur=None):
        if self.event.isCompleted(progress=pCur):
            if self.event.bonusCond.isDaily():
                msg = self._getCompleteDailyStatus('#quests:details/status/completed/daily')
            else:
                msg = i18n.makeString('#quests:details/status/completed')
            return (EVENT_STATUS.COMPLETED, msg)
        else:
            isAvailable, errorMsg = self.event.isAvailable()
            if not isAvailable:
                timeLeftInfo = self.event.getNearestActivityTimeLeft()
                if errorMsg in ('in_future', 'invalid_weekday', 'invalid_time_interval') and timeLeftInfo is not None:
                    startTimeLeft = timeLeftInfo[0]
                    if startTimeLeft > START_TIME_LIMIT:
                        fmt = self._getDateTimeString(self.event.getStartTime())
                    else:
                        fmt = self._getTillTimeString(startTimeLeft)
                    msg = i18n.makeString('#quests:details/status/notAvailable/%s' % errorMsg, time=fmt)
                else:
                    msg = i18n.makeString('#quests:details/status/notAvailable/%s' % errorMsg)
                return (EVENT_STATUS.NOT_AVAILABLE, msg)
            bonus = self.event.bonusCond
            bonusLimit = bonus.getBonusLimit()
            if bonusLimit is None or bonusLimit >= MAX_BONUS_LIMIT:
                msg = i18n.makeString(QUESTS.DETAILS_HEADER_COMPLETION_UNLIMITED)
            else:
                groupBy = bonus.getGroupByValue()
                if bonus.isDaily():
                    key = QUESTS.DETAILS_HEADER_COMPLETION_DAILY
                    if groupBy is not None:
                        key = '#quests:details/header/completion/daily/groupBy%s' % groupBy.capitalize()
                else:
                    key = QUESTS.DETAILS_HEADER_COMPLETION_SINGLE
                    if groupBy is not None:
                        key = '#quests:details/header/completion/single/groupBy%s' % groupBy.capitalize()
                msg = i18n.makeString(key, count=bonusLimit)
            return (EVENT_STATUS.NONE, msg)

    def _getBonuses(self, svrEvents, bonuses=None, useIconFormat=False):
        bonuses = bonuses or self.event.getBonuses()
        result, simpleBonusesList, customizationsList, vehiclesList, iconBonusesList = ([],
         [],
         [],
         [],
         [])
        for b in bonuses:
            if b.isShowInGUI():
                if b.getName() == 'dossier':
                    for achieve in b.getAchievements():
                        result.append(formatters.packAchieveElementByItem(achieve))

                elif b.getName() == 'customizations':
                    customizationsList.extend(b.getList())
                elif b.getName() == 'vehicles':
                    flist = b.formattedList()
                    if flist:
                        vehiclesList.extend(flist)
                elif b.hasIconFormat() and useIconFormat:
                    iconBonusesList.extend(b.getList())
                else:
                    flist = b.formattedList()
                    if flist:
                        simpleBonusesList.extend(flist)

        if len(customizationsList):
            result.append(formatters.packCustomizations(customizationsList))
        if len(iconBonusesList):
            result.append(formatters.packIconAwardBonusBlock(iconBonusesList))
        if len(vehiclesList) > 0:
            vehiclesLbl, _ = self._joinUpToMax(vehiclesList)
            result.append(formatters.packVehiclesBonusBlock(vehiclesLbl, str(self.event.getID())))
        if len(simpleBonusesList) > 0:
            result.append(formatters.packSimpleBonusesBlock(simpleBonusesList))
        parents = [ qID for _, qIDs in self.event.getParents().iteritems() for qID in qIDs ]
        for qID, q in self._getEventsByIDs(parents, svrEvents or {}).iteritems():
            result.append(formatters.packTextBlock(i18n.makeString('#quests:bonuses/item/task', q.getUserName()), questID=qID))

        return formatters.todict(result) if len(result) else formatters.todict([formatters.packTextBlock(text_styles.alert('#quests:bonuses/notAvailable'))])

    def _getBonusCount(self, pCur=None):
        if not self.event.isCompleted(progress=pCur):
            bonusLimit = self.event.bonusCond.getBonusLimit()
            if bonusLimit is None or bonusLimit > 1 or self.event.bonusCond.getGroupByValue() is not None:
                return self.event.getBonusCount(progress=pCur)
        return self.NO_BONUS_COUNT

    def _getProgressValues(self, svrEvents=None, pCur=None, pPrev=None):
        current, total, progressType, tooltip = (0,
         0,
         formatters.PROGRESS_BAR_TYPE.NONE,
         None)
        groupBy = self.event.bonusCond.getGroupByValue()
        condsRoot = self.event.bonusCond.getConditions()
        if self.event.isCompleted(pCur) or condsRoot.isEmpty():
            return (current,
             total,
             progressType,
             tooltip)
        else:
            countOfCumulatives = 0
            cumulatives = defaultdict(list)
            for cond in condsRoot.items:
                if isinstance(cond, conditions._Cumulativable):
                    countOfCumulatives += 1
                    for groupByKey, (cur, tot, _, isCompleted) in cond.getProgressPerGroup(pCur, pPrev).iteritems():
                        if not isCompleted:
                            cumulatives[groupByKey].append((cur, tot))

            if groupBy is None and countOfCumulatives == 1 and len(cumulatives[None]):
                (current, total), progressType = cumulatives[None][0], formatters.PROGRESS_BAR_TYPE.SIMPLE
            else:
                avgProgressesPerGroup = []
                for groupByKey, values in cumulatives.iteritems():
                    progressesSum = sum(map(lambda (c, t): c / float(t), values))
                    avgProgressesPerGroup.append((groupByKey, int(round(100.0 * progressesSum / len(values))), 100))

                avgProgresses = sorted(avgProgressesPerGroup, key=operator.itemgetter(1), reverse=True)
                if len(avgProgresses):
                    (groupByKey, current, total), nearestProgs = avgProgresses[0], avgProgresses[1:]
                    progressType = formatters.PROGRESS_BAR_TYPE.COMMON
                    if groupBy is not None and groupByKey is not None:
                        name, names = ('', '')
                        if groupBy == 'vehicle':
                            name = self.itemsCache.items.getItemByCD(groupByKey).shortUserName
                            names = [ self.itemsCache.items.getItemByCD(intCD).shortUserName for intCD, _, __ in nearestProgs ]
                        elif groupBy == 'nation':
                            name = i18n.makeString('#menu:nations/%s' % groupByKey)
                            names = [ i18n.makeString('#menu:nations/%s' % n) for n, _, __ in nearestProgs ]
                        elif groupBy == 'class':
                            name = i18n.makeString('#menu:classes/%s' % groupByKey)
                            names = [ i18n.makeString('#menu:classes/%s' % n) for n, _, __ in nearestProgs ]
                        elif groupBy == 'level':

                            def makeLvlStr(lvl):
                                return i18n.makeString(QUESTS.TOOLTIP_PROGRESS_GROUPBY_NOTE_LEVEL, int2roman(lvl))

                            name = makeLvlStr(int(groupByKey.replace('level ', '')))
                            names = [ makeLvlStr(int(l.replace('level ', ''))) for l, _, __ in nearestProgs ]
                        note = None
                        if len(names):
                            note = makeHtmlString('html_templates:lobby/quests/tooltips/progress', 'note', {'names': ', '.join(names[:self.PROGRESS_TOOLTIP_MAX_ITEMS])})
                        tooltip = {'header': i18n.makeString(QUESTS.TOOLTIP_PROGRESS_GROUPBY_HEADER),
                         'body': makeHtmlString('html_templates:lobby/quests/tooltips/progress', 'body', {'name': name}),
                         'note': note}
            return (current,
             total,
             progressType,
             tooltip)

    def _getConditions(self, svrEvents):
        result = self._packConditions(svrEvents)
        return formatters.todict(result)

    def _packConditions(self, svrEvents):
        subBlocks = []
        bonus = self.event.bonusCond
        battlesLeft, battlesCount, inrow = None, None, False
        battles = bonus.getConditions().find('battles')
        if battles is not None:
            battlesCount = battles.getTotalValue()
            if not self.event.isCompleted() and bonus.getGroupByValue() is None:
                progress = battles.getProgressPerGroup()
                if None in progress:
                    curProg, totalProg, _, _ = progress[None]
                    battlesLeft = totalProg - curProg
        bonusFmtConds = bonusCondFormatter.format(bonus, self.event)
        if len(bonusFmtConds):
            subBlocks.extend(formatters.indexing(bonusFmtConds))
        postBattleFmtConds = postBattleConditionFormatter.format(self.event.postBattleCond, self.event)
        if len(postBattleFmtConds):
            if len(bonusFmtConds):
                subBlocks.append(formatters.packSeparator(label=i18n.makeString('#quests:details/conditions/postBattle/separator')))
            subBlocks.extend(formatters.indexing(postBattleFmtConds))
        resetLabel = self._getDailyResetStatus('#quests:details/conditions/postBattle/dailyReset', formatters.formatYellow)
        if resetLabel:
            subBlocks.append(formatters.packTextBlock(label=resetLabel))
        result = []
        if len(subBlocks) or battlesCount:
            if not self.event.isGuiDisabled():
                result.append(formatters.packConditionsBlock(battlesCount, battlesLeft, bonus.isInRow(), conditions=subBlocks))
            else:
                result.append(formatters.packConditionsBlock(conditions=subBlocks))
        if bonus.getGroupByValue() is not None and not self.event.isGuiDisabled():
            progressesFmt = bonusCondFormatter.formatGroupByProgresses(bonus, self.event)
            if len(progressesFmt):
                result.append(formatters.packTopLevelContainer(i18n.makeString('#quests:details/conditions/groupBy/%s' % bonus.getGroupByValue()), subBlocks=progressesFmt, isResizable=len(progressesFmt) > 5))
        return result

    @classmethod
    def _joinUpToMax(cls, array, separator=', '):
        if len(array) > cls.SIMPLE_BONUSES_MAX_ITEMS:
            label = separator.join(array[:cls.SIMPLE_BONUSES_MAX_ITEMS]) + '..'
            fullLabel = separator.join(array)
        else:
            label = separator.join(array)
            fullLabel = None
        return (label, fullLabel)


class _PotapovQuestInfo(_QuestInfo):

    def _getBonuses(self, svrEvents, _=None, useIconFormat=True):
        mainBonuses = self.event.getBonuses(isMain=True)
        addBonuses = self.event.getBonuses(isMain=False)
        return (_QuestInfo._getBonuses(self, None, bonuses=mainBonuses, useIconFormat=useIconFormat), _QuestInfo._getBonuses(self, None, bonuses=addBonuses, useIconFormat=False))

    def getPostBattleInfo(self, svrEvents, pCur, pPrev, isProgressReset, isCompleted):

        def _packCondition(titleKey, text):
            return '%s\n%s' % (text_styles.middleTitle(i18n.makeString(titleKey)), text_styles.main(text))

        def _packStatus(completed):
            return 'done' if completed else 'notDone'

        return {'title': self.event.getUserName(),
         'questInfo': self.getInfo(svrEvents),
         'awards': None,
         'progressList': [],
         'alertMsg': '',
         'personalInfo': [{'statusStr': _packStatus(isCompleted[0]),
                           'text': _packCondition(QUESTS.QUESTTASKDETAILSVIEW_MAINCONDITIONS, self.event.getUserMainCondition())}, {'statusStr': _packStatus(isCompleted[1]),
                           'text': _packCondition(QUESTS.QUESTTASKDETAILSVIEW_ADDITIONALCONDITIONS, self.event.getUserAddCondition())}],
         'questType': self.event.getType()}


class _MotiveQuestInfo(_QuestInfo):

    def getPostBattleInfo(self, svrEvents, pCur, pPrev, isProgressReset, isCompleted):
        filterFunc = lambda quest: quest.getType() == EVENT_TYPE.MOTIVE_QUEST and not quest.isCompleted()
        motiveQuests = filter(filterFunc, svrEvents.values())
        info = super(_MotiveQuestInfo, self).getPostBattleInfo(svrEvents, pCur, pPrev, isProgressReset, isCompleted)
        info.update({'isLinkBtnVisible': len(motiveQuests) > 0})
        return info

    def _packConditions(self, svrEvents):
        result = super(_MotiveQuestInfo, self)._packConditions(svrEvents)
        descr = self.event.getDescription()
        if descr:
            result.append(formatters.packTextBlock(formatters.formatGray(descr)))
        return result


def getEventInfoData(event):
    if event.getType() == constants.EVENT_TYPE.POTAPOV_QUEST:
        return _PotapovQuestInfo(event)
    if event.getType() == constants.EVENT_TYPE.MOTIVE_QUEST:
        return _MotiveQuestInfo(event)
    return _QuestInfo(event) if event.getType() in constants.EVENT_TYPE.QUEST_RANGE else _EventInfo(event)


def getEventConditions(event, svrEvents=None):
    return getEventInfoData(event).getConditions(svrEvents)


def getEventPostBattleInfo(event, svrEvents=None, pCur=None, pPrev=None, isProgressReset=False, isCompleted=False):
    return getEventInfoData(event).getPostBattleInfo(svrEvents, pCur or {}, pPrev or {}, isProgressReset, isCompleted)


def getTutorialEventsDescriptor():
    try:
        from tutorial.doc_loader import getQuestsDescriptor
    except ImportError:
        LOG_ERROR('Can not load package tutorial')

        def getQuestsDescriptor():
            return None

    return getQuestsDescriptor()


def getTutorialQuestsBoosters():
    result = defaultdict(list)
    descriptor = getTutorialEventsDescriptor()
    itemsCache = dependency.instance(IItemsCache)
    completed = itemsCache.items.stats.tutorialsCompleted
    if descriptor is not None:
        for chapter in descriptor:
            if not chapter.isBonusReceived(completed) and chapter.getChapterStatus(descriptor, completed) == EVENT_STATUS.NONE:
                bonus = chapter.getBonus()
                if bonus is not None:
                    goodies = bonus.getValues().get('goodies', {})
                    boosterBonus = getTutorialBonusObj('goodies', goodies)
                    for booster, count in boosterBonus.getBoosters().iteritems():
                        if booster.enabled:
                            result[chapter].append((booster, count))

    return result


def getBoosterQuests():
    eventsCache = dependency.instance(IEventsCache)
    itemsCache = dependency.instance(IItemsCache)
    lobbyContext = dependency.instance(ILobbyContext)
    hasTopVehicle = len(itemsCache.items.getVehicles(FALLOUT_QUESTS_CRITERIA.TOP_VEHICLE))
    isFalloutQuestEnabled = lobbyContext.getServerSettings().isFalloutQuestEnabled()
    excludedQuests = (EVENT_TYPE.RANKED_QUEST,)
    return eventsCache.getAllQuests(lambda q: q.isAvailable()[0] and not q.isCompleted() and len(q.getBonuses('goodies')) and not (q.getType() == EVENT_TYPE.POTAPOV_QUEST and q.getPQType().branch == PQ_BRANCH.FALLOUT and (not isFalloutQuestEnabled or not hasTopVehicle)) and q.getType() not in excludedQuests, includePotapovQuests=True)


class _PotapovDependenciesResolver(object):
    eventsCache = dependency.descriptor(IEventsCache)
    _DEPENDENCIES_LIST = namedtuple('HandlersList', ['cache',
     'progress',
     'selectProcessor',
     'refuseProcessor',
     'rewardsProcessor',
     'sorter'])

    @classmethod
    def _makeRandomDependencies(cls):
        return cls._DEPENDENCIES_LIST(cls.eventsCache.random, cls.eventsCache.randomQuestsProgress, quests_proc.RandomQuestSelect, quests_proc.RandomQuestRefuse, quests_proc.PotapovQuestsGetRegularReward, partial(sorted, cmp=Vehicle.compareByVehTypeName))

    @classmethod
    def _makeFalloutDependencies(cls):
        return cls._DEPENDENCIES_LIST(cls.eventsCache.fallout, cls.eventsCache.falloutQuestsProgress, quests_proc.FalloutQuestSelect, quests_proc.FalloutQuestRefuse, quests_proc.PotapovQuestsGetRegularReward, sorted)

    @classmethod
    def chooseList(cls, questsType=None):
        if questsType is None:
            questsType = caches.getNavInfo().selectedPQType
        if questsType == QUESTS_ALIASES.SEASON_VIEW_TAB_RANDOM:
            depList = cls._makeRandomDependencies()
        else:
            depList = cls._makeFalloutDependencies()
        return depList


def getPotapovQuestsCache(questsType=None):
    return _PotapovDependenciesResolver.chooseList(questsType).cache


def getPotapovQuestsProgress(questsType=None):
    return _PotapovDependenciesResolver.chooseList(questsType).progress


def getPotapovQuestsSelectProcessor(questsType=None):
    return _PotapovDependenciesResolver.chooseList(questsType).selectProcessor


def getPotapovQuestsRefuseProcessor(questsType=None):
    return _PotapovDependenciesResolver.chooseList(questsType).refuseProcessor


def getPotapovQuestsRewardProcessor(questsType=None):
    return _PotapovDependenciesResolver.chooseList(questsType).rewardsProcessor


def sortWithQuestType(items, key, questsType=None):
    return _PotapovDependenciesResolver.chooseList(questsType).sorter(items, key=key)


_questBranchToTabMap = {PQ_BRANCH.REGULAR: QUESTS_ALIASES.SEASON_VIEW_TAB_RANDOM,
 PQ_BRANCH.FALLOUT: QUESTS_ALIASES.SEASON_VIEW_TAB_FALLOUT}

def getTabAliasByQuestBranchID(branchID):
    return _questBranchToTabMap[branchID]


def getTabAliasByQuestBranchName(branchName):
    return getTabAliasByQuestBranchID(PQ_BRANCH.NAME_TO_TYPE[branchName])


@async
@process('updating')
def getPotapovQuestAward(quest, callback):
    """ Display special tankwoman award window.
    """
    from gui.server_events.events_dispatcher import showTankwomanAward
    tankman, isMainBonus = quest.getTankmanBonus()
    needToGetTankman = quest.needToGetAddReward() and not isMainBonus or quest.needToGetMainReward() and isMainBonus
    if needToGetTankman and tankman is not None:
        for tmanData in tankman.getTankmenData():
            showTankwomanAward(quest.getID(), tmanData)
            break

        result = None
    else:
        result = yield getPotapovQuestsRewardProcessor()(quest).request()
    callback(result)
    return


def questsSortFunc(a, b):
    """ Sort function for common quests (all except potapov and motive).
    """
    res = cmp(a.isCompleted(), b.isCompleted())
    if res:
        return res
    if res:
        return -res
    res = cmp(a.getPriority(), b.getPriority())
    return res if res else cmp(a.getUserName(), b.getUserName())
