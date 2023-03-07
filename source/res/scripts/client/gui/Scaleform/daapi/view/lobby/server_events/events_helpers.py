# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/events_helpers.py
import operator
from collections import defaultdict
import typing
from gui.Scaleform.daapi.view.lobby.customization.progression_helpers import getC11n2dProgressionLinkBtnParams
from gui.shared.gui_items import GUI_ITEM_TYPE
import constants
from battle_pass_common import BattlePassConsts
from constants import EVENT_TYPE
from gui.server_events.events_constants import BATTLE_MATTERS_QUEST_ID
from gui import GUI_NATIONS, makeHtmlString
from gui.Scaleform import getNationsFilterAssetPath
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import getNationText
from gui.Scaleform.daapi.view.lobby.server_events.awards_formatters import OldStyleBonusesFormatter
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events import conditions, formatters, settings as quest_settings
from gui.server_events.events_helpers import EventInfoModel, MISSIONS_STATES, QuestInfoModel, isDailyQuest, getDataByC11nQuest
from gui.server_events.personal_progress.formatters import PostBattleConditionsFormatter
from gui.shared.formatters import icons, text_styles
from helpers import dependency, i18n, int2roman, time_utils
from helpers.i18n import makeString as _ms
from nations import ALLIANCE_TO_NATIONS
from personal_missions import PM_BRANCH
from quest_xml_source import MAX_BONUS_LIMIT
from shared_utils import first
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Iterable, Union
    from gui.server_events.bonuses import BattlePassStyleProgressTokenBonus, TokensBonus
    from gui.server_events.event_items import Quest
FINISH_TIME_LEFT_TO_SHOW = time_utils.ONE_DAY
START_TIME_LIMIT = 5 * time_utils.ONE_DAY
_AWARDS_PER_PAGE = 3

class BattlePassProgress(object):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __BATTLE_PASS_POINTS = 'battlePassPoints'

    def __init__(self, arenaBonusType, *args, **kwargs):
        self.__arenaBonusType = arenaBonusType
        self.__chapterID = kwargs.get('bpChapter', 0)
        self.__topPoints = kwargs.get('bpTopPoints', 0)
        self.__pointsAux = kwargs.get('bpNonChapterPointsDiff', 0)
        self.__pointsTotal = kwargs.get('sumPoints', 0)
        self.__hasBattlePass = kwargs.get('hasBattlePass', False)
        self.__questsProgress = kwargs.get('questsProgress', {})
        self.__battlePassComplete = kwargs.get('battlePassComplete', False)
        self.__availablePoints = kwargs.get('availablePoints', False)
        self.__questPoints = kwargs.get('eventBattlePassPoints', 0)
        self.__bonusCapPoints = kwargs.get('bpBonusPoints', 0)
        self.__prevLevel = 0
        self.__currLevel = 0
        self.__pointsNew = 0
        self.__pointsMax = 0
        self.__initExtendedData()

    @property
    def chapterID(self):
        return self.__chapterID

    @property
    def bpTopPoints(self):
        return self.__topPoints

    @property
    def isApplied(self):
        return self.__battlePassController.isGameModeEnabled(self.__arenaBonusType)

    @property
    def hasProgress(self):
        return self.isLevelReached or self.pointsAdd > 0

    @property
    def isDone(self):
        return self.isLevelReached or self.isLevelMax

    @property
    def isLevelReached(self):
        return self.__currLevel > self.__prevLevel

    @property
    def isLevelMax(self):
        return self.__chapterID > 0 and self.__currLevel == self.__battlePassController.getMaxLevelInChapter(self.__chapterID)

    @property
    def hasBattlePass(self):
        return self.__hasBattlePass

    @property
    def battlePassComplete(self):
        return self.__battlePassComplete

    @property
    def availablePoints(self):
        return self.__availablePoints

    @property
    def level(self):
        return self.__prevLevel + 1

    @property
    def currentLevel(self):
        return self.__currLevel

    @property
    def prevLevel(self):
        return self.__prevLevel

    @property
    def currLevel(self):
        return self.__currLevel

    @property
    def pointsAdd(self):
        totalPoints = self.__topPoints + self.__bonusCapPoints + self.__questPoints
        return self.__pointsAux or (totalPoints if self.__currLevel == self.__prevLevel else self.__pointsNew)

    @property
    def pointsAux(self):
        return self.__pointsAux

    @property
    def pointsNew(self):
        return self.__pointsNew

    @property
    def pointsMax(self):
        return self.__pointsMax

    @property
    def questPoints(self):
        return self.__questPoints

    @property
    def bonusCapPoints(self):
        return self.__bonusCapPoints

    @property
    def pointsTotal(self):
        return self.__pointsTotal

    @property
    def awards(self):
        return self.__battlePassController.getSingleAward(self.chapterID, self.level, self.__getRewardType()) if self.isLevelReached else []

    def getLevelAwards(self, level):
        return self.__battlePassController.getSingleAward(self.chapterID, level, self.__getRewardType())

    def __initExtendedData(self):
        if not self.__battlePassController.isEnabled() or self.__chapterID == 0:
            return
        prevPoints = self.__pointsTotal - self.__topPoints - self.__questPoints - self.__bonusCapPoints + self.__pointsAux
        self.__prevLevel = self.__battlePassController.getLevelByPoints(self.__chapterID, prevPoints)
        self.__currLevel = self.__battlePassController.getLevelByPoints(self.__chapterID, self.__pointsTotal)
        self.__pointsNew, self.__pointsMax = self.__battlePassController.getProgressionByPoints(self.__chapterID, self.__pointsTotal, self.__currLevel)

    def __getRewardType(self):
        return BattlePassConsts.REWARD_BOTH if self.__hasBattlePass else BattlePassConsts.REWARD_FREE

    @staticmethod
    def __isQuestCompleted(_, previousProgress, currentProgress):
        return currentProgress.get('bonusCount', 0) - previousProgress.get('bonusCount', 0) > 0


class EventPostBattleInfo(EventInfoModel):

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
         'isAvailable': isAvailable,
         'linkTooltip': TOOLTIPS.QUESTS_LINKBTN_TASK}

    def getPostBattleInfo(self, svrEvents, pCur, pPrev, isProgressReset, isCompleted, progressData):
        progresses = []
        if not isProgressReset and not isCompleted:
            progresses = self._getProgresses(pCur, pPrev)
            if not progresses:
                return None
        alertMsg = ''
        if isProgressReset:
            alertMsg = i18n.makeString('#quests:postBattle/progressReset')
        _, awards = ('', None)
        if not isProgressReset and isCompleted:
            awards = self._getBonuses(svrEvents, pCur=pCur)
        return {'title': self.event.getUserName(),
         'descr': self.event.getDescription(),
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

    def _getBonuses(self, svrEvents, pCur=None, bonuses=None):
        return []

    def _getProgresses(self, pCur, pPrev):
        index = 0
        progresses = []
        isQuestDailyQuest = isDailyQuest(str(self.event.getID()))
        for cond in self.event.bonusCond.getConditions().items:
            if isinstance(cond, conditions._Cumulativable):
                for _, (curProg, totalProg, diff, _) in cond.getProgressPerGroup(pCur, pPrev).iteritems():
                    if not isQuestDailyQuest:
                        label = cond.getUserString()
                    else:
                        label = cond.getCustomDescription()
                    if not diff or not label:
                        continue
                    index += 1
                    progresses.append({'progrTooltip': None,
                     'progrBarType': formatters.PROGRESS_BAR_TYPE.SIMPLE,
                     'maxProgrVal': totalProg,
                     'currentProgrVal': curProg,
                     'description': '%d. %s' % (index, label),
                     'progressDiff': '+ %s' % backport.getIntegralFormat(diff),
                     'progressDiffTooltip': TOOLTIPS.QUESTS_PROGRESS_EARNEDINBATTLE})

        return progresses


class QuestPostBattleInfo(EventPostBattleInfo, QuestInfoModel):
    PROGRESS_TOOLTIP_MAX_ITEMS = 4
    itemsCache = dependency.descriptor(IItemsCache)

    def _getStatus(self, pCur=None):
        if self.event.isCompleted(progress=pCur):
            if self.event.bonusCond.isDaily():
                msg = self._getCompleteDailyStatus(self._getCompleteKey())
            elif self.event.bonusCond.isWeekly():
                msg = self._getCompleteWeeklyStatus(self._getCompleteWeeklyKey())
            else:
                msg = backport.text(R.strings.quests.details.status.completed())
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

    def _getBonuses(self, svrEvents, pCur=None, bonuses=None):
        bonuses = bonuses or self.event.getBonuses()
        result = OldStyleBonusesFormatter(self.event).getFormattedBonuses(bonuses)
        if result:
            return [ award.getDict() for award in result ]
        return [formatters.packTextBlock(text_styles.alert(backport.text(R.strings.quests.bonuses.notAvailable()))).getDict()]

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


class PersonalMissionPostBattleInfo(EventPostBattleInfo):

    def getPostBattleInfo(self, svrEvents, pCur, pPrev, isProgressReset, isCompleted, progressData):
        info = super(PersonalMissionPostBattleInfo, self).getPostBattleInfo(svrEvents, pCur, pPrev, isProgressReset, isCompleted, progressData)
        condFormatter = PostBattleConditionsFormatter(self.event, progressData)
        if isCompleted.isMainComplete or isCompleted.isAddComplete:
            failedDescr = ''
        else:
            failedDescr = condFormatter.getFailedDescription()
        statusState, statusText = self._getStatus(pmComplete=isCompleted, failed=failedDescr)
        descr = failedDescr or condFormatter.getMultiplierDescription()
        info.update({'title': text_styles.highTitle(info.get('title')),
         'linkBtnVisible': statusState == PERSONAL_MISSIONS_ALIASES.POST_BATTLE_STATE_IN_PROGRESS,
         'collapsedToggleBtnVisible': statusState == PERSONAL_MISSIONS_ALIASES.POST_BATTLE_STATE_IN_PROGRESS,
         'descr': descr,
         'personalInfo': [condFormatter.getConditionsData(isMain=True), condFormatter.getConditionsData(isMain=False)],
         'questState': {'statusState': statusState,
                        'statusText': statusText},
         'awards': []})
        return info

    def _getStatus(self, pCur=None, pmComplete=None, failed=None):
        if pmComplete:
            if pmComplete.isAddComplete:
                msg = text_styles.bonusAppliedText(QUESTS.PERSONALMISSION_STATUS_FULLDONE)
                return (PERSONAL_MISSIONS_ALIASES.POST_BATTLE_STATE_FULL_DONE, msg)
            if pmComplete.isMainComplete:
                msg = text_styles.bonusAppliedText(QUESTS.PERSONALMISSION_STATUS_MAINDONE)
                return (PERSONAL_MISSIONS_ALIASES.POST_BATTLE_STATE_DONE, msg)
        if failed:
            msg = text_styles.error(QUESTS.PERSONALMISSION_STATUS_FAILED)
            return (PERSONAL_MISSIONS_ALIASES.POST_BATTLE_STATE_FAILED, msg)
        msg = text_styles.neutral(QUESTS.PERSONALMISSION_STATUS_INPROGRESS)
        return (PERSONAL_MISSIONS_ALIASES.POST_BATTLE_STATE_IN_PROGRESS, msg)


class MotiveQuestPostBattleInfo(QuestPostBattleInfo):

    def getPostBattleInfo(self, svrEvents, pCur, pPrev, isProgressReset, isCompleted, progressData):
        motiveQuests = [ q for q in svrEvents.values() if q.getType() == EVENT_TYPE.MOTIVE_QUEST and not q.isCompleted() ]
        info = super(MotiveQuestPostBattleInfo, self).getPostBattleInfo(svrEvents, pCur, pPrev, isProgressReset, isCompleted, progressData)
        info.update({'isLinkBtnVisible': len(motiveQuests) > 0})
        return info


class _BattleMattersQuestInfo(QuestPostBattleInfo):

    def getInfo(self, svrEvents, pCur=None, pPrev=None, noProgressInfo=False):
        battleResults = R.strings.battle_matters.battleResults
        result = super(_BattleMattersQuestInfo, self).getInfo(svrEvents, pCur, pPrev, noProgressInfo)
        result['description'] = backport.text(battleResults.descr()).format(questID=self.event.getOrder(), questName=self.event.getUserName())
        result['linkTooltip'] = backport.text(battleResults.linkBtn.tooltip())
        return result

    def _getProgresses(self, pCur, pPrev):
        index = 0
        progresses = []
        for cond in self.event.bonusCond.getConditions().items:
            if isinstance(cond, conditions._Cumulativable):
                for _, (curProg, totalProg, diff, _) in cond.getProgressPerGroup(pCur, pPrev).iteritems():
                    if not diff:
                        continue
                    index += 1
                    progresses.append({'progrTooltip': None,
                     'progrBarType': formatters.PROGRESS_BAR_TYPE.SIMPLE,
                     'maxProgrVal': totalProg,
                     'currentProgrVal': curProg,
                     'description': '%d. %s' % (index, self.event.getConditionLbl()),
                     'progressDiff': '+ %s' % backport.getIntegralFormat(diff),
                     'progressDiffTooltip': backport.text(R.strings.battle_matters.battleResults.progress.tooltip())})

        return progresses


def _getEventInfoData(event):
    if str(event.getID()).startswith(BATTLE_MATTERS_QUEST_ID):
        return _BattleMattersQuestInfo(event)
    if event.getType() == constants.EVENT_TYPE.PERSONAL_MISSION:
        return PersonalMissionPostBattleInfo(event)
    if event.getType() == constants.EVENT_TYPE.MOTIVE_QUEST:
        return MotiveQuestPostBattleInfo(event)
    if event.getType() in constants.EVENT_TYPE.QUEST_RANGE:
        postBattleInfoCls = event.postBattleInfo() or QuestPostBattleInfo
        return postBattleInfoCls(event)
    return EventPostBattleInfo(event)


def getEventPostBattleInfo(event, svrEvents=None, pCur=None, pPrev=None, isProgressReset=False, isCompleted=False, progressData=None):
    return _getEventInfoData(event).getPostBattleInfo(svrEvents, pCur or {}, pPrev or {}, isProgressReset, isCompleted, progressData)


class Progression2dStyleFormater(object):
    c11nService = dependency.descriptor(ICustomizationService)

    @classmethod
    def getProgress(cls, event, pCur, pPrev, isCompleted):
        progresses = []
        for cond in event.bonusCond.getConditions().items:
            if isinstance(cond, conditions._Cumulativable):
                for _, (curProg, totalProg, diff, _) in cond.getProgressPerGroup(pCur, pPrev).iteritems():
                    label = cond.getUserString()
                    customDescription = cond.getCustomDescription()
                    if customDescription is not None:
                        label = customDescription
                    for orItem in event.postBattleCond.getConditions().items:
                        customDescription = orItem.getCustomDescription()
                        if customDescription is not None:
                            label = customDescription

                    if not diff or not label:
                        continue
                    state = cls.getStatus(isCompleted) if isCompleted else None
                    progresses.append({'progrTooltip': None,
                     'progrBarType': formatters.PROGRESS_BAR_TYPE.SIMPLE,
                     'maxProgrVal': totalProg,
                     'currentProgrVal': curProg,
                     'description': label,
                     'progressDiff': '+ %s' % backport.getIntegralFormat(diff),
                     'progressDiffTooltip': TOOLTIPS.QUESTS_PROGRESS_EARNEDINBATTLE,
                     'questState': state})

        firstPostCond = first(event.postBattleCond.getConditions().items)
        if firstPostCond and not progresses:
            label = ''
            customDescription = firstPostCond.getCustomDescription()
            if customDescription is not None:
                label = customDescription
            if label:
                state = cls.getStatus(True)
                progresses.append({'progrTooltip': None,
                 'progrBarType': formatters.PROGRESS_BAR_TYPE.SIMPLE,
                 'maxProgrVal': 1,
                 'currentProgrVal': 1,
                 'description': label,
                 'progressDiff': '+ %s' % backport.getIntegralFormat(0),
                 'progressDiffTooltip': TOOLTIPS.QUESTS_PROGRESS_EARNEDINBATTLE,
                 'questState': state})
        if event.accountReqs.getTokens():
            state = cls.getStatus(isCompleted)
            progresses.append({'progrTooltip': None,
             'progrBarType': formatters.PROGRESS_BAR_TYPE.SIMPLE,
             'maxProgrVal': 1,
             'currentProgrVal': 1,
             'description': event.getDescription(),
             'progressDiff': '+ %s' % backport.getIntegralFormat(0),
             'progressDiffTooltip': TOOLTIPS.QUESTS_PROGRESS_EARNEDINBATTLE,
             'questState': state})
        title = ''
        itemCD = cls.c11nService.getItemCDByQuestID(event.getID())
        if itemCD:
            item = cls.c11nService.getItemByCD(itemCD)
            groupID, _ = item.getQuestsProgressionInfo()
            if groupID:
                title = backport.text(R.strings.vehicle_customization.customization.quests.pbsItem(), itemType=item.userType, itemName=item.userName)
        if progresses:
            progresses[0]['title'] = title
        return progresses

    @classmethod
    def getProgressRate(cls, event, pCur, pPrev, isCompleted):
        if isCompleted:
            return 1
        progress = 0
        count = 0
        for cond in event.bonusCond.getConditions().items:
            if isinstance(cond, conditions._Cumulativable):
                for _, (curProg, totalProg, __, ___) in cond.getProgressPerGroup(pCur, pPrev).iteritems():
                    progress += curProg / float(totalProg)
                    count += 1

        return progress / float(count) if count else progress

    @classmethod
    def getTitle(cls, style):
        return backport.text(R.strings.vehicle_customization.customization.postBattle.title(), value=style.userName)

    @classmethod
    def getStatus(cls, isComplete=None):
        if isComplete:
            msg = text_styles.bonusAppliedText(QUESTS.QUESTS_STATUS_DONE)
            return {'statusState': PERSONAL_MISSIONS_ALIASES.POST_BATTLE_STATE_DONE,
             'statusText': msg}
        msg = text_styles.neutral(QUESTS.PERSONALMISSION_STATUS_INPROGRESS)
        return {'statusState': PERSONAL_MISSIONS_ALIASES.POST_BATTLE_STATE_IN_PROGRESS,
         'statusText': msg}


@dependency.replace_none_kwargs(c11nService=ICustomizationService)
def get2dProgressionStylePostBattleInfo(styleID, quests, c11nService=None):
    style = c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)
    eventData = first(quests)
    if not eventData:
        return None
    else:
        event = eventData[0]
        fromatter = Progression2dStyleFormater
        info = {'awards': [],
         'alertMsg': '',
         'questInfo': _getEventInfoData(event).getInfo([]),
         'questState': fromatter.getStatus(isComplete=False),
         'questType': event.getType()}
        filteredQuests = {}
        for eventData in quests:
            questRate = fromatter.getProgressRate(*eventData)
            event = eventData[0]
            progressData = getDataByC11nQuest(event)
            branch = progressData.branch
            level = progressData.level
            if branch <= 0 or level <= 0:
                continue
            if (branch, level) not in filteredQuests:
                filteredQuests[branch, level] = (questRate, eventData)
                continue
            rate, __ = filteredQuests[branch, level]
            if questRate > rate:
                filteredQuests[branch, level] = (questRate, eventData)

        sortedQuests = [ eventData for _, (rate, eventData) in sorted(filteredQuests.items(), key=lambda t: t[0]) ]
        progressList = []
        for eventData in sortedQuests:
            progressInfo = fromatter.getProgress(*eventData)
            if progressInfo:
                progressList.extend(progressInfo)

        info['questInfo'].update({'description': fromatter.getTitle(style),
         'tasksCount': -1})
        linkBtnEnabled, linkBtnTooltip = getC11n2dProgressionLinkBtnParams()
        info.update({'linkBtnVisible': linkBtnEnabled,
         'linkBtnTooltip': backport.text(linkBtnTooltip),
         'progressList': progressList})
        return info


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
