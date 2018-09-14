# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/missions_helper.py
import sys
import BigWorld
import constants
from gui.Scaleform.daapi.view.lobby.missions import cards_formatters
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CardAwardComposer, DetailedCardAwardComposer
from gui.Scaleform.daapi.view.lobby.missions.conditions_formatters.prebattle import MissionsPreBattleConditionsFormatter
from gui.Scaleform.daapi.view.lobby.missions.conditions_formatters.requirements import AccountRequirementsFormatter, TQAccountRequirementsFormatter
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events.events_helpers import EVENT_STATUS, QuestInfoModel, AWARDS_PER_PAGE, AWARDS_PER_SINGLE_PAGE
from gui.server_events.formatters import isMarathon, DECORATION_SIZES
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from helpers.i18n import makeString as _ms
from quest_xml_source import MAX_BONUS_LIMIT
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
CARD_AWARDS_COUNT = 6
DETAILED_CARD_AWARDS_COUNT = 10
preBattleConditionFormatter = MissionsPreBattleConditionsFormatter()
accountReqsFormatter = AccountRequirementsFormatter()
tqAccountReqsFormatter = TQAccountRequirementsFormatter()
cardCondFormatter = cards_formatters.CardBattleConditionsFormatters()
detailedCardCondFormatter = cards_formatters.DetailedCardBattleConditionsFormatters()
cardTokenConditionFormatter = cards_formatters.CardTokenConditionFormatter()
detailedCardTokenConditionFormatter = cards_formatters.DetailedCardTokenConditionFormatter()
cardAwardsFormatter = CardAwardComposer(CARD_AWARDS_COUNT)
detailedCardAwardsFormatter = DetailedCardAwardComposer(DETAILED_CARD_AWARDS_COUNT)
AwardsWindowBonusFormatter = CardAwardComposer(sys.maxint)
HIDE_DONE = 'hideDone'
HIDE_UNAVAILABLE = 'hideUnavailable'

class BG_STATES(object):
    COMPLETED = 'completed'
    MARATHON = 'marathon'
    DEFAULT = 'default'


def getCompletetBonusLimitTooltip():
    """
    Gets complex tooltip data about completed status wih bonus limits.
    """
    return {'tooltip': makeTooltip(body=_ms(TOOLTIPS.QUESTS_COMPLETE_PROGRESS_STATUSTOOLTIP)),
     'isSpecial': False,
     'args': []}


def getCompletetBonusLimitValueTooltip(count):
    """
    Gets complex tooltip data about completed status wih bonus limits.
    """
    return {'tooltip': makeTooltip(body=_ms(TOOLTIPS.QUESTS_COMPLETE_PROGRESS_VALUE_STATUSTOOLTIP, count=text_styles.neutral(count))),
     'isSpecial': False,
     'args': []}


def getBonusLimitTooltip(bonusCount, bonusLimit, isDaily):
    """
    Gets complex tooltip data about bonus limits
    bonusCount - mission's complete count
    bonusLimit - server definition, means that player several times can complete mission and get bonus
    """
    header = _ms(TOOLTIPS.QUESTS_COMPLETE_PROGRESS_HEADER)
    if isDaily:
        key = TOOLTIPS.QUESTS_COMPLETE_PROGRESSDAILY_BODY
    else:
        key = TOOLTIPS.QUESTS_COMPLETE_PROGRESS_BODY
    body = _ms(key, count=text_styles.neutral(bonusCount), totalCount=text_styles.neutral(bonusLimit))
    return {'tooltip': makeTooltip(header=header, body=body),
     'isSpecial': False,
     'args': []}


def getPersonalBonusLimitDailyTooltip(bonusCount, bonusLimit, maxCompleteCount):
    """
    Gets complex tooltip data about bonus limits
    bonusCount - mission's complete count
    bonusLimit - server definition, means that player several times can complete mission and get bonus per day
    """
    totalLabel = text_styles.standard(_ms(TOOLTIPS.QUESTS_COMPLETE_PROGRESSDAILY_DAILYCOUNT, totalCount=text_styles.neutral(maxCompleteCount), dailyCount=text_styles.neutral(max(bonusLimit - bonusCount, 0))))
    header = _ms(TOOLTIPS.QUESTS_COMPLETE_PROGRESSDAILY_HEADER)
    body = _ms(TOOLTIPS.QUESTS_COMPLETE_PERSONAL_PROGRESSDAILY_BODY, count=text_styles.neutral(bonusCount), totalCount=totalLabel, dailyTotalCount=text_styles.neutral(bonusLimit))
    return {'tooltip': makeTooltip(header=header, body=body),
     'isSpecial': False,
     'args': []}


def getPersonalReqularTooltip(bonusCount):
    """
    Gets complex tooltip data about complete count
    bonusCount - mission's complete count
    """
    header = _ms(TOOLTIPS.QUESTS_COMPLETE_PROGRESSDAILY_HEADER)
    body = _ms(TOOLTIPS.QUESTS_COMPLETE_PERSONALREGULAR_BODY, count=text_styles.neutral(bonusCount))
    return {'tooltip': makeTooltip(header=header, body=body),
     'isSpecial': False,
     'args': []}


def getDisabledRequirementTooltip(event):
    """
    Gets tooltip data to display unavailable requirements
    """
    return {'tooltip': TOOLTIPS_CONSTANTS.UNAVAILABLE_QUEST,
     'isSpecial': True,
     'args': [event.getID()]}


def getInvalidTimeIntervalsTooltip(event):
    """
    Gets tooltip data to display mission's schedule
    """
    return {'tooltip': TOOLTIPS_CONSTANTS.SHEDULE_QUEST,
     'isSpecial': True,
     'args': [event.getID()]}


def getScheduleLabel():
    """
    Gets formatted schedule label
    """
    text = text_styles.main(QUESTS.MISSIONDETAILS_STATUS_NOTAVAILABLEBYTIME)
    clockIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_RENT_ICO_BIG, 19, 19, -4, 8)
    return text_styles.concatStylesToSingleLine(clockIcon, text)


def _getDailyLimitedStatusKey(isDaily):
    if isDaily:
        return QUESTS.MISSIONDETAILS_MISSIONSCOMPLETE_DAILY
    else:
        return QUESTS.MISSIONDETAILS_MISSIONSCOMPLETE


class _MissionInfo(QuestInfoModel):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, event):
        super(_MissionInfo, self).__init__(event)
        self.__formattedBonuses = None
        self._mainFormattedConditions = None
        return

    def getInfo(self, mainQuest=None):
        """
        Gets all data for mission card: conditions, awards, status fields, etc
        Main data to display mission card in AS.
        Used by _EventsBlockInfo to grab all cards in block
        """
        isAvailable, errorMsg = self.event.isAvailable()
        statusData = self._getStatusFields(isAvailable, errorMsg)
        return self._getInfo(statusData, isAvailable, errorMsg, mainQuest)

    def getSubstituteBonuses(self):
        """
        Applies compensation to the quests that emit already gathered tokens.
        
        Compensation works on top of tokens mechanism: if main marathon token quest
        already consumed all necessary tokens, these tokens should be explicitly
        substituted with compensation in the emitter quests.
        
        Compensation means bonuses from the hidden compensation quests.
        """
        return self._substituteBonuses()

    def _getInfo(self, statusData, isAvailable, errorMsg, mainQuest=None):
        status = statusData['status']
        data = {'eventID': self.event.getID(),
         'title': self._getTitle(self.event.getUserName()),
         'isAvailable': isAvailable,
         'statusLabel': statusData.get('statusLabel'),
         'statusTooltipData': statusData.get('statusTooltipData'),
         'awards': self._getAwards(mainQuest),
         'status': status,
         'background': self._getBackGround(status),
         'uiDecoration': self._getUIDecoration()}
        data.update(self._getConditions())
        return data

    def _getUIDecoration(self):
        """
        Gets background decoration for mission's card from web
        """
        return self.eventsCache.prefetcher.getMissionDecoration(self.event.getIconID(), DECORATION_SIZES.CARDS)

    def _getMissionDurationTooltipData(self):
        """
        Gets complex tooltip data about mission duration and its nearest active time
        """
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
         'args': None}

    def _getCompleteStatusFields(self, isLimited, bonusCount, bonusLimit):
        """
        Gets status fields data for completed mission state.
        Data used in mission card to display its completed state.
        For completed daily quests return unavailable state fields.
        """
        if self.event.bonusCond.isDaily():
            status = EVENT_STATUS.NOT_AVAILABLE
            clockIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_TIMERICON, 16, 16, -2, 8)
            statusText = _ms(QUESTS.MISSIONDETAILS_STATUS_NOTAVAILABLE)
            statusLabel = text_styles.concatStylesWithSpace(clockIcon, text_styles.error(statusText))
            statusTooltipData = {'tooltip': makeTooltip(_ms(TOOLTIPS.QUESTS_UNAVAILABLE_TIME_STATUSTOOLTIP), self._getCompleteDailyStatus(QUESTS.MISSIONDETAILS_STATUS_COMPLETED_DAILY)),
             'isSpecial': False,
             'args': None}
        else:
            status = EVENT_STATUS.COMPLETED
            if isLimited and bonusLimit > 1:
                statusLabel = text_styles.bonusAppliedText(_ms(QUESTS.MISSIONDETAILS_MISSIONSCOMPLETE, count=text_styles.bonusAppliedText(bonusCount), total=text_styles.standard(bonusLimit)))
                statusTooltipData = getCompletetBonusLimitTooltip()
            else:
                statusTooltipData = None
                progressDesc = text_styles.success(_ms(QUESTS.QUESTS_STATUS_DONE))
                icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OKICON, 16, 16, -2, 8)
                statusLabel = text_styles.concatStylesToSingleLine(icon, progressDesc)
        return {'statusLabel': statusLabel,
         'status': status,
         'statusTooltipData': statusTooltipData}

    def _getUnavailableStatusFields(self, errorMsg):
        """
        Gets status fields data for unavailable mission state.
        Data used in mission card to display its unavailable state.
        """
        if errorMsg == 'requirements':
            isVehAvailable = self.event.vehicleReqs.isAnyVehicleAcceptable() or len(self.event.vehicleReqs.getSuitableVehicles()) > 0
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
         'status': EVENT_STATUS.NOT_AVAILABLE,
         'statusTooltipData': tooltipData}

    def _getRegularStatusFields(self, isLimited, bonusCount, bonusLimit):
        """
        Gets status fields data for regular mission state.
        Data used in mission card to display its regular state.
        """
        statusTooltipData = None
        timerMsg = self.getTimerMsg()
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
         'status': EVENT_STATUS.NONE,
         'statusTooltipData': statusTooltipData}

    def _getStatusFields(self, isAvailable, errorMsg):
        """
        Gets GUI data for all fields that relates to status
        """
        bonusLimit = self.event.bonusCond.getBonusLimit()
        bonusCount = min(self.event.getBonusCount(), bonusLimit)
        isLimited = self._isLimited()
        if self.event.isCompleted():
            return self._getCompleteStatusFields(isLimited, bonusCount, bonusLimit)
        elif not isAvailable:
            return self._getUnavailableStatusFields(errorMsg)
        else:
            return self._getRegularStatusFields(isLimited, bonusCount, bonusLimit)

    def _getBackGround(self, status):
        if status == EVENT_STATUS.COMPLETED:
            return BG_STATES.COMPLETED
        elif isMarathon(self.event.getGroupID()):
            return BG_STATES.MARATHON
        else:
            return BG_STATES.DEFAULT

    def _getAwards(self, mainQuest=None):
        """
        Gets formatted awards list to display on awards ribbon in GUI.
        Awards has minimized scale.
        """
        if self.__formattedBonuses is None:
            self.__formattedBonuses = cardAwardsFormatter.getFormattedBonuses(self._substituteBonuses(mainQuest))
        return self.__formattedBonuses

    def _getConditions(self):
        """
        Gets dict with different types of conditions
        For mission card displayed only bonus, postBattle and token conditions, prebattle conditions are not displayed
        """
        return {'battleConditions': self._getMainConditions()}

    def _getDailyResetStatusLabel(self):
        dailyStr = self._getDailyResetStatus(QUESTS.MISSIONDETAILS_RESETDATE, text_styles.main)
        if dailyStr:
            clockIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_RENT_ICO_BIG, 19, 19, -4, 8)
            return text_styles.concatStylesToSingleLine(clockIcon, dailyStr)
        return dailyStr

    def _getMainConditions(self):
        """
        Gets formatted conditions to display in GUI.
        Conditions are placed in the centre of card and contain icon, title, description and progress
        Conditions has minimized scale in mission card.
        """
        if self._mainFormattedConditions is None:
            self._mainFormattedConditions = cardCondFormatter.format(self.event)
        return self._mainFormattedConditions

    def _isLimited(self):
        bonusLimit = self.event.bonusCond.getBonusLimit()
        return False if bonusLimit is None or bonusLimit >= MAX_BONUS_LIMIT else True

    def _getTitle(self, title):
        return text_styles.highlightText(title)

    def _substituteBonuses(self, mainQuest=None):
        """ Applies compensation to the quests that emit already gathered tokens.
        
        Compensation works on top of tokens mechanism: if main marathon token quest
        already consumed all necessary tokens, these tokens should be explicitly
        substituted with compensation in the emitter quests.
        
        Compensation means bonuses from the hidden compensation quests.
        """
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
            self._mainFormattedConditions = cardTokenConditionFormatter.format(self.event)
        return self._mainFormattedConditions


class _PersonalMissionInfo(_MissionInfo):

    def _getRegularStatusFields(self, isLimited, bonusCount, bonusLimit):
        statusData = super(_PersonalMissionInfo, self)._getRegularStatusFields(isLimited, bonusCount, bonusLimit)
        return self._getUpdatedByTokenStatusData(statusData, bonusCount, bonusLimit)

    def _getUpdatedByTokenStatusData(self, statusData, bonusCount, bonusLimit):
        """
        There is special behavior fo personal quest.
        It is important to show complete remaining count info for personal quest,
        its depends on required tokens count in account
        """
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
        """ Gets criteria to find all suitable vehicles for current quest
        
        :return: tuple, list of required vehicles and list of extra conditions
        """
        conds = self.event.vehicleReqs.getConditions()
        extraConditions = []
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
        """
        No back decoration for detailed card view, only for simplified card
        """
        pass

    def _getInfo(self, statusData, isAvailable, errorMsg, mainQuest=None):
        data = super(_DetailedMissionInfo, self)._getInfo(statusData, isAvailable, errorMsg, mainQuest)
        data.update({'statusLabel': statusData.get('statusLabel', ''),
         'resetDateLabel': statusData.get('scheduleOrResetLabel', ''),
         'scheduleTooltip': statusData.get('scheduleTooltip'),
         'titleTooltip': self.__getDescription(),
         'dateLabel': statusData.get('dateLabel', ''),
         'bottomStatusText': statusData.get('bottomStatusText', '')})
        return data

    def _getCompleteStatusFields(self, isLimited, bonusCount, bonusLimit):
        """
        Gets status fields data for completed mission state.
        Data used in detailed mission view to display its completed state.
        For completed daily quests return unavailable state fields.
        """
        statusTooltipData = None
        dateLabel = self._getActiveTimeDateLabel()
        resetDateLabel = ''
        status = EVENT_STATUS.COMPLETED
        if isLimited and bonusLimit > 1:
            statusLabel = text_styles.bonusAppliedText(_ms(QUESTS.MISSIONDETAILS_MISSIONSCOMPLETE, count=text_styles.bonusAppliedText(bonusCount), total=text_styles.standard(bonusLimit)))
            statusTooltipData = getCompletetBonusLimitTooltip()
        else:
            progressDesc = text_styles.success(_ms(QUESTS.QUESTS_STATUS_DONE))
            icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OKICON, 16, 16, -2, 8)
            statusLabel = text_styles.concatStylesToSingleLine(icon, progressDesc)
        if self.event.bonusCond.isDaily():
            status = EVENT_STATUS.NOT_AVAILABLE
            dateLabel = text_styles.concatStylesWithSpace(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_TIMERICON, 16, 16, -2, 8), text_styles.error(QUESTS.MISSIONDETAILS_STATUS_NOTAVAILABLE), self._getCompleteDailyStatus(QUESTS.MISSIONDETAILS_STATUS_COMPLETED_DAILY))
            resetDateLabel = self._getDailyResetStatusLabel()
        return {'statusLabel': statusLabel,
         'dateLabel': dateLabel,
         'status': status,
         'bottomStatusText': text_styles.concatStylesWithSpace(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_DONE, 32, 32, -8), text_styles.missionStatusAvailable(QUESTS.MISSIONDETAILS_BOTTOMSTATUSCOMPLETE)),
         'statusTooltipData': statusTooltipData,
         'resetDateLabel': resetDateLabel}

    def _getUnavailableStatusFields(self, errorMsg):
        """
        Gets status fields data for unavailable mission state.
        Data used in detailed mission view to display its unavailable state.
        """
        scheduleLabel = ''
        dateLabel = ''
        scheduleTooltip = None
        if errorMsg != 'requirement':
            clockIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_TIMERICON, 16, 16, -2, 8)
            timeLeft = self.event.getNearestActivityTimeLeft()
            if timeLeft is not None:
                startTimeLeft = timeLeft[0]
                timeStatusText = text_styles.standard(_ms('#quests:missionDetails/status/notAvailable/%s' % errorMsg, time=self._getTillTimeString(startTimeLeft)))
                dateLabel = text_styles.concatStylesWithSpace(clockIcon, text_styles.error(QUESTS.MISSIONDETAILS_STATUS_WRONGTIME), timeStatusText)
            if errorMsg in ('invalid_weekday', 'invalid_time_interval'):
                scheduleLabel = getScheduleLabel()
                scheduleTooltip = getInvalidTimeIntervalsTooltip(self.event)
        return {'status': EVENT_STATUS.NOT_AVAILABLE,
         'dateLabel': dateLabel,
         'scheduleOrResetLabel': scheduleLabel,
         'scheduleTooltip': scheduleTooltip}

    def _getRegularStatusFields(self, isLimited, bonusCount, bonusLimit):
        """
        Gets status fields data for regular mission state.
        Data used in detailed mission view to display its regular state.
        """
        scheduleOrResetLabel = ''
        scheduleTooltip = None
        if isLimited:
            isDaily = self.event.bonusCond.isDaily()
            statusLabel = text_styles.concatStylesWithSpace(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_INPROGRESSICON, 16, 16, -2, 8), text_styles.standard(_ms(_getDailyLimitedStatusKey(isDaily), count=text_styles.stats(bonusCount), total=text_styles.standard(bonusLimit))))
            statusTooltipData = getBonusLimitTooltip(bonusCount, bonusLimit, isDaily)
        else:
            statusTooltipData = getCompletetBonusLimitValueTooltip(self.event.getBonusCount())
            statusLabel = text_styles.concatStylesWithSpace(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_INPROGRESSICON, 16, 16, -2, 8), text_styles.standard(_ms(QUESTS.MISSIONDETAILS_MISSIONSCOMPLETECOUNTER, count=text_styles.stats(self.event.getBonusCount()))))
        if self.event.getWeekDays() or self.event.getActiveTimeIntervals():
            scheduleOrResetLabel = getScheduleLabel()
            scheduleTooltip = getInvalidTimeIntervalsTooltip(self.event)
        elif self.event.bonusCond.isDaily():
            scheduleOrResetLabel = self._getDailyResetStatusLabel()
        return {'statusLabel': statusLabel,
         'status': EVENT_STATUS.NONE,
         'statusTooltipData': statusTooltipData,
         'dateLabel': self._getActiveTimeDateLabel(),
         'scheduleOrResetLabel': scheduleOrResetLabel,
         'scheduleTooltip': scheduleTooltip}

    def _getActiveTimeDateLabel(self):
        """
        Gets formatted mission's active time
        """
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
        """
        Gets formatted conditions to display in GUI.
        detailedCardCondFormatter formatter has logic to control condition representation and scale.
        """
        return detailedCardCondFormatter.format(self.event)

    def _getPrebattleConditions(self):
        """
        Gets formatted prebattle conditions to display in GUI.
        Prebattle conditions are placed under main conditions in GUI
        has horizontal layout and looks like label with icon.
        """
        return preBattleConditionFormatter.format(self.event.preBattleCond, self.event)

    def _getAccountRequirements(self):
        """
        Gets formatted account requirements list to display in GUI.
        account requirements are placed under header in mission detailed view
        Shows completed and not available requirements in GUI to complete mission.
        """
        return accountReqsFormatter.format(self.event.accountReqs, self.event)

    def _getAwards(self, mainQuest=None):
        """
        Gets formatted awards list to display on awards ribbon in GUI.
        detailedCardAwardsFormatter formatter has logic to control awards scale.
        """
        return detailedCardAwardsFormatter.getFormattedBonuses(self._substituteBonuses(mainQuest))

    def _getTitle(self, title):
        return text_styles.promoSubTitle(title)

    def __getDescription(self):
        description = self.event.getDescription()
        return None if not description else makeTooltip(QUESTS.MISSIONDETAILS_DESCRIPTION, description)


class _DetailedPersonalMissionInfo(_DetailedMissionInfo, _PersonalMissionInfo):

    def _getRegularStatusFields(self, isLimited, bonusCount, bonusLimit):
        statusData = super(_DetailedPersonalMissionInfo, self)._getRegularStatusFields(isLimited, bonusCount, bonusLimit)
        return self._getUpdatedByTokenStatusData(statusData, bonusCount, bonusLimit)

    @classmethod
    def _getPersonalDailyStatusLabel(cls, statusLabel, bonusLimit, bonusCount):
        text = _ms(QUESTS.MISSIONDETAILS_PERSONALQUEST_DETAILS_COMPLETE_LEFT_DAILY, count=text_styles.stats(max(bonusLimit - bonusCount, 0)))
        return text_styles.standard('%s (%s)' % (statusLabel, text_styles.standard(text)))


class _DetailedTokenMissionInfo(_DetailedMissionInfo):

    def getVehicleRequirementsCriteria(self):
        """ Token quest lacks of vehicles requirements.
        """
        return (None, [])

    def _getMainConditions(self):
        return detailedCardTokenConditionFormatter.format(self.event)

    def _getAccountRequirements(self):
        return tqAccountReqsFormatter.format(self.event.accountReqs, self.event)

    def _getRegularStatusFields(self, isLimited, bonusCount, bonusLimit):
        statusData = super(_DetailedTokenMissionInfo, self)._getRegularStatusFields(isLimited, bonusCount, bonusLimit)
        statusLabel = statusData.get('bottomStatusText', '') or self.__getTokensCount()
        statusData.update({'bottomStatusText': statusLabel})
        return statusData

    def __getTokensCount(self):
        tokens = detailedCardTokenConditionFormatter.getPreformattedConditions(self.event)
        needCount = 0
        gotCount = 0
        for tokenData in tokens:
            tokenNeedCount = tokenData.needCount
            needCount += tokenNeedCount
            gotCount += min(tokenData.gotCount, tokenNeedCount)

        return text_styles.middleTitle(_ms(QUESTS.MISSIONDETAILS_BOTTOMSTATUSTOKENS, count=gotCount, total=needCount)) if needCount or gotCount else ''


def getMissionInfoData(event):
    if event.getType() == constants.EVENT_TYPE.TOKEN_QUEST:
        return _TokenMissionInfo(event)
    elif event.getType() == constants.EVENT_TYPE.PERSONAL_QUEST:
        return _PersonalMissionInfo(event)
    else:
        return _MissionInfo(event) if event.getType() in constants.EVENT_TYPE.LIKE_BATTLE_QUESTS else None


def getDetailedMissionData(event):
    if event.getType() == constants.EVENT_TYPE.TOKEN_QUEST:
        return _DetailedTokenMissionInfo(event)
    elif event.getType() == constants.EVENT_TYPE.PERSONAL_QUEST:
        return _DetailedPersonalMissionInfo(event)
    else:
        return _DetailedMissionInfo(event) if event.getType() in constants.EVENT_TYPE.LIKE_BATTLE_QUESTS else None


def getAwardsWindowBonuses(bonuses):
    result = AwardsWindowBonusFormatter.getFormattedBonuses(bonuses)
    while len(result) % AWARDS_PER_PAGE != 0 and len(result) > AWARDS_PER_SINGLE_PAGE:
        result.append({})

    return result
