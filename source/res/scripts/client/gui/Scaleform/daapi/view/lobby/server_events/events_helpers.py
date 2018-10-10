# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/events_helpers.py
import operator
from collections import defaultdict
import BigWorld
import constants
from constants import EVENT_TYPE
from gui import makeHtmlString, GUI_NATIONS
from gui.Scaleform import getNationsFilterAssetPath
from gui.Scaleform.daapi.view.lobby.server_events.awards_formatters import OldStyleBonusesFormatter
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import getNationText
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.LINKEDSET import LINKEDSET
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events import formatters, conditions, settings as quest_settings
from gui.server_events.events_helpers import EventInfoModel, MISSIONS_STATES, QuestInfoModel, isLinkedSet
from gui.server_events.events_helpers import getLocalizedMissionNameForLinkedSetQuest, getLocalizedQuestNameForLinkedSetQuest, getLocalizedQuestDescForLinkedSetQuest
from gui.server_events.personal_progress.formatters import PostBattleConditionsFormatter
from gui.shared.formatters import text_styles, icons
from helpers import i18n, int2roman, time_utils, dependency
from helpers.i18n import makeString as _ms
from nations import ALLIANCE_TO_NATIONS
from personal_missions import PM_BRANCH
from quest_xml_source import MAX_BONUS_LIMIT
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_AWARDS_PER_PAGE = 3
FINISH_TIME_LEFT_TO_SHOW = time_utils.ONE_DAY
START_TIME_LIMIT = 5 * time_utils.ONE_DAY

class _EventInfo(EventInfoModel):

    def getInfo(self, svrEvents, pCur=None, pPrev=None, noProgressInfo=False):
        if noProgressInfo:
            status = MISSIONS_STATES.NONE
            bonusCount = self.NO_BONUS_COUNT
            qProgCur, qProgTot, qProgbarType, tooltip = (0,
             0,
             formatters.PROGRESS_BAR_TYPE.NONE,
             None)
        else:
            bonusCount = self._getBonusCount(pCur)
            status, _ = self._getStatus(pCur)
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

    def getPostBattleInfo(self, svrEvents, pCur, pPrev, isProgressReset, isCompleted, progressData):
        index = 0
        progresses = []
        if not isProgressReset and not isCompleted:
            for cond in self.event.bonusCond.getConditions().items:
                if isinstance(cond, conditions._Cumulativable):
                    for _, (curProg, totalProg, diff, _) in cond.getProgressPerGroup(pCur, pPrev).iteritems():
                        label = cond.getUserString()
                        if not diff or not label:
                            continue
                        index += 1
                        progresses.append({'progrTooltip': None,
                         'progrBarType': formatters.PROGRESS_BAR_TYPE.SIMPLE,
                         'maxProgrVal': totalProg,
                         'currentProgrVal': curProg,
                         'description': '%d. %s' % (index, label),
                         'progressDiff': '+ %s' % BigWorld.wg_getIntegralFormat(diff)})

            if not progresses:
                return
        alertMsg = ''
        if isProgressReset:
            alertMsg = i18n.makeString('#quests:postBattle/progressReset')
        _, awards = ('', None)
        if not isProgressReset and isCompleted:
            awards = self._getBonuses(svrEvents)
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

    def _getBonuses(self, svrEvents, bonuses=None):
        return []


class _QuestInfo(_EventInfo, QuestInfoModel):
    PROGRESS_TOOLTIP_MAX_ITEMS = 4
    itemsCache = dependency.descriptor(IItemsCache)

    def _getStatus(self, pCur=None):
        if self.event.isCompleted(progress=pCur):
            if self.event.bonusCond.isDaily():
                msg = self._getCompleteDailyStatus('#quests:details/status/completed/daily')
            else:
                msg = i18n.makeString('#quests:details/status/completed')
            return (MISSIONS_STATES.COMPLETED, msg)
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
                return (MISSIONS_STATES.NOT_AVAILABLE, msg)
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
            return (MISSIONS_STATES.NONE, msg)

    def _getBonuses(self, svrEvents, bonuses=None):
        bonuses = bonuses or self.event.getBonuses()
        result = OldStyleBonusesFormatter(self.event).getFormattedBonuses(bonuses)
        return formatters.todict(result) if result else formatters.todict([formatters.packTextBlock(text_styles.alert('#quests:bonuses/notAvailable'))])

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

            if groupBy is None and countOfCumulatives == 1 and cumulatives[None]:
                (current, total), progressType = cumulatives[None][0], formatters.PROGRESS_BAR_TYPE.SIMPLE
            else:
                avgProgressesPerGroup = []
                for groupByKey, values in cumulatives.iteritems():
                    progressesSum = sum([ c / float(t) for c, t in values ])
                    avgProgressesPerGroup.append((groupByKey, int(round(100.0 * progressesSum / len(values))), 100))

                avgProgresses = sorted(avgProgressesPerGroup, key=operator.itemgetter(1), reverse=True)
                if avgProgresses:
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
                        if names:
                            note = makeHtmlString('html_templates:lobby/quests/tooltips/progress', 'note', {'names': ', '.join(names[:self.PROGRESS_TOOLTIP_MAX_ITEMS])})
                        tooltip = {'header': i18n.makeString(QUESTS.TOOLTIP_PROGRESS_GROUPBY_HEADER),
                         'body': makeHtmlString('html_templates:lobby/quests/tooltips/progress', 'body', {'name': name}),
                         'note': note}
            return (current,
             total,
             progressType,
             tooltip)


class _PersonalMissionInfo(_EventInfo):

    def getPostBattleInfo(self, svrEvents, pCur, pPrev, isProgressReset, isCompleted, progressData):
        info = super(_PersonalMissionInfo, self).getPostBattleInfo(svrEvents, pCur, pPrev, isProgressReset, isCompleted, progressData)
        condFormatter = PostBattleConditionsFormatter(self.event, progressData)
        statusState, statusText = self._getStatus(pmComplete=isCompleted)
        info.update({'title': text_styles.highTitle(info.get('title')),
         'linkBtnVisible': statusState == PERSONAL_MISSIONS_ALIASES.POST_BATTLE_STATE_IN_PROGRESS,
         'collapsedToggleBtnVisible': statusState == PERSONAL_MISSIONS_ALIASES.POST_BATTLE_STATE_IN_PROGRESS,
         'descr': condFormatter.getMultiplierDescription(),
         'personalInfo': [condFormatter.getConditionsData(isMain=True), condFormatter.getConditionsData(isMain=False)],
         'questState': {'statusState': statusState,
                        'statusText': statusText},
         'awards': []})
        return info

    def _getStatus(self, pCur=None, pmComplete=None):
        if pmComplete:
            if pmComplete.isAddComplete:
                msg = text_styles.bonusAppliedText(QUESTS.PERSONALMISSION_STATUS_FULLDONE)
                return (PERSONAL_MISSIONS_ALIASES.POST_BATTLE_STATE_FULL_DONE, msg)
            if pmComplete.isMainComplete:
                msg = text_styles.bonusAppliedText(QUESTS.PERSONALMISSION_STATUS_MAINDONE)
                return (PERSONAL_MISSIONS_ALIASES.POST_BATTLE_STATE_DONE, msg)
        msg = text_styles.neutral(QUESTS.PERSONALMISSION_STATUS_INPROGRESS)
        return (PERSONAL_MISSIONS_ALIASES.POST_BATTLE_STATE_IN_PROGRESS, msg)


class _MotiveQuestInfo(_QuestInfo):

    def getPostBattleInfo(self, svrEvents, pCur, pPrev, isProgressReset, isCompleted, progressData):
        motiveQuests = [ q for q in svrEvents.values() if q.getType() == EVENT_TYPE.MOTIVE_QUEST and not q.isCompleted() ]
        info = super(_MotiveQuestInfo, self).getPostBattleInfo(svrEvents, pCur, pPrev, isProgressReset, isCompleted, progressData)
        info.update({'isLinkBtnVisible': len(motiveQuests) > 0})
        return info


class _LinkedSetQuestInfo(_QuestInfo):

    def getInfo(self, svrEvents, pCur=None, pPrev=None, noProgressInfo=False):
        res = super(_LinkedSetQuestInfo, self).getInfo(svrEvents, pCur, pPrev, noProgressInfo)
        missionName = getLocalizedMissionNameForLinkedSetQuest(self.event)
        questName = getLocalizedQuestNameForLinkedSetQuest(self.event)
        res['description'] = _ms(LINKEDSET.QUEST_CARD_TITLE, mission_name=missionName, quest_name=questName)
        return res

    def getPostBattleInfo(self, svrEvents, pCur, pPrev, isProgressReset, isCompleted, progressData):
        bonuses = self.event.getBonuses()
        if not bonuses:
            return None
        else:
            res = super(_LinkedSetQuestInfo, self).getPostBattleInfo(svrEvents, pCur, pPrev, isProgressReset, isCompleted, progressData)
            res['title'] = getLocalizedQuestNameForLinkedSetQuest(self.event)
            progresses = res.get('progressList', [])
            if progresses and len(progresses) == 1:
                curProgress = progresses[0]
                curProgress['description'] = getLocalizedQuestDescForLinkedSetQuest(self.event)
            return res


def _getEventInfoData(event):
    if event.getType() == constants.EVENT_TYPE.PERSONAL_MISSION:
        return _PersonalMissionInfo(event)
    if event.getType() == constants.EVENT_TYPE.MOTIVE_QUEST:
        return _MotiveQuestInfo(event)
    if isLinkedSet(event.getGroupID()):
        return _LinkedSetQuestInfo(event)
    return _QuestInfo(event) if event.getType() in constants.EVENT_TYPE.QUEST_RANGE else _EventInfo(event)


def getEventPostBattleInfo(event, svrEvents=None, pCur=None, pPrev=None, isProgressReset=False, isCompleted=False, progressData=None):
    return _getEventInfoData(event).getPostBattleInfo(svrEvents, pCur or {}, pPrev or {}, isProgressReset, isCompleted, progressData)


def getNationsForChain(operation, chainID):
    return ALLIANCE_TO_NATIONS[operation.getChainClassifier(chainID).classificationAttr]


def getChainVehRequirements(operation, chainID, useIcons=False):
    vehs, minLevel, maxLevel = getChainVehTypeAndLevelRestrictions(operation, chainID)
    if useIcons and operation.getBranch() == PM_BRANCH.PERSONAL_MISSION_2:
        nations = getNationsForChain(operation, chainID)
        vehsData = []
        for nation in GUI_NATIONS:
            if nation in nations:
                vehsData.append(icons.makeImageTag(getNationsFilterAssetPath(nation), 26, 16, -4))

        vehs = ' '.join(vehsData)
    return _ms(PERSONAL_MISSIONS.OPERATIONINFO_CHAINVEHREQ, vehs=vehs, minLevel=minLevel, maxLevel=maxLevel)


def getChainVehTypeAndLevelRestrictions(operation, chainID):
    _eventsCache = dependency.instance(IEventsCache)
    pmCache = _eventsCache.getPersonalMissions()
    minLevel, maxLevel = pmCache.getVehicleLevelRestrictions(operation.getID())
    vehType = _ms(QUESTS.getAddBottomVehType(operation.getChainClassifier(chainID).classificationAttr))
    if operation.getBranch() == PM_BRANCH.PERSONAL_MISSION_2:
        nations = getNationsForChain(operation, chainID)
        nationsText = []
        for nation in GUI_NATIONS:
            if nation in nations:
                nationsText.append(getNationText(nation))

        vehType = _ms(vehType, nations=', '.join(nationsText))
    return (vehType, int2roman(minLevel), int2roman(maxLevel))


_questBranchToTabMap = {PM_BRANCH.REGULAR: QUESTS_ALIASES.SEASON_VIEW_TAB_RANDOM}
