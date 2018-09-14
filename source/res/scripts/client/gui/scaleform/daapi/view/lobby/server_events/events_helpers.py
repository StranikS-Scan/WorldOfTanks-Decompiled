# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/events_helpers.py
import random
import time
import operator
from collections import defaultdict
import BigWorld
import constants
from gui.Scaleform.framework import AppRef
from helpers import i18n, int2roman, time_utils
from dossiers2.custom.records import RECORD_DB_IDS
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK
from gui import makeHtmlString
from gui.shared import g_itemsCache, utils
from gui.server_events import formatters, conditions, settings as quest_settings
from gui.server_events.modifiers import ACTION_MODIFIER_TYPE
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.framework.managers.TextManager import TextType
from quest_xml_source import MAX_BONUS_LIMIT
FINISH_TIME_LEFT_TO_SHOW = time_utils.ONE_DAY
START_TIME_LIMIT = 5 * time_utils.ONE_DAY

class _EventInfo(AppRef):

    class EVENT_STATUS(utils.CONST_CONTAINER):
        COMPLETED = 'done'
        NOT_AVAILABLE = 'notAvailable'
        NONE = ''

    NO_BONUS_COUNT = -1

    def __init__(self, event):
        self.event = event

    def getInfo(self, svrEvents, pCur = None, pPrev = None, noProgressInfo = False):
        if noProgressInfo:
            status, statusMsg = self.EVENT_STATUS.NONE, self._getStatus()[1]
            bonusCount = self.NO_BONUS_COUNT
            qProgCur, qProgTot, qProgbarType, tooltip = (0,
             0,
             formatters.PROGRESS_BAR_TYPE.NONE,
             None)
        else:
            bonusCount = self._getBonusCount(pCur)
            status, statusMsg = self._getStatus(pCur)
            qProgCur, qProgTot, qProgbarType, tooltip = self._getProgressValues(svrEvents, pCur, pPrev)
        return {'questID': str(self.event.getID()),
         'isNew': quest_settings.isNewCommonEvent(self.event),
         'eventType': self.event.getType(),
         'status': status,
         'IGR': self.event.isIGR(),
         'taskType': self.event.getUserType(),
         'description': self.event.getUserName(),
         'timerDescr': self._getTimerMsg(),
         'tasksCount': bonusCount,
         'progrBarType': qProgbarType,
         'progrTooltip': tooltip,
         'maxProgrVal': qProgTot,
         'currentProgrVal': qProgCur,
         'isLock': False,
         'isLocked': False}

    def getDetails(self, svrEvents):
        eProgCur, eProgTot, eProgbarType, tooltip = self._getProgressValues(svrEvents)
        status, statusMsg = self._getStatus()
        requirements = self._getRequirements(svrEvents)
        condsDescription = self._getConditionsDescription()
        topConditions = self._getTopConditions(svrEvents)
        conds = self._getConditions(svrEvents)
        hasConditions = bool(len(condsDescription) or len(topConditions) or len(conds) > 0)
        return {'header': {'title': self.event.getUserName(),
                    'date': self._getActiveDateTimeString(),
                    'status': status,
                    'statusDescription': statusMsg,
                    'progrBarType': eProgbarType,
                    'eventType': self.event.getType(),
                    'progrTooltip': tooltip,
                    'maxProgrVal': eProgTot,
                    'currentProgrVal': eProgCur,
                    'tasksCount': self._getBonusCount(),
                    'hasConditions': hasConditions,
                    'hasRequirements': len(requirements) > 0},
         'award': self._getBonuses(svrEvents),
         'requirements': {'title': '',
                          'description': '',
                          'containerElements': requirements},
         'conditions': {'title': self._getConditionsTitle(),
                        'description': condsDescription,
                        'topConditions': topConditions,
                        'containerElements': conds}}

    def getPostBattleInfo(self, svrEvents, pCur, pPrev, isProgressReset, isCompleted):
        index = 0
        progresses = []
        if not isProgressReset and not isCompleted:
            for cond in self.event.bonusCond.getConditions().items:
                if isinstance(cond, conditions._Cumulativable):
                    for groupByKey, (curProg, totalProg, diff, _) in cond.getProgressPerGroup(pCur, pPrev).iteritems():
                        label = cond.getUserString()
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
            awards = self._getBonuses(svrEvents)
        return {'title': self.event.getUserName(),
         'awards': awards,
         'progressList': progresses,
         'alertMsg': alertMsg,
         'questInfo': self.getInfo(svrEvents, pCur, pPrev),
         'personalInfo': [],
         'questType': self.event.getType()}

    @classmethod
    def _getTillTimeString(cls, timeValue):
        if START_TIME_LIMIT >= timeValue > time_utils.ONE_DAY:
            fmt = i18n.makeString(QUESTS.ITEM_TIMER_TILLSTART_DAYS)
        elif time_utils.ONE_DAY >= timeValue > time_utils.ONE_HOUR:
            fmt = i18n.makeString(QUESTS.ITEM_TIMER_TILLSTART_HOURS)
        else:
            fmt = i18n.makeString(QUESTS.ITEM_TIMER_TILLSTART_MIN)
        gmtime = time.gmtime(timeValue)
        return fmt % {'hours': time.strftime('%H', gmtime),
         'min': time.strftime('%M', gmtime),
         'days': str(gmtime.tm_mday)}

    @classmethod
    def _getDateTimeString(cls, timeValue):
        return '{0:>s} {1:>s}'.format(BigWorld.wg_getLongDateFormat(timeValue), BigWorld.wg_getShortTimeFormat(timeValue))

    @classmethod
    def _getDailyProgressResetTimeOffset(cls):
        regionalSettings = BigWorld.player().serverSettings['regional_settings']
        if 'starting_time_of_a_new_game_day' in regionalSettings:
            newDayOffset = regionalSettings['starting_time_of_a_new_game_day']
        elif 'starting_time_of_a_new_day' in regionalSettings:
            newDayOffset = regionalSettings['starting_time_of_a_new_day']
        else:
            newDayOffset = 0
        return newDayOffset

    @classmethod
    def _getEventsByIDs(cls, ids, svrEvents):
        result = {}
        for eID in ids:
            if eID in svrEvents:
                result[eID] = svrEvents[eID]

        return result

    def _getStatus(self, pCur = None):
        return (self.EVENT_STATUS.NONE, '')

    def _getBonusCount(self, pCur = None):
        return self.NO_BONUS_COUNT

    def _getProgressValues(self, svrEvents = None, pCur = None, pPrev = None):
        return (0,
         0,
         formatters.PROGRESS_BAR_TYPE.NONE,
         None)

    def _getBonuses(self, svrEvents, bonuses = None):
        bonuses = bonuses or self.event.getBonuses()
        result = []
        for b in bonuses:
            if b.isShowInGUI():
                result.append(b.format())

        if len(result):
            return formatters.todict([formatters.packTextBlock(', '.join(result))])
        return []

    def _getRequirements(self, svrEvents):
        return []

    def _getConditionsTitle(self):
        return i18n.makeString('#quests:details/conditions/label')

    def _getConditionsDescription(self):
        return ''

    def _getTopConditions(self, svrEvents):
        return []

    def _getConditions(self, svrEvents):
        return []

    def _getTimerMsg(self):
        startTimeLeft = self.event.getStartTimeLeft()
        if startTimeLeft > 0:
            if startTimeLeft > START_TIME_LIMIT:
                fmt = self._getDateTimeString(self.event.getStartTime())
            else:
                fmt = self._getTillTimeString(startTimeLeft)
            return makeHtmlString('html_templates:lobby/quests', 'timerTillStart', {'time': fmt})
        if FINISH_TIME_LEFT_TO_SHOW > self.event.getFinishTimeLeft() > 0:
            gmtime = time.gmtime(self.event.getFinishTimeLeft())
            if gmtime.tm_hour > 0:
                fmt = i18n.makeString('#quests:item/timer/tillFinish/onlyHours')
            else:
                fmt = i18n.makeString('#quests:item/timer/tillFinish/lessThanHour')
            fmt %= {'hours': time.strftime('%H', gmtime),
             'min': time.strftime('%M', gmtime),
             'days': str(gmtime.tm_mday)}
            return makeHtmlString('html_templates:lobby/quests', 'timerTillFinish', {'time': fmt})
        return ''

    def _getActiveDateTimeString(self):
        i18nKey, args = None, {}
        if self.event.getFinishTimeLeft() <= time_utils.ONE_DAY:
            gmtime = time.gmtime(self.event.getFinishTimeLeft())
            if gmtime.tm_hour > 0:
                fmt = i18n.makeString(QUESTS.ITEM_TIMER_TILLFINISH_LONGFULLFORMAT)
            else:
                fmt = i18n.makeString(QUESTS.ITEM_TIMER_TILLFINISH_SHORTFULLFORMAT)
            fmt %= {'hours': time.strftime('%H', gmtime)}
            return fmt
        else:
            if self.event.getStartTimeLeft() > 0:
                i18nKey = '#quests:details/header/activeDuration'
                args = {'startTime': self._getDateTimeString(self.event.getStartTime()),
                 'finishTime': self._getDateTimeString(self.event.getFinishTime())}
            elif self.event.getFinishTimeLeft() <= time_utils.HALF_YEAR:
                i18nKey = '#quests:details/header/tillDate'
                args = {'finishTime': self._getDateTimeString(self.event.getFinishTime())}
            weekDays = self.event.getWeekDays()
            intervals = self.event.getActiveTimeIntervals()
            if len(weekDays) or len(intervals):
                if i18nKey is None:
                    i18nKey = '#quests:details/header/schedule'
                if len(weekDays):
                    days = ', '.join([ i18n.makeString('#menu:dateTime/weekDays/full/%d' % idx) for idx in self.event.getWeekDays() ])
                    i18nKey += 'Days'
                    args['days'] = days
                if len(intervals):
                    times = []
                    for low, high in intervals:
                        times.append('%s - %s' % (BigWorld.wg_getShortTimeFormat(low), BigWorld.wg_getShortTimeFormat(high)))

                    i18nKey += 'Times'
                    times = ', '.join(times)
                    args['times'] = times
            return i18n.makeString(i18nKey, **args)


class _QuestInfo(_EventInfo):
    PROGRESS_TOOLTIP_MAX_ITEMS = 4
    SIMPLE_BONUSES_MAX_ITEMS = 5

    def _getBonuses(self, svrEvents, bonuses = None):
        bonuses = bonuses or self.event.getBonuses()
        result, simpleBonusesList, customizationsList = [], [], []
        for b in bonuses:
            if b.isShowInGUI():
                if b.getName() == 'dossier':
                    for record in b.getRecords():
                        if record[0] != ACHIEVEMENT_BLOCK.RARE:
                            result.append(formatters.packAchieveElement(RECORD_DB_IDS[record]))

                elif b.getName() == 'customizations':
                    customizationsList.extend(b.getList())
                else:
                    flist = b.formattedList()
                    if flist:
                        simpleBonusesList.extend(flist)

        label = ', '.join(simpleBonusesList)
        fullLabel = None
        if len(simpleBonusesList) > self.SIMPLE_BONUSES_MAX_ITEMS:
            label = ', '.join(simpleBonusesList[:self.SIMPLE_BONUSES_MAX_ITEMS]) + '..'
            fullLabel = ', '.join(simpleBonusesList)
        result.append(formatters.packTextBlock(label, fullLabel=fullLabel))
        if len(customizationsList):
            result.append(formatters.packCustomizations(customizationsList))
        parents = [ qID for _, qIDs in self.event.getParents().iteritems() for qID in qIDs ]
        for qID, q in self._getEventsByIDs(parents, svrEvents or {}).iteritems():
            result.append(formatters.packTextBlock(i18n.makeString('#quests:bonuses/item/task', q.getUserName()), questID=qID))

        if len(result):
            return formatters.todict(result)
        else:
            return []

    def _getBonusCount(self, pCur = None):
        if not self.event.isCompleted(progress=pCur):
            bonusLimit = self.event.bonusCond.getBonusLimit()
            if bonusLimit is None or bonusLimit > 1 or self.event.bonusCond.getGroupByValue() is not None:
                return self.event.getBonusCount(progress=pCur)
        return self.NO_BONUS_COUNT

    def _getStatus(self, pCur = None):
        if self.event.isCompleted(progress=pCur):
            if self.event.bonusCond.isDaily():
                msg = i18n.makeString('#quests:details/status/completed/daily', time=self._getTillTimeString(time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay()))
            else:
                msg = i18n.makeString('#quests:details/status/completed')
            return (self.EVENT_STATUS.COMPLETED, msg)
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
                return (self.EVENT_STATUS.NOT_AVAILABLE, msg)
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
            return (self.EVENT_STATUS.NONE, msg)

    def _getProgressValues(self, svrEvents = None, pCur = None, pPrev = None):
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
                            name = g_itemsCache.items.getItemByCD(groupByKey).shortUserName
                            names = [ g_itemsCache.items.getItemByCD(intCD).shortUserName for intCD, _, __ in nearestProgs ]
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

    def _getRequirements(self, svrEvents):
        result = []
        accReqsFmt = self.event.accountReqs.format(svrEvents, self.event)
        if accReqsFmt is not None:
            result.append(formatters.todict(accReqsFmt))
        vehReqsFmt = self.event.vehicleReqs.format(svrEvents, self.event)
        if vehReqsFmt is not None:
            result.append(formatters.todict(vehReqsFmt))
        return result

    def _getTopConditions(self, svrEvents):
        result = []
        preBattleFmt = self.event.preBattleCond.format(svrEvents, self.event)
        if preBattleFmt is not None:
            result.extend(preBattleFmt)
        descr = self.event.getDescription()
        if descr:
            result.append(formatters.packTextBlock(formatters.formatGray(descr)))
        return formatters.todict(result)

    def _getConditions(self, svrEvents):
        subBlocks = []
        bonus = self.event.bonusCond
        battlesLeft, battlesCount, inrow = None, None, False
        battles = bonus.getConditions().find('battles')
        if battles is not None:
            battlesCount = battles._getTotalValue()
            if not self.event.isCompleted() and bonus.getGroupByValue() is None:
                progress = battles.getProgressPerGroup()
                if None in progress:
                    curProg, totalProg, _, _ = progress[None]
                    battlesLeft = totalProg - curProg
        bonusFmtConds = bonus.format(svrEvents, event=self.event)
        if len(bonusFmtConds):
            subBlocks.extend(formatters.indexing(bonusFmtConds))
        postBattleFmtConds = self.event.postBattleCond.format(svrEvents, event=self.event)
        if len(postBattleFmtConds):
            if len(bonusFmtConds):
                subBlocks.append(formatters.packSeparator(label=i18n.makeString('#quests:details/conditions/postBattle/separator')))
            subBlocks.extend(formatters.indexing(postBattleFmtConds))
        if bonus.isDaily():
            resetHourOffset = (time_utils.ONE_DAY - self._getDailyProgressResetTimeOffset()) / 3600
            if resetHourOffset >= 0:
                subBlocks.append(formatters.packTextBlock(label=formatters.formatYellow('#quests:details/conditions/postBattle/dailyReset') % {'time': time.strftime(i18n.makeString('#quests:details/conditions/postBattle/dailyReset/timeFmt'), time_utils.getTimeStructInLocal(time_utils.getTimeTodayForUTC(hour=resetHourOffset)))}))
        result = []
        if len(subBlocks) or battlesCount:
            if not self.event.isGuiDisabled():
                result.append(formatters.packConditionsBlock(battlesCount, battlesLeft, bonus.isInRow(), conditions=subBlocks))
            else:
                result.append(formatters.packConditionsBlock(conditions=subBlocks))
        if bonus.getGroupByValue() is not None and not self.event.isGuiDisabled():
            progressesFmt = bonus.formatGroupByProgresses(svrEvents, self.event)
            if len(progressesFmt):
                result.append(formatters.packTopLevelContainer(i18n.makeString('#quests:details/conditions/groupBy/%s' % bonus.getGroupByValue()), subBlocks=progressesFmt, isResizable=len(progressesFmt) > 5))
        return formatters.todict(result)


class _ActionInfo(_EventInfo):

    @classmethod
    def _getDateTimeString(cls, timeValue):
        return '{0:>s}'.format(BigWorld.wg_getLongDateFormat(timeValue))

    def _getConditionsTitle(self):
        return None

    def _getConditionsDescription(self):
        descr = self.event.getDescription()
        if descr:
            return formatters.formatBright(descr)
        return ''

    def _getConditions(self, svrEvents):
        modifiers = defaultdict(list)
        for m in self.event.getModifiers():
            fmtData = m.format(self.event)
            if fmtData is not None:
                modifiers[m.getType()].extend(fmtData)

        result = []
        if len(modifiers[ACTION_MODIFIER_TYPE.DISCOUNT]):
            result.append(formatters.packTopLevelContainer(i18n.makeString(QUESTS.DETAILS_MODIFIERS_TITLE_DISCOUNT), subBlocks=modifiers[ACTION_MODIFIER_TYPE.DISCOUNT]))
        if len(modifiers[ACTION_MODIFIER_TYPE.RENT]):
            result.append(formatters.packTopLevelContainer(i18n.makeString(QUESTS.DETAILS_MODIFIERS_TITLE_DISCOUNT), subBlocks=modifiers[ACTION_MODIFIER_TYPE.RENT]))
        for fmtData in modifiers[ACTION_MODIFIER_TYPE.SELLING]:
            result.append(fmtData)

        return formatters.todict(result)

    def _getActiveDateTimeString(self):
        if self.event.getFinishTimeLeft() <= time_utils.QUARTER_HOUR:
            return formatters.formatYellow(QUESTS.DETAILS_HEADER_COMETOEND)
        return super(_ActionInfo, self)._getActiveDateTimeString()

    def _getTimerMsg(self):
        if self.event.getFinishTimeLeft() <= time_utils.QUARTER_HOUR:
            return makeHtmlString('html_templates:lobby/quests', 'comeToEnd')
        return super(_ActionInfo, self)._getTimerMsg()


class _PotapovQuestInfo(_QuestInfo):

    def _getBonuses(self, svrEvents, _ = None):
        from gui.server_events.bonuses import FakeTextBonus
        mainBonuses = self.event.getBonuses(isMain=True)
        addBonuses = self.event.getBonuses(isMain=False)

        def _getBonuses(bonuses):
            return _QuestInfo._getBonuses(self, None, bonuses=bonuses)

        return _getBonuses(mainBonuses) + _getBonuses([FakeTextBonus(i18n.makeString('#quests:bonuses/item/additionBonus'))]) + _getBonuses(addBonuses)

    def getPostBattleInfo(self, svrEvents, pCur, pPrev, isProgressReset, isCompleted):
        _getText = self.app.utilsManager.textManager.getText

        def _packCondition(titleKey, text):
            return '%s\n%s' % (_getText(TextType.MIDDLE_TITLE, i18n.makeString(titleKey)), _getText(TextType.MAIN_TEXT, text))

        def _packStatus(completed):
            if completed:
                return 'done'
            return 'notDone'

        return {'title': self.event.getUserName(),
         'questInfo': self.getInfo(svrEvents),
         'awards': None,
         'progressList': [],
         'alertMsg': '',
         'personalInfo': [{'statusStr': _packStatus(isCompleted[0]),
                           'text': _packCondition(QUESTS.QUESTTASKDETAILSVIEW_MAINCONDITIONS, self.event.getUserMainCondition())}, {'statusStr': _packStatus(isCompleted[1]),
                           'text': _packCondition(QUESTS.QUESTTASKDETAILSVIEW_ADDITIONALCONDITIONS, self.event.getUserAddCondition())}],
         'questType': self.event.getType()}


def getEventInfoData(event):
    if event.getType() == constants.EVENT_TYPE.POTAPOV_QUEST:
        return _PotapovQuestInfo(event)
    if event.getType() in constants.EVENT_TYPE.QUEST_RANGE:
        return _QuestInfo(event)
    if event.getType() == constants.EVENT_TYPE.ACTION:
        return _ActionInfo(event)
    return _EventInfo(event)


def getEventInfo(event, svrEvents = None, noProgressInfo = False):
    return getEventInfoData(event).getInfo(svrEvents, noProgressInfo=noProgressInfo)


def getEventDetails(event, svrEvents = None):
    return getEventInfoData(event).getDetails(svrEvents)


def getEventPostBattleInfo(event, svrEvents = None, pCur = None, pPrev = None, isProgressReset = False, isCompleted = False):
    return getEventInfoData(event).getPostBattleInfo(svrEvents, pCur or {}, pPrev or {}, isProgressReset, isCompleted)
