# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/missions_helper.py
import operator
import sys
import BigWorld
import constants
from debug_utils import LOG_WARNING
from gui.Scaleform.daapi.view.lobby.missions import cards_formatters
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer, DetailedCardAwardComposer, PersonalMissionsAwardComposer
from gui.Scaleform.daapi.view.lobby.missions.cards_formatters import PMCardConditionsFormatter
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_BUTTONS import PERSONAL_MISSIONS_BUTTONS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events import events_helpers
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.cond_formatters.prebattle import MissionsPreBattleConditionsFormatter
from gui.server_events.cond_formatters.requirements import AccountRequirementsFormatter, TQAccountRequirementsFormatter
from gui.server_events.conditions import GROUP_TYPE
from gui.server_events.events_helpers import MISSIONS_STATES, QuestInfoModel, AWARDS_PER_SINGLE_PAGE
from gui.server_events.formatters import isMarathon, DECORATION_SIZES
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency, int2roman
from helpers.i18n import makeString as _ms
from quest_xml_source import MAX_BONUS_LIMIT
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
CARD_AWARDS_COUNT = 6
DETAILED_CARD_AWARDS_COUNT = 10
_preBattleConditionFormatter = MissionsPreBattleConditionsFormatter()
_accountReqsFormatter = AccountRequirementsFormatter()
_tqAccountReqsFormatter = TQAccountRequirementsFormatter()
_cardCondFormatter = cards_formatters.CardBattleConditionsFormatters()
_detailedCardCondFormatter = cards_formatters.DetailedCardBattleConditionsFormatters()
_cardTokenConditionFormatter = cards_formatters.CardTokenConditionFormatter()
_detailedCardTokenConditionFormatter = cards_formatters.DetailedCardTokenConditionFormatter()
_cardAwardsFormatter = CurtailingAwardsComposer(CARD_AWARDS_COUNT)
_detailedCardAwardsFormatter = DetailedCardAwardComposer(DETAILED_CARD_AWARDS_COUNT)
_awardsWindowBonusFormatter = CurtailingAwardsComposer(sys.maxint)
_personalMissionsConditionsFormatter = PMCardConditionsFormatter()
_personalMissionsAwardsFormatter = PersonalMissionsAwardComposer(DETAILED_CARD_AWARDS_COUNT)
HIDE_DONE = 'hideDone'
HIDE_UNAVAILABLE = 'hideUnavailable'
AWARD_SHEET_ICON = icons.makeImageTag(RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_SHEET_RECEIVED_SMALL, 16, 16, -2, 0)

class BG_STATES(object):
    COMPLETED = 'completed'
    MARATHON = 'marathon'
    DISABLED = 'disabled'
    DEFAULT = 'default'


def getCompletetBonusLimitTooltip():
    return {'tooltip': makeTooltip(body=_ms(TOOLTIPS.QUESTS_COMPLETE_PROGRESS_STATUSTOOLTIP)),
     'isSpecial': False,
     'specialArgs': []}


def getCompletetBonusLimitValueTooltip(count):
    return {'tooltip': makeTooltip(body=_ms(TOOLTIPS.QUESTS_COMPLETE_PROGRESS_VALUE_STATUSTOOLTIP, count=text_styles.neutral(count))),
     'isSpecial': False,
     'specialArgs': []}


def getBonusLimitTooltip(bonusCount, bonusLimit, isDaily):
    header = _ms(TOOLTIPS.QUESTS_COMPLETE_PROGRESS_HEADER)
    if isDaily:
        key = TOOLTIPS.QUESTS_COMPLETE_PROGRESSDAILY_BODY
    else:
        key = TOOLTIPS.QUESTS_COMPLETE_PROGRESS_BODY
    body = _ms(key, count=text_styles.neutral(bonusCount), totalCount=text_styles.neutral(bonusLimit))
    return {'tooltip': makeTooltip(header=header, body=body),
     'isSpecial': False,
     'specialArgs': []}


def getPersonalBonusLimitDailyTooltip(bonusCount, bonusLimit, maxCompleteCount):
    totalLabel = text_styles.standard(_ms(TOOLTIPS.QUESTS_COMPLETE_PROGRESSDAILY_DAILYCOUNT, totalCount=text_styles.neutral(maxCompleteCount), dailyCount=text_styles.neutral(max(bonusLimit - bonusCount, 0))))
    header = _ms(TOOLTIPS.QUESTS_COMPLETE_PROGRESSDAILY_HEADER)
    body = _ms(TOOLTIPS.QUESTS_COMPLETE_PERSONAL_PROGRESSDAILY_BODY, count=text_styles.neutral(bonusCount), totalCount=totalLabel, dailyTotalCount=text_styles.neutral(bonusLimit))
    return {'tooltip': makeTooltip(header=header, body=body),
     'isSpecial': False,
     'specialArgs': []}


def getPersonalReqularTooltip(bonusCount):
    header = _ms(TOOLTIPS.QUESTS_COMPLETE_PROGRESSDAILY_HEADER)
    body = _ms(TOOLTIPS.QUESTS_COMPLETE_PERSONALREGULAR_BODY, count=text_styles.neutral(bonusCount))
    return {'tooltip': makeTooltip(header=header, body=body),
     'isSpecial': False,
     'specialArgs': []}


def getDisabledRequirementTooltip(event):
    return {'tooltip': TOOLTIPS_CONSTANTS.UNAVAILABLE_QUEST,
     'isSpecial': True,
     'specialArgs': [event.getID()],
     'specialAlias': TOOLTIPS_CONSTANTS.UNAVAILABLE_QUEST}


def getInvalidTimeIntervalsTooltip(event):
    return {'tooltip': TOOLTIPS_CONSTANTS.SHEDULE_QUEST,
     'isSpecial': True,
     'specialArgs': [event.getID()],
     'specialAlias': TOOLTIPS_CONSTANTS.SHEDULE_QUEST}


def getScheduleLabel():
    text = text_styles.main(QUESTS.MISSIONDETAILS_STATUS_NOTAVAILABLEBYTIME)
    clockIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_RENT_ICO_BIG, 19, 19, -4, 8)
    return text_styles.concatStylesToSingleLine(clockIcon, text)


def getOperations(currOperationID):
    operations = []
    for oID, o in sorted(events_helpers.getPersonalMissionsCache().getOperations().iteritems(), key=operator.itemgetter(0)):
        state = PERSONAL_MISSIONS_ALIASES.OPERATION_UNLOCKED_STATE
        descr = text_styles.stats(PERSONAL_MISSIONS.OPERATIONS_UNLOCKED_DESC)
        title = text_styles.highTitle(o.getShortUserName())
        if not o.isUnlocked():
            state = PERSONAL_MISSIONS_ALIASES.OPERATION_LOCKED_STATE
            descr = text_styles.error(PERSONAL_MISSIONS.OPERATIONS_LOCKED_DESC)
        elif o.isFullCompleted():
            state = PERSONAL_MISSIONS_ALIASES.OPERATION_COMPLETE_FULL_STATE
            descr = text_styles.bonusAppliedText(PERSONAL_MISSIONS.OPERATIONS_FULLYCOMPLETED_DESC)
        elif o.isAwardAchieved():
            state = PERSONAL_MISSIONS_ALIASES.OPERATION_COMPLETE_STATE
            descr = text_styles.bonusAppliedText(PERSONAL_MISSIONS.OPERATIONS_COMPLETED_DESC)
        elif o.isInProgress():
            state = PERSONAL_MISSIONS_ALIASES.OPERATION_CURRENT_STATE
            descr = text_styles.neutral(PERSONAL_MISSIONS.OPERATIONS_CURRENT_DESC)
        elif not o.hasRequiredVehicles():
            state = PERSONAL_MISSIONS_ALIASES.OPERATION_LOCKED_STATE
            descr = text_styles.error(PERSONAL_MISSIONS.OPERATIONS_LOCKED_DESC)
        if state != PERSONAL_MISSIONS_ALIASES.OPERATION_UNLOCKED_STATE:
            iconStateSource = RES_ICONS.getPersonalMissionOperationState(state)
        else:
            iconStateSource = None
        freeSheetIcon = ''
        freeSheetCounter = ''
        tokensPawned = o.getTokensPawnedCount()
        if tokensPawned:
            freeSheetIcon = RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_SHEET_RECEIVED_SMALL
            freeSheetCounter = text_styles.counter('x%d' % tokensPawned)
        operationVO = {'title': title,
         'desc': descr,
         'iconSource': RES_ICONS.getPersonalMissionOperationImage(oID),
         'iconStateSource': iconStateSource,
         'freeSheetIconSource': freeSheetIcon,
         'freeSheetCounter': freeSheetCounter,
         'state': state,
         'isSelected': oID == currOperationID,
         'id': oID}
        operations.append(operationVO)

    return operations


def _getDailyLimitedStatusKey(isDaily):
    return QUESTS.MISSIONDETAILS_MISSIONSCOMPLETE_DAILY if isDaily else QUESTS.MISSIONDETAILS_MISSIONSCOMPLETE


class _MissionInfo(QuestInfoModel):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, event):
        super(_MissionInfo, self).__init__(event)
        self.__formattedBonuses = None
        self._mainFormattedConditions = None
        return

    def getInfo(self, mainQuest=None):
        isAvailable, errorMsg = self.event.isAvailable()
        statusData = self._getStatusFields(isAvailable, errorMsg)
        return self._getInfo(statusData, isAvailable, errorMsg, mainQuest)

    def getSubstituteBonuses(self):
        return self._substituteBonuses()

    def _getInfo(self, statusData, isAvailable, errorMsg, mainQuest=None):
        status = statusData['status']
        data = {'eventID': self._getEventID(),
         'title': self._getTitle(self.event.getUserName()),
         'isAvailable': isAvailable,
         'statusLabel': statusData.get('statusLabel'),
         'statusTooltipData': statusData.get('statusTooltipData', ''),
         'status': status,
         'background': self._getBackGround(status),
         'uiDecoration': self._getUIDecoration()}
        data.update(self._getConditions())
        data.update(self._getAwards(mainQuest))
        return data

    def _getEventID(self):
        return self.event.getID()

    def _getUIDecoration(self):
        return self.eventsCache.prefetcher.getMissionDecoration(self.event.getIconID(), DECORATION_SIZES.CARDS)

    def _getMissionDurationTooltipData(self):
        header = _ms(TOOLTIPS.QUESTS_UNAVAILABLE_TIME_STATUSTOOLTIP)
        body = _ms(QUESTS.MISSIONS_TAB_MARATHONS_HEADER_PERIOD, startDate=BigWorld.wg_getLongDateFormat(self.event.getStartTime()), endDate=BigWorld.wg_getLongDateFormat(self.event.getFinishTime()))
        note = None
        timeLeft = self.event.getNearestActivityTimeLeft()
        if timeLeft is not None:
            startTimeLeft = timeLeft[0]
            if startTimeLeft > 0:
                note = text_styles.neutral(_ms('#quests:missionDetails/status/notAvailable/nearestTime', time=self._getTillTimeString(startTimeLeft)))
        return {'tooltip': makeTooltip(header, body, note),
         'isSpecial': False,
         'specialArgs': None}

    def _getCompleteStatusFields(self, isLimited, bonusCount, bonusLimit):
        if self.event.bonusCond.isDaily():
            status = MISSIONS_STATES.NOT_AVAILABLE
            clockIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_TIMERICON, 16, 16, -2, 8)
            statusText = _ms(QUESTS.MISSIONDETAILS_STATUS_NOTAVAILABLE)
            statusLabel = text_styles.concatStylesWithSpace(clockIcon, text_styles.error(statusText))
            statusTooltipData = {'tooltip': makeTooltip(_ms(TOOLTIPS.QUESTS_UNAVAILABLE_TIME_STATUSTOOLTIP), self._getCompleteDailyStatus(QUESTS.MISSIONDETAILS_STATUS_COMPLETED_DAILY)),
             'isSpecial': False,
             'specialArgs': None}
        else:
            status = MISSIONS_STATES.COMPLETED
            if isLimited and bonusLimit > 1:
                statusLabel = text_styles.bonusAppliedText(_ms(QUESTS.MISSIONDETAILS_MISSIONSCOMPLETE, count=text_styles.bonusAppliedText(bonusCount), total=text_styles.standard(bonusLimit)))
                statusTooltipData = getCompletetBonusLimitTooltip()
            else:
                statusTooltipData = None
                progressDesc = text_styles.bonusAppliedText(_ms(QUESTS.QUESTS_STATUS_DONE))
                icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OKICON, 16, 16, -2, 8)
                statusLabel = text_styles.concatStylesToSingleLine(icon, progressDesc)
        return {'statusLabel': statusLabel,
         'status': status,
         'statusTooltipData': statusTooltipData}

    def _getUnavailableStatusFields(self, errorMsg):
        if errorMsg == 'requirements':
            vehicleReqs = self.event.vehicleReqs
            isVehAvailable = vehicleReqs.isAnyVehicleAcceptable() or vehicleReqs.getSuitableVehicles()
            if not isVehAvailable:
                statusText = _ms(QUESTS.MISSIONDETAILS_STATUS_WRONGVEHICLE)
            else:
                statusText = _ms(QUESTS.MISSIONDETAILS_STATUS_NOTAVAILABLE)
            notAvailableIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_MARKER_BLOCKED, 14, 14, -2, 10)
            statusMsg = text_styles.concatStylesWithSpace(notAvailableIcon, text_styles.error(statusText))
            tooltipData = getDisabledRequirementTooltip(self.event)
        else:
            clockIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_TIMERICON, 16, 16, -2, 8)
            statusMsg = text_styles.concatStylesWithSpace(clockIcon, text_styles.error(QUESTS.MISSIONDETAILS_STATUS_NOTAVAILABLE))
            if errorMsg in ('invalid_weekday', 'invalid_time_interval'):
                tooltipData = getInvalidTimeIntervalsTooltip(self.event)
            else:
                tooltipData = self._getMissionDurationTooltipData()
        return {'statusLabel': statusMsg,
         'status': MISSIONS_STATES.NOT_AVAILABLE,
         'statusTooltipData': tooltipData}

    def _getRegularStatusFields(self, isLimited, bonusCount, bonusLimit):
        statusTooltipData = None
        timerMsg = self.getTimerMsg('comeToEndInMinutesSeparated')
        if isLimited:
            isDaily = self.event.bonusCond.isDaily()
            statusLabel = text_styles.standard(_ms(_getDailyLimitedStatusKey(isDaily), count=text_styles.stats(bonusCount), total=text_styles.standard(bonusLimit)))
            statusTooltipData = getBonusLimitTooltip(bonusCount, bonusLimit, isDaily)
        elif self.event.getWeekDays() or self.event.getActiveTimeIntervals():
            statusLabel = getScheduleLabel()
            statusTooltipData = getInvalidTimeIntervalsTooltip(self.event)
        elif timerMsg:
            statusLabel = timerMsg
        else:
            statusTooltipData = getCompletetBonusLimitValueTooltip(self.event.getBonusCount())
            statusLabel = text_styles.standard(_ms(QUESTS.MISSIONDETAILS_MISSIONSCOMPLETECOUNTER, count=text_styles.stats(self.event.getBonusCount())))
        return {'statusLabel': statusLabel,
         'status': MISSIONS_STATES.NONE,
         'statusTooltipData': statusTooltipData}

    def _getStatusFields(self, isAvailable, errorMsg):
        bonusLimit = self.event.bonusCond.getBonusLimit()
        bonusCount = min(self.event.getBonusCount(), bonusLimit)
        isLimited = self._isLimited()
        if self.event.isCompleted():
            return self._getCompleteStatusFields(isLimited, bonusCount, bonusLimit)
        return self._getUnavailableStatusFields(errorMsg) if not isAvailable else self._getRegularStatusFields(isLimited, bonusCount, bonusLimit)

    def _getBackGround(self, status):
        if status == MISSIONS_STATES.COMPLETED:
            return BG_STATES.COMPLETED
        return BG_STATES.MARATHON if isMarathon(self.event.getGroupID()) else BG_STATES.DEFAULT

    def _getAwards(self, mainQuest=None):
        if self.__formattedBonuses is None:
            self.__formattedBonuses = _cardAwardsFormatter.getFormattedBonuses(self._substituteBonuses(mainQuest))
        return {'awards': self.__formattedBonuses}

    def _getConditions(self):
        return {'battleConditions': self._getMainConditions()}

    def _getDailyResetStatusLabel(self):
        dailyStr = self._getDailyResetStatus(QUESTS.MISSIONDETAILS_RESETDATE, text_styles.main)
        if dailyStr:
            clockIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_RENT_ICO_BIG, 19, 19, -4, 8)
            return text_styles.concatStylesToSingleLine(clockIcon, dailyStr)
        return dailyStr

    def _getMainConditions(self):
        if self._mainFormattedConditions is None:
            self._mainFormattedConditions = _cardCondFormatter.format(self.event)
        return self._mainFormattedConditions

    def _isLimited(self):
        bonusLimit = self.event.bonusCond.getBonusLimit()
        return False if bonusLimit is None or bonusLimit >= MAX_BONUS_LIMIT else True

    def _getTitle(self, title):
        return text_styles.highlightText(title)

    def _substituteBonuses(self, mainQuest=None):
        if not self.event.isCompensationPossible():
            return self.event.getBonuses()
        else:
            if mainQuest is None:
                mainQuest = first(self.eventsCache.getQuests(lambda q: isMarathon(q.getID()) and q.getGroupID() == self.event.getGroupID()).values())
            if mainQuest:
                bonuses = self.event.getBonuses()
                toCompensate = []
                for token in mainQuest.accountReqs.getTokens():
                    if token.isAvailable():
                        toCompensate.append(token.getID())

                if not toCompensate:
                    return bonuses
                resultBonus = []
                for bonus in bonuses:
                    if bonus.getName() == 'battleToken':
                        tokenID = first(bonus.getTokens())
                        if tokenID in toCompensate:
                            compensation = self.eventsCache.getCompensation(tokenID)
                            if compensation:
                                resultBonus.extend(compensation)
                                continue
                    resultBonus.append(bonus)

                return resultBonus
            return self.event.getBonuses()
            return


class _TokenMissionInfo(_MissionInfo):

    def _getMainConditions(self):
        if self._mainFormattedConditions is None:
            self._mainFormattedConditions = _cardTokenConditionFormatter.format(self.event)
        return self._mainFormattedConditions


class _PrivateMissionInfo(_MissionInfo):

    def _getRegularStatusFields(self, isLimited, bonusCount, bonusLimit):
        statusData = super(_PrivateMissionInfo, self)._getRegularStatusFields(isLimited, bonusCount, bonusLimit)
        return self._getUpdatedByTokenStatusData(statusData, bonusCount, bonusLimit)

    def _getUpdatedByTokenStatusData(self, statusData, bonusCount, bonusLimit):
        tokens = self.event.accountReqs.getTokens()
        for token in tokens:
            if token.getID() == self.event.getRequiredToken() and token.isConsumable():
                maxCompleteCount = int(token.getReceivedCount() / token.getNeededCount())
                statusLabel = text_styles.standard(_ms(QUESTS.MISSIONDETAILS_PERSONALQUEST_COMPLETE_LEFT, count=text_styles.stats(maxCompleteCount)))
                if self.event.bonusCond.isDaily():
                    statusTooltipData = getPersonalBonusLimitDailyTooltip(bonusCount, bonusLimit, maxCompleteCount)
                    statusLabel = self._getPersonalDailyStatusLabel(statusLabel, bonusLimit, bonusCount)
                else:
                    statusTooltipData = getPersonalReqularTooltip(bonusCount)
                statusData.update({'statusLabel': statusLabel,
                 'statusTooltipData': statusTooltipData})
                break

        return statusData

    @classmethod
    def _getPersonalDailyStatusLabel(cls, statusLabel, bonusLimit, bonusCount):
        dailyLeftLabel = text_styles.standard(_ms(QUESTS.MISSIONDETAILS_PERSONALQUEST_COMPLETE_LEFT_DAILY, count=text_styles.stats(max(bonusLimit - bonusCount, 0))))
        return '%s\n%s' % (statusLabel, dailyLeftLabel)


class _DetailedMissionInfo(_MissionInfo):
    __AWARDS_COUNT = 6

    def getVehicleRequirementsCriteria(self):
        conds = self.event.vehicleReqs.getConditions()
        extraConditions = []
        if conds.type == GROUP_TYPE.OR:
            LOG_WARNING('OR group is not supported in vehicle section')
            return (REQ_CRITERIA.DISCLOSABLE, [])
        cond = conds.find('vehicleDescr') or conds.find('premiumVehicle')
        if cond:
            criteria = cond.getFilterCriteria(cond.getData())
        else:
            criteria = REQ_CRITERIA.DISCLOSABLE
        xpMultCond = conds.find('hasReceivedMultipliedXP')
        if xpMultCond:
            extraConditions.append(xpMultCond)
        return (criteria, extraConditions)

    def _getUIDecoration(self):
        decoration = self.eventsCache.prefetcher.getMissionDecoration(self.event.getIconID(), DECORATION_SIZES.DETAILS_EX)
        if decoration:
            return decoration
        decoration = self.eventsCache.prefetcher.getMissionDecoration(self.event.getIconID(), DECORATION_SIZES.DETAILS)
        return decoration if decoration else RES_ICONS.MAPS_ICONS_QUESTS_DECORATIONS_DEFAULT_750X264

    def _getInfo(self, statusData, isAvailable, errorMsg, mainQuest=None):
        data = super(_DetailedMissionInfo, self)._getInfo(statusData, isAvailable, errorMsg, mainQuest)
        data.update({'statusLabel': statusData.get('statusLabel', ''),
         'resetDateLabel': statusData.get('scheduleOrResetLabel', ''),
         'scheduleTooltip': statusData.get('scheduleTooltip'),
         'titleTooltip': self.__getDescription(),
         'dateLabel': statusData.get('dateLabel', ''),
         'bottomStatusText': statusData.get('bottomStatusText', '')})
        return data

    def _getStatusFields(self, isAvailable, errorMsg):
        bonusLimit = self.event.bonusCond.getBonusLimit()
        bonusCount = min(self.event.getBonusCount(), bonusLimit)
        isLimited = self._isLimited()
        if self.event.isCompleted():
            return self._getCompleteStatusFields(isLimited, bonusCount, bonusLimit)
        data = self._getRegularStatusFields(isLimited, bonusCount, bonusLimit)
        if not isAvailable:
            data.update(self._getUnavailableStatusFields(errorMsg))
        return data

    def _getCompleteStatusFields(self, isLimited, bonusCount, bonusLimit):
        statusTooltipData = None
        dateLabel = self._getActiveTimeDateLabel()
        resetDateLabel = ''
        status = MISSIONS_STATES.COMPLETED
        if isLimited and bonusLimit > 1:
            statusLabel = text_styles.bonusAppliedText(_ms(QUESTS.MISSIONDETAILS_MISSIONSCOMPLETE, count=text_styles.bonusAppliedText(bonusCount), total=text_styles.standard(bonusLimit)))
            statusTooltipData = getCompletetBonusLimitTooltip()
        else:
            progressDesc = text_styles.bonusAppliedText(_ms(QUESTS.QUESTS_STATUS_DONE))
            icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OKICON, 16, 16, -2, 8)
            statusLabel = text_styles.concatStylesToSingleLine(icon, progressDesc)
        if self.event.bonusCond.isDaily():
            status = MISSIONS_STATES.NOT_AVAILABLE
            dateLabel = text_styles.concatStylesWithSpace(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_TIMERICON, 16, 16, -2, 8), text_styles.error(QUESTS.MISSIONDETAILS_STATUS_NOTAVAILABLE), self._getCompleteDailyStatus(QUESTS.MISSIONDETAILS_STATUS_COMPLETED_DAILY))
            resetDateLabel = self._getDailyResetStatusLabel()
        return {'statusLabel': statusLabel,
         'dateLabel': dateLabel,
         'status': status,
         'bottomStatusText': text_styles.concatStylesWithSpace(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_DONE, 32, 32, -8), text_styles.missionStatusAvailable(QUESTS.MISSIONDETAILS_BOTTOMSTATUSCOMPLETE)),
         'statusTooltipData': statusTooltipData,
         'resetDateLabel': resetDateLabel}

    def _getUnavailableStatusFields(self, errorMsg):
        result = {'status': MISSIONS_STATES.NOT_AVAILABLE}
        if errorMsg != 'requirement':
            timeLeft = self.event.getNearestActivityTimeLeft()
            if timeLeft is not None:
                clockIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_TIMERICON, 16, 16, -2, 8)
                startTimeLeft = timeLeft[0]
                timeStatusText = text_styles.standard(_ms('#quests:missionDetails/status/notAvailable/%s' % errorMsg, time=self._getTillTimeString(startTimeLeft)))
                result['dateLabel'] = text_styles.concatStylesWithSpace(clockIcon, text_styles.error(QUESTS.MISSIONDETAILS_STATUS_WRONGTIME), timeStatusText)
            if errorMsg in ('invalid_weekday', 'invalid_time_interval'):
                result['scheduleOrResetLabel'] = getScheduleLabel()
                result['scheduleTooltip'] = getInvalidTimeIntervalsTooltip(self.event)
        return result

    def _getRegularStatusFields(self, isLimited, bonusCount, bonusLimit):
        scheduleOrResetLabel = ''
        scheduleTooltip = None
        if isLimited:
            isDaily = self.event.bonusCond.isDaily()
            statusLabel = text_styles.concatStylesWithSpace(icons.inProgress(), text_styles.standard(_ms(_getDailyLimitedStatusKey(isDaily), count=text_styles.stats(bonusCount), total=text_styles.standard(bonusLimit))))
            statusTooltipData = getBonusLimitTooltip(bonusCount, bonusLimit, isDaily)
        else:
            statusTooltipData = getCompletetBonusLimitValueTooltip(self.event.getBonusCount())
            statusLabel = text_styles.concatStylesWithSpace(icons.inProgress(), text_styles.standard(_ms(QUESTS.MISSIONDETAILS_MISSIONSCOMPLETECOUNTER, count=text_styles.stats(self.event.getBonusCount()))))
        if self.event.getWeekDays() or self.event.getActiveTimeIntervals():
            scheduleOrResetLabel = getScheduleLabel()
            scheduleTooltip = getInvalidTimeIntervalsTooltip(self.event)
        elif self.event.bonusCond.isDaily():
            scheduleOrResetLabel = self._getDailyResetStatusLabel()
        return {'statusLabel': statusLabel,
         'status': MISSIONS_STATES.NONE,
         'statusTooltipData': statusTooltipData,
         'dateLabel': self._getActiveTimeDateLabel(),
         'scheduleOrResetLabel': scheduleOrResetLabel,
         'scheduleTooltip': scheduleTooltip}

    def _getActiveTimeDateLabel(self):
        activeTimeStr = self._getActiveDateTimeString()
        return text_styles.standard(activeTimeStr) if activeTimeStr is not None else ''

    def _getConditions(self):
        conditions = {'prebattleConditions': self._getPrebattleConditions(),
         'battleConditions': self._getMainConditions()}
        accountRequirements = self._getAccountRequirements()
        if accountRequirements:
            conditions.update(accountRequirements=accountRequirements)
        return conditions

    def _getMainConditions(self):
        return _detailedCardCondFormatter.format(self.event)

    def _getPrebattleConditions(self):
        return _preBattleConditionFormatter.format(self.event.preBattleCond, self.event)

    def _getAccountRequirements(self):
        return _accountReqsFormatter.format(self.event.accountReqs, self.event)

    def _getAwards(self, mainQuest=None):
        return {'awards': _detailedCardAwardsFormatter.getFormattedBonuses(self._substituteBonuses(mainQuest))}

    def _getTitle(self, title):
        return text_styles.promoSubTitle(title)

    def __getDescription(self):
        description = self.event.getDescription()
        return None if not description else makeTooltip(QUESTS.MISSIONDETAILS_DESCRIPTION, description)


class _DetailedPrivateMissionInfo(_DetailedMissionInfo, _PrivateMissionInfo):

    def _getRegularStatusFields(self, isLimited, bonusCount, bonusLimit):
        statusData = super(_DetailedPrivateMissionInfo, self)._getRegularStatusFields(isLimited, bonusCount, bonusLimit)
        return self._getUpdatedByTokenStatusData(statusData, bonusCount, bonusLimit)

    @classmethod
    def _getPersonalDailyStatusLabel(cls, statusLabel, bonusLimit, bonusCount):
        text = _ms(QUESTS.MISSIONDETAILS_PERSONALQUEST_DETAILS_COMPLETE_LEFT_DAILY, count=text_styles.stats(max(bonusLimit - bonusCount, 0)))
        return text_styles.standard('%s (%s)' % (statusLabel, text_styles.standard(text)))


class _DetailedTokenMissionInfo(_DetailedMissionInfo):

    def getVehicleRequirementsCriteria(self):
        return (None, [])

    def _getMainConditions(self):
        return _detailedCardTokenConditionFormatter.format(self.event)

    def _getAccountRequirements(self):
        return _tqAccountReqsFormatter.format(self.event.accountReqs, self.event)

    def _getRegularStatusFields(self, isLimited, bonusCount, bonusLimit):
        statusData = super(_DetailedTokenMissionInfo, self)._getRegularStatusFields(isLimited, bonusCount, bonusLimit)
        statusLabel = statusData.get('bottomStatusText', '') or self.__getTokensCount()
        statusData.update({'bottomStatusText': statusLabel})
        return statusData

    def __getTokensCount(self):
        tokens = _detailedCardTokenConditionFormatter.getPreformattedConditions(self.event)
        needCount = 0
        gotCount = 0
        for tokenData in tokens:
            tokenNeedCount = tokenData.needCount
            needCount += tokenNeedCount
            gotCount += min(tokenData.gotCount, tokenNeedCount)

        return text_styles.middleTitle(_ms(QUESTS.MISSIONDETAILS_BOTTOMSTATUSTOKENS, count=gotCount, total=needCount)) if needCount or gotCount else ''


class _DetailedPersonalMissionInfo(_MissionInfo):

    def getVehicleRequirementsCriteria(self):
        extraConditions = []
        criteria = REQ_CRITERIA.INVENTORY
        criteria |= REQ_CRITERIA.VEHICLE.LEVELS(range(self.event.getVehMinLevel(), constants.MAX_VEHICLE_LEVEL + 1))
        criteria |= REQ_CRITERIA.VEHICLE.CLASSES(self.event.getVehicleClasses())
        return (criteria, extraConditions)

    def _getStatusFields(self, isAvailable, errorMsg):
        quest = self.event
        statusTooltipData = None
        if quest.isFullCompleted():
            return self._getFullCompleteStatusFields()
        elif not isAvailable:
            return self._getUnavailableStatusFields(errorMsg)
        elif quest.isInProgress():
            return self._getProgressStatusFields()
        elif quest.isCompleted():
            return self._getCompleteStatusFields()
        else:
            statusLabel = None
            status = MISSIONS_STATES.NONE
            return {'statusLabel': statusLabel,
             'status': status,
             'statusTooltipData': statusTooltipData}

    def _getUnavailableStatusFields(self, errorMsg):
        return self.__getNoVehicleStatusFields() if errorMsg == 'noVehicle' else self.__getUnlockedStatusFields()

    def _getFullCompleteStatusFields(self):
        quest = self.event
        statusTooltipData = {'tooltip': makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_FULLDONE_HEADER, body=TOOLTIPS.PERSONALMISSIONS_STATUS_FULLDONE_BODY)}
        statusLabel = text_styles.bonusAppliedText(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_DOUBLECHECKMARK, vSpace=-2) + ' ' + _ms(QUESTS.PERSONALMISSION_STATUS_FULLDONE))
        bottomStatusText = ''
        if quest.isDone():
            bottomStatusText = text_styles.missionStatusAvailable(QUESTS.PERSONALMISSION_BOTTOMSTATUS_ALLAWARDSRECEIVED)
        return {'statusLabel': statusLabel,
         'status': MISSIONS_STATES.FULL_COMPLETED,
         'statusTooltipData': statusTooltipData,
         'bottomStatusText': bottomStatusText}

    def _getCompleteStatusFields(self, *args):
        quest = self.event
        if quest.areTokensPawned():
            statusTooltipData = {'tooltip': makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_DONEWITHPAWN_HEADER, body=TOOLTIPS.PERSONALMISSIONS_STATUS_DONEWITHPAWN_BODY)}
            count = text_styles.stats(str(quest.getPawnCost()) + AWARD_SHEET_ICON)
            statusLabel = text_styles.bonusAppliedText(icons.checkmark() + _ms(QUESTS.PERSONALMISSION_STATUS_DONEWITHPAWN, count=count))
        else:
            statusLabel = text_styles.bonusAppliedText(icons.checkmark() + _ms(QUESTS.PERSONALMISSION_STATUS_MAINDONE))
            statusTooltipData = {'tooltip': makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_MAINDONE_HEADER, body=TOOLTIPS.PERSONALMISSIONS_STATUS_MAINDONE_BODY)}
        return {'statusLabel': statusLabel,
         'status': MISSIONS_STATES.COMPLETED,
         'statusTooltipData': statusTooltipData}

    def _getProgressStatusFields(self):

        def makeLabel(key):
            return text_styles.neutral(icons.inProgress() + _ms(key))

        quest = self.event
        if quest.areTokensPawned():
            statusLabel = '%s %s' % (makeLabel(QUESTS.PERSONALMISSION_STATUS_SHEETRECOVERYINPROGRESS), AWARD_SHEET_ICON)
            statusTooltipData = {'tooltip': makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_SHEETRECOVERYINPROGRESS_HEADER, body=TOOLTIPS.PERSONALMISSIONS_STATUS_SHEETRECOVERYINPROGRESS_BODY)}
        elif quest.isMainCompleted() and not quest.isFullCompleted():
            statusLabel = makeLabel(QUESTS.PERSONALMISSION_STATUS_ADDINPROGRESS)
            statusTooltipData = {'tooltip': makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_ADDINPROGRESS_HEADER, body=TOOLTIPS.PERSONALMISSIONS_STATUS_ADDINPROGRESS_BODY)}
        else:
            statusLabel = makeLabel(PERSONAL_MISSIONS.DETAILEDVIEW_STATUS_INPROGRESS)
            statusTooltipData = {'tooltip': makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_INPROGRESS_HEADER, body=TOOLTIPS.PERSONALMISSIONS_STATUS_INPROGRESS_BODY)}
        status = MISSIONS_STATES.NONE
        return {'statusLabel': statusLabel,
         'status': status,
         'statusTooltipData': statusTooltipData}

    def _getEventID(self):
        return str(self.event.getID())

    def _getUIDecoration(self):
        if self.event.isFinal():
            tile = self.eventsCache.personalMissions.getOperations()[self.event.getOperationID()]
            vehBonus = tile.getVehicleBonus()
            if vehBonus is not None:
                return vehBonus.name
        return 'Empty'

    def _getBackGround(self, status):
        if status in (MISSIONS_STATES.COMPLETED, MISSIONS_STATES.FULL_COMPLETED):
            return BG_STATES.COMPLETED
        return BG_STATES.DISABLED if status is MISSIONS_STATES.NOT_AVAILABLE else BG_STATES.DEFAULT

    def _getAwards(self, mainQuest=None):
        return {'awards': _personalMissionsAwardsFormatter.getFormattedBonuses(self.event.getBonuses(isMain=True), size=AWARDS_SIZES.BIG, isObtained=self.event.isMainCompleted(), obtainedImage=RES_ICONS.MAPS_ICONS_LIBRARY_AWARDOBTAINED, obtainedImageOffset=10),
         'awardsFullyCompleted': _personalMissionsAwardsFormatter.getFormattedBonuses(self.event.getBonuses(isMain=False), size=AWARDS_SIZES.BIG, isObtained=self.event.isFullCompleted(), areTokensPawned=self.event.areTokensPawned(), pawnCost=self.event.getPawnCost(), obtainedImage=RES_ICONS.MAPS_ICONS_LIBRARY_AWARDOBTAINED, obtainedImageOffset=10)}

    def _getConditions(self):
        return {'conditions': _personalMissionsConditionsFormatter.format(self.event, isMain=True),
         'conditionsFullyCompleted': _personalMissionsConditionsFormatter.format(self.event, isMain=False)}

    def _getTitle(self, title):
        return text_styles.promoSubTitle(title)

    def _getInfo(self, statusData, isAvailable, errorMsg, mainQuest=None):
        data = super(_DetailedPersonalMissionInfo, self)._getInfo(statusData, isAvailable, errorMsg, mainQuest)
        data.update({'bottomStatusText': statusData.get('bottomStatusText', ''),
         'addBottomStatusText': statusData.get('addBottomStatusText', ''),
         'bottomStatusTooltipData': statusData.get('bottomStatusTooltipData', ''),
         'retryBtnLabel': self.__getRetryBtnLabel(),
         'retryBtnTooltip': self.__getRetryBtnTooltip(),
         'completeBtnLabel': _ms(PERSONAL_MISSIONS.DETAILEDVIEW_COMPLETEBTNLABEL, count=self.event.getPawnCost(), icon=AWARD_SHEET_ICON),
         'titleTooltip': self.__getDescription(),
         'holdAwardSheetBtnTooltipData': self.__getHoldAwardSheetBtnTooltipData()})
        data.update({'buttonState': self.__getBtnStates(isAvailable)})
        return data

    def __getHoldAwardSheetBtnTooltipData(self):
        if self.__isPawnAvailable(self.event):
            specialAlias = TOOLTIPS_CONSTANTS.FREE_SHEET
        else:
            specialAlias = TOOLTIPS_CONSTANTS.FREE_SHEET_NOT_ENOUGH
        return {'specialAlias': specialAlias,
         'isSpecial': True,
         'specialArgs': []}

    def __getRetryBtnLabel(self):
        if self.event.areTokensPawned():
            if self.event.getPawnCost() <= 1:
                return _ms(PERSONAL_MISSIONS.TASKDETAILSVIEW_BTNLABEL_RETURNAWARDSHEET)
            return _ms(PERSONAL_MISSIONS.TASKDETAILSVIEW_BTNLABEL_RETURNAWARDSHEETS)
        return _ms(PERSONAL_MISSIONS.DETAILEDVIEW_RETRYBTNLABEL)

    def __getRetryBtnTooltip(self):
        return PERSONAL_MISSIONS.DETAILEDVIEW_TOOLTIPS_RETURNAWARDLISTBTN if self.event.areTokensPawned() else PERSONAL_MISSIONS.DETAILEDVIEW_TOOLTIPS_RETRYBTN

    def __getDescription(self):
        description = '\n'.join([self.event.getUserDescription(), self.event.getUserAdvice()])
        return None if not description else makeTooltip(PERSONAL_MISSIONS.DETAILEDVIEW_INFOPANEL_HEADER, description)

    def __getBtnStates(self, isAvailable):
        quest = self.event
        isPawnAvailable = self.__isPawnAvailable(quest)
        if not quest.isUnlocked():
            states = PERSONAL_MISSIONS_BUTTONS.START_BTN_VISIBLE
        elif quest.isInProgress():
            states = PERSONAL_MISSIONS_BUTTONS.DECLINE_BTN_VISIBLE
            if isAvailable:
                states |= PERSONAL_MISSIONS_BUTTONS.DECLINE_BTN_ENABLED
            if not quest.isMainCompleted():
                states |= PERSONAL_MISSIONS_BUTTONS.HOLD_AWARD_SHEET_BTN_VISIBLE
                if not quest.areTokensPawned() and isPawnAvailable:
                    states |= PERSONAL_MISSIONS_BUTTONS.HOLD_AWARD_SHEET_BTN_ENABLED
        elif quest.isFullCompleted():
            states = PERSONAL_MISSIONS_BUTTONS.NO_BUTTONS
        elif quest.isMainCompleted():
            states = PERSONAL_MISSIONS_BUTTONS.RETRY_BTN_VISIBLE
            if isAvailable:
                states |= PERSONAL_MISSIONS_BUTTONS.RETRY_BTN_ENABLED
        else:
            states = PERSONAL_MISSIONS_BUTTONS.START_BTN_VISIBLE
            if isAvailable:
                states |= PERSONAL_MISSIONS_BUTTONS.START_BTN_ENABLED
        if quest.canBePawned():
            states |= PERSONAL_MISSIONS_BUTTONS.HOLD_AWARD_SHEET_BTN_VISIBLE
            if isPawnAvailable:
                states |= PERSONAL_MISSIONS_BUTTONS.HOLD_AWARD_SHEET_BTN_ENABLED
        return states

    def __isPawnAvailable(self, quest):
        return self.eventsCache.random.getFreeTokensCount() >= quest.getPawnCost()

    def __getNoVehicleStatusFields(self):
        addBottomStatusText = text_styles.error(icons.markerBlocked() + ' ' + _ms(QUESTS.PERSONALMISSION_STATUS_LOCKEDBYVEHICLE))
        bottomStatusTooltipData = {'tooltip': makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_LOCKEDBYVEHICLE_HEADER, body=_ms(TOOLTIPS.PERSONALMISSIONS_STATUS_LOCKEDBYVEHICLE_BODY, vehType=', '.join([ _ms(MENU.classesShort(vehType)) for vehType in self.event.getVehicleClasses() ]), minLevel=int2roman(self.event.getVehMinLevel()), maxLevel=int2roman(self.event.getVehMaxLevel())))}
        if self.event.isInProgress():
            statusData = self._getProgressStatusFields()
            statusData.update(addBottomStatusText=addBottomStatusText)
            statusData.update(bottomStatusTooltipData=bottomStatusTooltipData)
            return statusData
        if self.event.isMainCompleted():
            statusData = self._getCompleteStatusFields()
            statusData.update(addBottomStatusText=addBottomStatusText)
            statusData.update(bottomStatusTooltipData=bottomStatusTooltipData)
            return statusData
        return {'addBottomStatusText': addBottomStatusText,
         'status': MISSIONS_STATES.NOT_AVAILABLE,
         'bottomStatusTooltipData': bottomStatusTooltipData}

    def __getUnlockedStatusFields(self):
        quest = self.event
        operations = events_helpers.getPersonalMissionsCache().getOperations()
        operationID = quest.getOperationID()
        operation = operations.get(operationID)
        if not operation.isUnlocked():
            prevOperationID = max(operationID - 1, 0)
            prevOperation = operations.get(prevOperationID)
            statusTooltipData = {'tooltip': makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_LOCKEDBYPREVOPERATION_HEADER, body=TOOLTIPS.PERSONALMISSIONS_STATUS_LOCKEDBYPREVOPERATION_BODY)}
            statusLabel = text_styles.error(icons.markerBlocked() + ' ' + _ms(QUESTS.PERSONALMISSION_STATUS_LOCKEDBYPREVOPERATION, prevCampaign=prevOperation.getShortUserName()))
        else:
            statusTooltipData = {'tooltip': makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_LOCKEDBYPREVMISSIONS_HEADER, body=TOOLTIPS.PERSONALMISSIONS_STATUS_LOCKEDBYPREVMISSIONS_BODY)}
            statusLabel = text_styles.error(icons.markerBlocked() + ' ' + _ms(QUESTS.PERSONALMISSION_STATUS_LOCKEDBYPREVMISSIONS))
        return {'addBottomStatusText': statusLabel,
         'status': MISSIONS_STATES.NOT_AVAILABLE,
         'bottomStatusTooltipData': statusTooltipData}


def getMissionInfoData(event):
    if event.getType() == constants.EVENT_TYPE.TOKEN_QUEST:
        return _TokenMissionInfo(event)
    elif event.getType() == constants.EVENT_TYPE.PERSONAL_QUEST:
        return _PrivateMissionInfo(event)
    else:
        return _MissionInfo(event) if event.getType() in constants.EVENT_TYPE.LIKE_BATTLE_QUESTS else None


def getDetailedMissionData(event):
    if event.getType() == constants.EVENT_TYPE.TOKEN_QUEST:
        return _DetailedTokenMissionInfo(event)
    elif event.getType() == constants.EVENT_TYPE.PERSONAL_QUEST:
        return _DetailedPrivateMissionInfo(event)
    elif event.getType() == constants.EVENT_TYPE.PERSONAL_MISSION:
        return _DetailedPersonalMissionInfo(event)
    else:
        return _DetailedMissionInfo(event) if event.getType() in constants.EVENT_TYPE.LIKE_BATTLE_QUESTS else None


def getAwardsWindowBonuses(bonuses):
    result = _awardsWindowBonusFormatter.getFormattedBonuses(bonuses, AWARDS_SIZES.BIG)
    while len(result) % AWARDS_PER_SINGLE_PAGE != 0 and len(result) > AWARDS_PER_SINGLE_PAGE:
        result.append({})

    return result


def getPersonalMissionAwardsFormatter():
    return _personalMissionsAwardsFormatter


def getMissionAwardsFormatter():
    return _awardsWindowBonusFormatter
