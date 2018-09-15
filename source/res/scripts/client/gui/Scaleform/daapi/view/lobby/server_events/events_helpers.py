# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/events_helpers.py
import operator
from collections import defaultdict
import BigWorld
import constants
from constants import EVENT_TYPE
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.server_events.awards_formatters import OldStyleBonusesFormatter
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events import formatters, conditions, settings as quest_settings
from gui.server_events.events_helpers import EventInfoModel, MISSIONS_STATES, QuestInfoModel
from gui.shared.formatters import text_styles
from helpers import i18n, int2roman, time_utils, dependency
from personal_missions import PM_BRANCH
from quest_xml_source import MAX_BONUS_LIMIT
from skeletons.gui.shared import IItemsCache
_AWARDS_PER_PAGE = 3
FINISH_TIME_LEFT_TO_SHOW = time_utils.ONE_DAY
START_TIME_LIMIT = 5 * time_utils.ONE_DAY

class _EventInfo(EventInfoModel):

    def getInfo(self, svrEvents, pCur=None, pPrev=None, noProgressInfo=False):
        if noProgressInfo:
            status, statusMsg = MISSIONS_STATES.NONE, self._getStatus()[1]
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
                         'progressDiff': '+ %s' % BigWorld.wg_getIntegralFormat(diff)})

            if not progresses:
                return
        alertMsg = ''
        if isProgressReset:
            alertMsg = i18n.makeString('#quests:postBattle/progressReset')
        diffStr, awards = ('', None)
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
        parents = [ qID for _, qIDs in self.event.getParents().iteritems() for qID in qIDs ]
        for qID, q in self._getEventsByIDs(parents, svrEvents or {}).iteritems():
            result.append(formatters.packTextBlock(i18n.makeString('#quests:bonuses/item/task', q.getUserName()), questID=qID))

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
                    progressesSum = sum(map(lambda (c, t): c / float(t), values))
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


class _PersonalMissionInfo(_QuestInfo):

    def _getBonuses(self, svrEvents, _=None):
        mainBonuses = self.event.getBonuses(isMain=True)
        addBonuses = self.event.getBonuses(isMain=False)
        return (_QuestInfo._getBonuses(self, None, bonuses=mainBonuses), _QuestInfo._getBonuses(self, None, bonuses=addBonuses))

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
                           'text': _packCondition(PERSONAL_MISSIONS.TASKDETAILSVIEW_MAINCONDITIONS, self.event.getUserMainCondition())}, {'statusStr': _packStatus(isCompleted[1]),
                           'text': _packCondition(PERSONAL_MISSIONS.TASKDETAILSVIEW_ADDITIONALCONDITIONS, self.event.getUserAddCondition())}],
         'questType': self.event.getType()}


class _MotiveQuestInfo(_QuestInfo):

    def getPostBattleInfo(self, svrEvents, pCur, pPrev, isProgressReset, isCompleted):
        motiveQuests = filter(lambda q: q.getType() == EVENT_TYPE.MOTIVE_QUEST and not q.isCompleted(), svrEvents.values())
        info = super(_MotiveQuestInfo, self).getPostBattleInfo(svrEvents, pCur, pPrev, isProgressReset, isCompleted)
        info.update({'isLinkBtnVisible': len(motiveQuests) > 0})
        return info


def getEventInfoData(event):
    if event.getType() == constants.EVENT_TYPE.PERSONAL_MISSION:
        return _PersonalMissionInfo(event)
    if event.getType() == constants.EVENT_TYPE.MOTIVE_QUEST:
        return _MotiveQuestInfo(event)
    return _QuestInfo(event) if event.getType() in constants.EVENT_TYPE.QUEST_RANGE else _EventInfo(event)


def getEventPostBattleInfo(event, svrEvents=None, pCur=None, pPrev=None, isProgressReset=False, isCompleted=False):
    return getEventInfoData(event).getPostBattleInfo(svrEvents, pCur or {}, pPrev or {}, isProgressReset, isCompleted)


_questBranchToTabMap = {PM_BRANCH.REGULAR: QUESTS_ALIASES.SEASON_VIEW_TAB_RANDOM,
 PM_BRANCH.FALLOUT: QUESTS_ALIASES.SEASON_VIEW_TAB_FALLOUT}
