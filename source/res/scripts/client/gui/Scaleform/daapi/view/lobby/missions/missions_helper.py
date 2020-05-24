# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/missions_helper.py
import operator
import time
from collections import namedtuple
import constants
from debug_utils import LOG_WARNING
from gui.ranked_battles.ranked_helpers import isRankedQuestID
from gui.Scaleform.daapi.view.lobby.missions import cards_formatters
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer, AwardsWindowComposer, DetailedCardAwardComposer, PersonalMissionsAwardComposer, LinkedSetAwardsComposer
from gui.Scaleform.daapi.view.lobby.server_events.events_helpers import getChainVehTypeAndLevelRestrictions
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_BUTTONS import PERSONAL_MISSIONS_BUTTONS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.awards_formatters import AWARDS_SIZES, getEpicAwardFormatter, EPIC_AWARD_SIZE
from gui.server_events.bonuses import SimpleBonus
from gui.server_events.cond_formatters.prebattle import MissionsPreBattleConditionsFormatter
from gui.server_events.cond_formatters.requirements import AccountRequirementsFormatter, TQAccountRequirementsFormatter
from gui.server_events.conditions import GROUP_TYPE
from gui.server_events.events_constants import FRONTLINE_GROUP_ID
from gui.server_events.events_helpers import MISSIONS_STATES, QuestInfoModel, AWARDS_PER_SINGLE_PAGE, isMarathon, AwardSheetPresenter, isPremium
from gui.server_events.formatters import DECORATION_SIZES
from gui.server_events.personal_progress import formatters
from gui.shared.formatters import text_styles, icons, time_formatters
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency, int2roman, time_utils, i18n
from helpers.i18n import makeString as _ms
from personal_missions import PM_BRANCH
from potapov_quests import PM_BRANCH_TO_FREE_TOKEN_NAME
from quest_xml_source import MAX_BONUS_LIMIT
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IEventProgressionController, IEpicBattleMetaGameController, IRankedBattlesController
CARD_AWARDS_COUNT = 6
CARD_AWARDS_BIG_COUNT = 5
CARD_AWARDS_EPIC_COUNT = 2
LINKED_SET_CARD_AWARDS_COUNT = 8
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
_awardsWindowBonusFormatter = AwardsWindowComposer(CARD_AWARDS_BIG_COUNT)
_epicAwardsWindowBonusFormatter = CurtailingAwardsComposer(CARD_AWARDS_EPIC_COUNT, getEpicAwardFormatter())
_personalMissionsAwardsFormatter = PersonalMissionsAwardComposer(DETAILED_CARD_AWARDS_COUNT)
_linkedSetAwardsComposer = LinkedSetAwardsComposer(LINKED_SET_CARD_AWARDS_COUNT)
HIDE_DONE = 'hideDone'
HIDE_UNAVAILABLE = 'hideUnavailable'
PostponedOperationState = namedtuple('PostponedOperationState', ['state', 'postponeTime'])

def getHtmlAwardSheetIcon(branch=None):
    return icons.makeImageTag(AwardSheetPresenter.getIcon(AwardSheetPresenter.Size.X_16, branch), 16, 16, -3, 0)


class BG_STATES(object):
    COMPLETED = 'completed'
    NOT_AVAILABLE = 'notAvailable'
    MARATHON = 'marathon'
    DISABLED = 'disabled'
    DEFAULT = 'default'
    IN_PROGRESS = 'inProgress'


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


def getOperations(branch, currOperationID):
    _eventsCache = dependency.instance(IEventsCache)
    operations = []
    for oID, o in sorted(_eventsCache.getPersonalMissions().getOperationsForBranch(branch).iteritems(), key=operator.itemgetter(0)):
        state = PERSONAL_MISSIONS_ALIASES.OPERATION_UNLOCKED_STATE
        descr = text_styles.stats(PERSONAL_MISSIONS.OPERATIONS_UNLOCKED_DESC)
        title = text_styles.highTitle(o.getShortUserName())
        if o.isDisabled():
            state, _ = getPostponedOperationState(oID)
            descr = text_styles.error(PERSONAL_MISSIONS.OPERATIONS_LOCKED_DESC)
        elif not o.isUnlocked():
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
            freeSheetIcon = AwardSheetPresenter.getIcon(AwardSheetPresenter.Size.X_16, o.getBranch())
            freeSheetCounter = text_styles.counter('x%d' % tokensPawned)
        if state == PERSONAL_MISSIONS_ALIASES.OPERATION_POSTPONED_STATE:
            tooltipAlias = TOOLTIPS_CONSTANTS.OPERATION_POSTPONED
        else:
            tooltipAlias = TOOLTIPS_CONSTANTS.OPERATION
        operationVO = {'title': title,
         'desc': descr,
         'iconSource': RES_ICONS.getPersonalMissionOperationImage(oID),
         'iconStateSource': iconStateSource,
         'freeSheetIconSource': freeSheetIcon,
         'freeSheetCounter': freeSheetCounter,
         'state': state,
         'isSelected': oID == currOperationID,
         'id': oID,
         'tooltipAlias': tooltipAlias}
        operations.append(operationVO)

    return operations


def getPostponedOperationState(operationID):
    _eventsCache = dependency.instance(IEventsCache)
    disabledOperations = _eventsCache.getPersonalMissions().getDisabledPMOperations()
    state = None
    postponeTime = ''
    if operationID in disabledOperations:
        timestamp = disabledOperations[operationID]
        state = PERSONAL_MISSIONS_ALIASES.OPERATION_DISABLED_STATE
        if timestamp:
            state = PERSONAL_MISSIONS_ALIASES.OPERATION_POSTPONED_STATE
            timeLeft = time_utils.getTimeDeltaFromNowInLocal(timestamp)
            if timeLeft <= time_utils.ONE_DAY:
                postponeTime = PERSONAL_MISSIONS.OPERATIONINFO_OPERATIONBTN_POSTPONED_LESSTHANDAY
            else:
                days = int(timeLeft / time_utils.ONE_DAY)
                postponeTime = i18n.makeString(PERSONAL_MISSIONS.OPERATIONINFO_OPERATIONBTN_POSTPONED_DAYS, days=days)
    return PostponedOperationState(state, postponeTime)


@dependency.replace_none_kwargs(epicMetaGameCtrl=IEpicBattleMetaGameController)
def isEpicDailyQuestsRefreshAvailable(epicMetaGameCtrl=None):
    dayTimeLeft = time_utils.getDayTimeLeft()
    cycleTimeLeft = epicMetaGameCtrl.getCurrentCycleTimeLeft()
    currentPrimeTimeEnd = epicMetaGameCtrl.getCurrentPrimeTimeEnd()
    if currentPrimeTimeEnd is None:
        return False
    else:
        primeTimeTimeLeft = currentPrimeTimeEnd - time_utils.getCurrentLocalServerTimestamp()
        return (epicMetaGameCtrl.hasPrimeTimesLeft() or primeTimeTimeLeft > dayTimeLeft) and cycleTimeLeft > dayTimeLeft


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _isPremiumEnabled(itemsCache=None):
    return itemsCache.items.stats.isActivePremium(constants.PREMIUM_TYPE.PLUS)


def _getDailyLimitedStatusKey(isDaily):
    return QUESTS.MISSIONDETAILS_MISSIONSCOMPLETE_DAILY if isDaily else QUESTS.MISSIONDETAILS_MISSIONSCOMPLETE


def _getClockIconTag():
    clockIcon = backport.image(R.images.gui.maps.icons.library.timerIcon())
    return icons.makeImageTag(clockIcon, 16, 16, -2, 8)


def _getNotAvailableIconTag():
    notAvailableIcon = backport.image(R.images.gui.maps.icons.library.marker_blocked())
    return icons.makeImageTag(notAvailableIcon, 14, 14, -2, 10)


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
         'title': self._getTitle(self._getEventTitle()),
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

    def _getEventTitle(self):
        return self.event.getUserName()

    def _getUIDecoration(self):
        return self.eventsCache.prefetcher.getMissionDecoration(self.event.getIconID(), DECORATION_SIZES.CARDS)

    def _getMissionDurationTooltipData(self):
        header = _ms(TOOLTIPS.QUESTS_UNAVAILABLE_TIME_STATUSTOOLTIP)
        body = _ms(QUESTS.MISSIONS_TAB_MARATHONS_HEADER_PERIOD, startDate=backport.getLongDateFormat(self.event.getStartTime()), endDate=backport.getLongDateFormat(self.event.getFinishTime()))
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
            clockIcon = _getClockIconTag()
            statusText = _ms(QUESTS.MISSIONDETAILS_STATUS_NOTAVAILABLE)
            statusLabel = text_styles.concatStylesWithSpace(clockIcon, text_styles.error(statusText))
            statusTooltipData = {'tooltip': makeTooltip(_ms(self._getCompleteStatusTooltipHeader()), self._getCompleteDailyStatus(self._getCompleteKey())),
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

    def _getCompleteKey(self):
        return backport.text(R.strings.quests.missionDetails.status.completed.daily())

    def _getCompleteStatusTooltipHeader(self):
        return backport.text(R.strings.tooltips.quests.unavailable.time.statusTooltip())

    def _getUnavailableStatusFields(self, errorMsg):
        if errorMsg == 'requirements':
            vehicleReqs = self.event.vehicleReqs
            isVehAvailable = vehicleReqs.isAnyVehicleAcceptable() or vehicleReqs.getSuitableVehicles()
            if not isVehAvailable:
                statusText = _ms(QUESTS.MISSIONDETAILS_STATUS_WRONGVEHICLE)
            else:
                statusText = _ms(QUESTS.MISSIONDETAILS_STATUS_NOTAVAILABLE)
            notAvailableIcon = _getNotAvailableIconTag()
            statusMsg = text_styles.concatStylesWithSpace(notAvailableIcon, text_styles.error(statusText))
            tooltipData = getDisabledRequirementTooltip(self.event)
        else:
            clockIcon = _getClockIconTag()
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
        bonuses = self.event.getBonuses()
        substitutes = []
        for bonus in bonuses:
            if bonus.getName() == 'customizations':
                bonuses.remove(bonus)
                substitutes.extend(bonus.compensation())

        if substitutes:
            bonuses.extend(substitutes)
        if not self.event.isCompensationPossible():
            return bonuses
        else:
            if mainQuest is None:
                mainQuest = first(self.eventsCache.getQuests(lambda q: isMarathon(q.getID()) and q.getGroupID() == self.event.getGroupID()).values())
            if mainQuest:
                toCompensate = [ token.getID() for token in mainQuest.accountReqs.getTokens() if token.isAvailable() ]
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
            return bonuses
            return


class _EpicDailyMissionInfo(_MissionInfo):
    _epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def _getCompleteDailyStatus(self, completeKey):
        season = self._epicMetaGameCtrl.getCurrentSeason() or self._epicMetaGameCtrl.getNextSeason()
        cycle = season.getCycleInfo()
        dayTimeLeft = time_utils.getDayTimeLeft()
        cycleTimeLeft = self._epicMetaGameCtrl.getCurrentCycleTimeLeft()
        if isEpicDailyQuestsRefreshAvailable():
            timeLeftString = i18n.makeString(completeKey, time=self._getTillTimeString(dayTimeLeft))
        else:
            if cycleTimeLeft < time_utils.ONE_DAY:
                timeLeft = backport.text(R.strings.epic_battle.questsTooltip.epicBattle.lessThanDay())
            else:
                timeLeft = time_formatters.getTillTimeByResource(cycleTimeLeft, R.strings.menu.headerButtons.battle.types.ranked.availability, removeLeadingZeros=True)
            timeLeftString = i18n.makeString(completeKey, cycle=int2roman(cycle.ordinalNumber), time=timeLeft)
        return timeLeftString

    def _getCompleteStatusTooltipHeader(self):
        return QUESTS.MISSIONDETAILS_STATUS_NOTAVAILABLE if not isEpicDailyQuestsRefreshAvailable() else super(_EpicDailyMissionInfo, self)._getCompleteStatusTooltipHeader()

    def _getCompleteKey(self):
        return EPIC_BATTLE.QUESTSTOOLTIP_EPICBATTLE_TIMELEFT if not isEpicDailyQuestsRefreshAvailable() else super(_EpicDailyMissionInfo, self)._getCompleteKey()


class _RankedMissionInfo(_MissionInfo):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def _getCompleteStatusFields(self, isLimited, bonusCount, bonusLimit):
        return self.__getRankedUnavailableStatusFields() if self.event.bonusCond.isDaily() and not self.__rankedController.hasPrimeTimesNextDayLeft() else super(_RankedMissionInfo, self)._getCompleteStatusFields(isLimited, bonusCount, bonusLimit)

    def _getUnavailableStatusFields(self, errorMsg):
        isLeagues = self.__rankedController.isAccountMastered()
        isAnyPrimeNow = self.__rankedController.hasAvailablePrimeTimeServers()
        isAnyPrimeLeftTotal = self.__rankedController.hasPrimeTimesTotalLeft()
        if not isLeagues or not isAnyPrimeLeftTotal:
            return self.__getRankedUnavailableStatusFields()
        return self.__getRankedUnavailableStatusFields(True) if not isAnyPrimeNow else super(_RankedMissionInfo, self)._getUnavailableStatusFields(errorMsg)

    def _getRegularStatusFields(self, isLimited, bonusCount, bonusLimit):
        if not self.__rankedController.hasPrimeTimesTotalLeft():
            return self.__getRankedUnavailableStatusFields()
        return self.__getRankedUnavailableStatusFields(True) if not self.__rankedController.hasAvailablePrimeTimeServers() else super(_RankedMissionInfo, self)._getRegularStatusFields(isLimited, bonusCount, bonusLimit)

    def __getRankedUnavailableStatusFields(self, isTemporary=False):
        return {'statusLabel': text_styles.concatStylesWithSpace(_getClockIconTag() if isTemporary else _getNotAvailableIconTag(), text_styles.error(backport.text(R.strings.quests.missionDetails.status.notAvailable()))),
         'status': MISSIONS_STATES.NOT_AVAILABLE,
         'statusTooltipData': getDisabledRequirementTooltip(self.event)}


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


class _PremiumMissionInfo(_MissionInfo):

    def _getUIDecoration(self):
        return backport.image(R.images.gui.maps.icons.missions.decorations.premium_482x222())

    def _getCompleteStatusFields(self, isLimited, bonusCount, bonusLimit):
        status = MISSIONS_STATES.COMPLETED
        if isLimited and bonusLimit > 1:
            statusLabel = text_styles.bonusAppliedText(_ms(QUESTS.MISSIONDETAILS_MISSIONSCOMPLETE, count=text_styles.bonusAppliedText(bonusCount), total=text_styles.standard(bonusLimit)))
        else:
            progressDesc = text_styles.bonusAppliedText(_ms(QUESTS.QUESTS_STATUS_DONE))
            icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OKICON, 16, 16, -2, 8)
            statusLabel = text_styles.concatStylesToSingleLine(icon, progressDesc)
        return {'statusLabel': statusLabel,
         'status': status}

    def _getUnavailableStatusFields(self, errorMsg):
        if errorMsg == 'requirements':
            vehicleReqs = self.event.vehicleReqs
            isVehAvailable = vehicleReqs.isAnyVehicleAcceptable() or vehicleReqs.getSuitableVehicles()
            if not isVehAvailable:
                statusText = _ms(QUESTS.MISSIONDETAILS_STATUS_WRONGVEHICLE)
            else:
                statusText = _ms(QUESTS.MISSIONDETAILS_STATUS_NOTAVAILABLE)
            notAvailableIcon = _getNotAvailableIconTag()
            statusMsg = text_styles.concatStylesWithSpace(notAvailableIcon, text_styles.error(statusText))
        else:
            clockIcon = _getClockIconTag()
            statusMsg = text_styles.concatStylesWithSpace(clockIcon, text_styles.error(QUESTS.MISSIONDETAILS_STATUS_NOTAVAILABLE))
        return {'statusLabel': statusMsg,
         'status': MISSIONS_STATES.NOT_AVAILABLE}

    def _getRegularStatusFields(self, isLimited, bonusCount, bonusLimit):
        statusLabel = text_styles.concatStylesWithSpace(icons.inProgress(), text_styles.neutral(backport.text(R.strings.quests.personalMission.status.inProgress())))
        return {'statusLabel': statusLabel,
         'status': MISSIONS_STATES.NONE}


class _DetailedMissionInfo(_MissionInfo):
    __AWARDS_COUNT = 6
    __eventProgressionController = dependency.descriptor(IEventProgressionController)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

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
        battleCond = self.event.preBattleCond.getConditions()
        if battleCond:
            bonusTypes = battleCond.find('bonusTypes')
            if bonusTypes:
                arenaTypes = bonusTypes.getValue()
                if arenaTypes:
                    if constants.ARENA_BONUS_TYPE.EVENT_BATTLES not in arenaTypes or constants.ARENA_BONUS_TYPE.EVENT_BATTLES_2 not in arenaTypes:
                        criteria = criteria | ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
                    if constants.ARENA_BONUS_TYPE.EPIC_BATTLE not in arenaTypes:
                        criteria = criteria | ~REQ_CRITERIA.VEHICLE.EPIC_BATTLE
        xpMultCond = conds.find('hasReceivedMultipliedXP')
        if xpMultCond:
            extraConditions.append(xpMultCond)
        return (criteria, extraConditions)

    def _getUIDecoration(self):
        decoration = self.eventsCache.prefetcher.getMissionDecoration(self.event.getIconID(), DECORATION_SIZES.DETAILS)
        return decoration if decoration else RES_ICONS.MAPS_ICONS_QUESTS_DECORATIONS_DEFAULT_750X264

    def _getInfo(self, statusData, isAvailable, errorMsg, mainQuest=None):
        data = super(_DetailedMissionInfo, self)._getInfo(statusData, isAvailable, errorMsg, mainQuest)
        resetDateLabel = statusData.get('scheduleOrResetLabel', '')
        statusLabel = statusData.get('statusLabel', '')
        if 'eventID' in data:
            if data['eventID'] in self.__eventProgressionController.questIDs and not isAvailable:
                _, level, _ = self.__epicController.getPlayerLevelInfo()
                maxLevel = self.__epicController.getMaxPlayerLevel()
                if level < maxLevel:
                    iconSrc = backport.image(R.images.gui.maps.icons.library.marker_blocked())
                    notAvailableIcon = icons.makeImageTag(source=iconSrc, width=14, height=14, vSpace=-2, hSpace=10)
                    statusText = backport.text(R.strings.quests.missionDetails.status.notAvailable())
                    statusLabel = text_styles.concatStylesWithSpace(notAvailableIcon, text_styles.error(statusText))
                    resetDateLabel = text_styles.main(backport.text(R.strings.event_progression.questsCard.frontLine.getLevel(), level=maxLevel))
        data.update({'statusLabel': statusLabel,
         'resetDateLabel': resetDateLabel,
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
            dateLabel = self._getCompletedDateLabel()
            resetDateLabel = self._getDailyResetStatusLabel()
        return {'statusLabel': statusLabel,
         'dateLabel': dateLabel,
         'status': status,
         'bottomStatusText': text_styles.concatStylesWithSpace(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_DONE, 32, 32, -8), text_styles.missionStatusAvailable(QUESTS.MISSIONDETAILS_BOTTOMSTATUSCOMPLETE)),
         'statusTooltipData': statusTooltipData,
         'resetDateLabel': resetDateLabel}

    def _getCompletedDateLabel(self):
        dateLabel = text_styles.concatStylesWithSpace(_getClockIconTag(), text_styles.error(QUESTS.MISSIONDETAILS_STATUS_NOTAVAILABLE), self._getCompleteDailyStatus(QUESTS.MISSIONDETAILS_STATUS_COMPLETED_DAILY))
        return dateLabel

    def _getUnavailableStatusFields(self, errorMsg):
        result = {'status': MISSIONS_STATES.NOT_AVAILABLE}
        if errorMsg != 'requirement':
            timeLeft = self.event.getNearestActivityTimeLeft()
            if timeLeft is not None:
                clockIcon = _getClockIconTag()
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


class _EpicDetailedMissionInfo(_DetailedMissionInfo, _EpicDailyMissionInfo):

    def _getCompletedDateLabel(self):
        dateLabel = text_styles.concatStylesWithSpace(_getClockIconTag(), text_styles.error(QUESTS.MISSIONDETAILS_STATUS_NOTAVAILABLE), self._getCompleteDailyStatus(self._getCompleteKey()))
        return dateLabel

    def _getDailyResetStatusLabel(self):
        if not isEpicDailyQuestsRefreshAvailable():
            dailyStr = self._getCompleteDailyStatus(self._getCompleteKey())
            if dailyStr:
                clockIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_RENT_ICO_BIG, 19, 19, -4, 8)
                return text_styles.concatStylesToSingleLine(clockIcon, dailyStr)
        else:
            dailyStr = super(_EpicDetailedMissionInfo, self)._getDailyResetStatusLabel()
        return dailyStr


class _RankedDetailedMissionInfo(_DetailedMissionInfo):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def _getInfo(self, statusData, isAvailable, errorMsg, mainQuest=None):
        data = super(_RankedDetailedMissionInfo, self)._getInfo(statusData, isAvailable, errorMsg, mainQuest)
        updateDict = {}
        isDaily = self.event.bonusCond.isDaily()
        isCompleted = self.event.isCompleted()
        isLeagues = self.__rankedController.isAccountMastered()
        isAnyPrimeNow = self.__rankedController.hasAvailablePrimeTimeServers()
        isAnyPrimeLeftTotal = self.__rankedController.hasPrimeTimesTotalLeft()
        isAnyPrimeLeftNextDay = self.__rankedController.hasPrimeTimesNextDayLeft()
        if isDaily and isCompleted and not isAnyPrimeLeftNextDay:
            updateDict['dateLabel'] = self.__getDateLabel(self.__getSeasonEndLabel())
        elif not isAnyPrimeLeftTotal and not isCompleted:
            updateDict['dateLabel'] = self.__getDateLabel(self.__getSeasonEndLabel())
            updateDict['resetDateLabel'] = ''
        elif not isLeagues:
            statusLabel = text_styles.error(backport.text(R.strings.quests.missionDetails.status.notAvailable()))
            updateDict['statusLabel'] = text_styles.concatStylesWithSpace(_getNotAvailableIconTag(), statusLabel)
            updateDict['resetDateLabel'] = backport.text(R.strings.ranked_battles.quests.detailed.notInLeagues())
        elif not isAnyPrimeNow and not isCompleted:
            dateStr = backport.text(R.strings.ranked_battles.quests.detailed.allServersPrime())
            updateDict['dateLabel'] = self.__getDateLabel(dateStr, True)
        if updateDict:
            updateDict['scheduleTooltip'] = None
            updateDict['statusTooltipData'] = None
            updateDict['status'] = MISSIONS_STATES.NOT_AVAILABLE
            data.update(updateDict)
        return data

    def __getSeasonEndLabel(self):
        season = self.__rankedController.getCurrentSeason()
        label = backport.text(R.strings.ranked_battles.quests.detailed.seasonEnd.default())
        if season is not None:
            seasonEnd = time_utils.getTimeDeltaFromNowInLocal(time_utils.makeLocalServerTime(season.getEndDate()))
            label = backport.getTillTimeStringByRClass(seasonEnd, R.strings.ranked_battles.quests.detailed.seasonEnd)
        return label

    def __getDateLabel(self, text, isTemporary=False):
        imageTag = _getClockIconTag() if isTemporary else _getNotAvailableIconTag()
        statusText = backport.text(R.strings.ranked_battles.quests.detailed.unavailableLabel())
        return text_styles.concatStylesWithSpace(imageTag, text_styles.error(statusText), text)


class _PremiumDetailedMissionInfo(_DetailedMissionInfo):

    def _getUIDecoration(self):
        return backport.image(R.images.gui.maps.icons.quests.decorations.premium_750x264())

    def _getConditions(self):
        conditions = {'prebattleConditions': self._getPrebattleConditions(),
         'battleConditions': self._getMainConditions()}
        return conditions

    def _getStatusFields(self, isAvailable, errorMsg):
        bonusLimit = self.event.bonusCond.getBonusLimit()
        bonusCount = min(self.event.getBonusCount(), bonusLimit)
        isLimited = self._isLimited()
        if self.event.isCompleted():
            return self._getCompleteStatusFields(isLimited, bonusCount, bonusLimit)
        return self._getUnavailableStatusFields(errorMsg) if not isAvailable else self._getRegularStatusFields(isLimited, bonusCount, bonusLimit)

    def _getUnavailableStatusFields(self, errorMsg):
        dateLabel = self.getDateLabel()
        addStatusMsg = ''
        if errorMsg == 'requirements':
            vehicleReqs = self.event.vehicleReqs
            isVehAvailable = vehicleReqs.isAnyVehicleAcceptable() or vehicleReqs.getSuitableVehicles()
            if not isVehAvailable:
                statusText = _ms(QUESTS.MISSIONDETAILS_STATUS_WRONGVEHICLE)
            else:
                statusText = _ms(QUESTS.MISSIONDETAILS_STATUS_NOTAVAILABLE)
                isPremEnabled = _isPremiumEnabled()
                if not isPremEnabled:
                    addStatusMsg = backport.text(R.strings.quests.premiumQuests.detailedQuests.requirements.premiumAccount())
                else:
                    addStatusMsg = backport.text(R.strings.quests.premiumQuests.detailedQuests.requirements.token())
            notAvailableIcon = _getNotAvailableIconTag()
            statusMsg = text_styles.concatStylesWithSpace(notAvailableIcon, text_styles.error(statusText))
        else:
            clockIcon = _getClockIconTag()
            statusMsg = text_styles.concatStylesWithSpace(clockIcon, text_styles.error(QUESTS.MISSIONDETAILS_STATUS_NOTAVAILABLE))
        return {'statusLabel': statusMsg,
         'status': MISSIONS_STATES.NOT_AVAILABLE,
         'dateLabel': dateLabel,
         'scheduleOrResetLabel': text_styles.neutral(addStatusMsg)}

    def _getCompleteStatusFields(self, isLimited, bonusCount, bonusLimit):
        statusTooltipData = None
        status = MISSIONS_STATES.COMPLETED
        if isLimited and bonusLimit > 1:
            statusLabel = text_styles.bonusAppliedText(_ms(QUESTS.MISSIONDETAILS_MISSIONSCOMPLETE, count=text_styles.bonusAppliedText(bonusCount), total=text_styles.standard(bonusLimit)))
            statusTooltipData = getCompletetBonusLimitTooltip()
        else:
            progressDesc = text_styles.bonusAppliedText(_ms(QUESTS.QUESTS_STATUS_DONE))
            icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OKICON, 16, 16, -2, 8)
            statusLabel = text_styles.concatStylesToSingleLine(icon, progressDesc)
        return {'statusLabel': statusLabel,
         'status': status,
         'bottomStatusText': text_styles.concatStylesWithSpace(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_DONE, 32, 32, -8), text_styles.missionStatusAvailable(QUESTS.MISSIONDETAILS_BOTTOMSTATUSCOMPLETE)),
         'statusTooltipData': statusTooltipData}

    def _getRegularStatusFields(self, isLimited, bonusCount, bonusLimit):
        dateLabel = self.getDateLabel()
        statusLabel = text_styles.concatStylesWithSpace(icons.inProgress(), text_styles.neutral(backport.text(R.strings.quests.personalMission.status.inProgress())))
        return {'statusLabel': statusLabel,
         'status': MISSIONS_STATES.NONE,
         'dateLabel': dateLabel}

    def getDateLabel(self):
        deltaTime = max(time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay(), 0)
        gmtime = time.gmtime(deltaTime)
        if deltaTime >= time_utils.ONE_HOUR:
            fmt = R.strings.quests.item.timer.tillFinish.longFullFormat()
            return backport.text(fmt, hours=time.strftime('%H', gmtime))
        fmt = R.strings.quests.item.timer.tillFinish.longFullFormatMin()
        return backport.text(fmt, minutes=time.strftime('%M', gmtime))

    def _getBackGround(self, status):
        if status == MISSIONS_STATES.COMPLETED:
            return BG_STATES.COMPLETED
        if status == MISSIONS_STATES.NOT_AVAILABLE:
            return BG_STATES.NOT_AVAILABLE
        return BG_STATES.MARATHON if isMarathon(self.event.getGroupID()) else BG_STATES.DEFAULT


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
    _eventsCache = dependency.descriptor(IEventsCache)
    DISCARDABLE_OPERATIONS_IDS = (7,)
    PAUSABLE_OPERATIONS_IDS = (7,)

    def __init__(self, event):
        super(_DetailedPersonalMissionInfo, self).__init__(event)
        self.__anyConditions = False

    def getVehicleRequirementsCriteria(self):
        extraConditions = []
        criteria = REQ_CRITERIA.INVENTORY
        criteria |= REQ_CRITERIA.VEHICLE.LEVELS(range(self.event.getVehMinLevel(), constants.MAX_VEHICLE_LEVEL + 1))
        criteria |= REQ_CRITERIA.VEHICLE.CLASSES(self.event.getQuestClassifier().classificationAttr)
        return (criteria, extraConditions)

    def getAwardScreenConditionsFormatter(self):
        return formatters.PMAwardScreenConditionsFormatter(self.event)

    def getAwards(self, extended=False):
        return self._getAwards(extended=extended)

    def _getStatusFields(self, isAvailable, errorMsg):
        quest = self.event
        statusTooltipData = None
        if not isAvailable:
            return self._getUnavailableStatusFields(errorMsg)
        elif quest.isFullCompleted():
            return self._getFullCompleteStatusFields()
        elif quest.isInProgress():
            return self._getProgressStatusFields()
        elif quest.isCompleted():
            return self._getCompleteStatusFields()
        else:
            statusLabel = None
            status = MISSIONS_STATES.NONE
            addBottomStatusText = self.__getAddBottomInfo()
            showIcon = False
            return {'showIcon': showIcon,
             'addBottomStatusText': addBottomStatusText,
             'statusLabel': statusLabel,
             'status': status,
             'statusTooltipData': statusTooltipData}

    def _getUnavailableStatusFields(self, errorMsg):
        if errorMsg == 'noVehicle':
            return self._getNoVehicleStatusFields()
        return self._getDisabledStatusFields() if errorMsg == 'disabled' else self._getUnlockedStatusFields()

    def _getDisabledStatusFields(self):
        statusLabel = text_styles.error(QUESTS.PERSONALMISSION_STATUS_MISSIONDISABLED)
        return {'showIcon': True,
         'statusLabel': statusLabel,
         'status': MISSIONS_STATES.DISABLED}

    def _getNoVehicleStatusFields(self):
        addBottomStatusText = self.__getAddBottomLocked()
        bodyTooltip = TOOLTIPS.PERSONALMISSIONS_STATUS_LOCKEDBYVEHICLETYPE_BODY
        if self.event.getQuestBranch() == PM_BRANCH.PERSONAL_MISSION_2:
            bodyTooltip = TOOLTIPS.PERSONALMISSIONS_STATUS_LOCKEDBYVEHICLEALLIANCE_BODY
        bottomStatusTooltipData = {'tooltip': makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_LOCKEDBYVEHICLE_HEADER, body=_ms(bodyTooltip, vehType=_ms(MENU.classesShort(self.event.getQuestClassifier().classificationAttr)), minLevel=int2roman(self.event.getVehMinLevel()), maxLevel=int2roman(self.event.getVehMaxLevel())))}
        if self.event.isInProgress():
            statusData = self._getProgressStatusFields()
            statusData.update(addBottomStatusText=addBottomStatusText)
            statusData.update(bottomStatusTooltipData=bottomStatusTooltipData)
            statusData.update(showIcon=True)
            return statusData
        if self.event.isMainCompleted():
            statusData = self._getCompleteStatusFields()
            statusData.update(addBottomStatusText=addBottomStatusText)
            statusData.update(bottomStatusTooltipData=bottomStatusTooltipData)
            statusData.update(showIcon=True)
            return statusData
        showIcon = True
        return {'showIcon': showIcon,
         'addBottomStatusText': addBottomStatusText,
         'status': MISSIONS_STATES.NOT_AVAILABLE,
         'bottomStatusTooltipData': bottomStatusTooltipData}

    def _getUnlockedStatusFields(self):
        quest = self.event
        operations = self._eventsCache.getPersonalMissions().getAllOperations()
        quests = self._eventsCache.getPersonalMissions().getAllQuests()
        operationID = quest.getOperationID()
        operation = operations.get(operationID)
        if not operation.isUnlocked():
            initialQuest = quests[first(operation.getInitialQuests().iterkeys())]
            pmType = initialQuest.getPMType()
            prevOperationID = max((quests[qId].getOperationID() for qId in pmType.requiredUnlocks))
            prevOperation = operations.get(prevOperationID)
            statusTooltipData = {'tooltip': makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_LOCKEDBYPREVOPERATION_HEADER, body=TOOLTIPS.PERSONALMISSIONS_STATUS_LOCKEDBYPREVOPERATION_BODY)}
            statusLabel = text_styles.error(_ms(QUESTS.PERSONALMISSION_STATUS_LOCKEDBYPREVOPERATION, prevCampaign=prevOperation.getShortUserName()))
        else:
            statusTooltipData = {'tooltip': makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_LOCKEDBYPREVMISSIONS_HEADER, body=TOOLTIPS.PERSONALMISSIONS_STATUS_LOCKEDBYPREVMISSIONS_BODY)}
            statusLabel = text_styles.error(QUESTS.PERSONALMISSION_STATUS_LOCKEDBYPREVMISSIONS)
        showIcon = False
        return {'showIcon': showIcon,
         'statusLabel': statusLabel,
         'status': MISSIONS_STATES.NOT_AVAILABLE,
         'statusTooltipData': statusTooltipData}

    def _getFullCompleteStatusFields(self):
        quest = self.event
        statusTooltipData = {'tooltip': makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_FULLDONE_HEADER, body=TOOLTIPS.PERSONALMISSIONS_STATUS_FULLDONE_BODY)}
        statusLabel = text_styles.bonusAppliedText(QUESTS.PERSONALMISSION_STATUS_FULLDONE)
        bottomStatusText = ''
        if quest.isDone():
            bottomStatusText = text_styles.missionStatusAvailable(QUESTS.PERSONALMISSION_BOTTOMSTATUS_ALLAWARDSRECEIVED)
        showIcon = False
        return {'showIcon': showIcon,
         'statusLabel': statusLabel,
         'status': MISSIONS_STATES.FULL_COMPLETED,
         'statusTooltipData': statusTooltipData,
         'bottomStatusText': bottomStatusText}

    def _getCompleteStatusFields(self, *args):
        quest = self.event
        addBottomStatusText = self.__getAddBottomInfo()
        if quest.areTokensPawned():
            statusTooltipData = {'tooltip': makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_DONEWITHPAWN_HEADER, body=TOOLTIPS.PERSONALMISSIONS_STATUS_DONEWITHPAWN_BODY)}
            count = text_styles.stats(str(quest.getPawnCost()) + getHtmlAwardSheetIcon(quest.getQuestBranch()))
            statusLabel = text_styles.bonusAppliedText(_ms(QUESTS.PERSONALMISSION_STATUS_DONEWITHPAWN, count=count))
        else:
            statusLabel = text_styles.bonusAppliedText(QUESTS.PERSONALMISSION_STATUS_MAINDONE)
            statusTooltipData = {'tooltip': makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_MAINDONE_HEADER, body=TOOLTIPS.PERSONALMISSIONS_STATUS_MAINDONE_BODY)}
        showIcon = False
        return {'showIcon': showIcon,
         'addBottomStatusText': addBottomStatusText,
         'statusLabel': statusLabel,
         'status': MISSIONS_STATES.COMPLETED,
         'statusTooltipData': statusTooltipData}

    def _getProgressStatusFields(self):
        quest = self.event
        addBottomStatusText = self.__getAddBottomInfo()
        status = MISSIONS_STATES.IN_PROGRESS
        if quest.isOnPause:
            status = MISSIONS_STATES.IS_ON_PAUSE
            statusLabel = text_styles.playerOnline(QUESTS.PERSONALMISSION_STATUS_ISONPAUSE)
            statusTooltipData = {'tooltip': TOOLTIPS.PERSONALMISSIONS_STATUS_ONPAUSE}
        elif quest.areTokensPawned():
            statusLabel = '%s %s' % (text_styles.neutral(QUESTS.PERSONALMISSION_STATUS_SHEETRECOVERYINPROGRESS), getHtmlAwardSheetIcon(quest.getQuestBranch()))
            statusTooltipData = {'tooltip': makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_SHEETRECOVERYINPROGRESS_HEADER, body=TOOLTIPS.PERSONALMISSIONS_STATUS_SHEETRECOVERYINPROGRESS_BODY)}
        elif quest.isMainCompleted() and not quest.isFullCompleted():
            statusLabel = text_styles.neutral(QUESTS.PERSONALMISSION_STATUS_ADDINPROGRESS)
            statusTooltipData = {'tooltip': makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_ADDINPROGRESS_HEADER, body=TOOLTIPS.PERSONALMISSIONS_STATUS_ADDINPROGRESS_BODY)}
        else:
            statusLabel = text_styles.neutral(PERSONAL_MISSIONS.DETAILEDVIEW_STATUS_INPROGRESS)
            statusTooltipData = {'tooltip': makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_INPROGRESS_HEADER, body=TOOLTIPS.PERSONALMISSIONS_STATUS_INPROGRESS_BODY)}
        showIcon = False
        return {'showIcon': showIcon,
         'statusLabel': statusLabel,
         'status': status,
         'statusTooltipData': statusTooltipData,
         'addBottomStatusText': addBottomStatusText}

    def _getEventID(self):
        return str(self.event.getID())

    def _getUIDecoration(self):
        if self.event.isFinal():
            tile = self.eventsCache.getPersonalMissions().getAllOperations().get(self.event.getOperationID())
            if tile:
                vehBonus = tile.getVehicleBonus()
                if vehBonus is not None:
                    return vehBonus.name
        return 'Empty'

    def _getBackGround(self, status):
        if status in (MISSIONS_STATES.COMPLETED, MISSIONS_STATES.FULL_COMPLETED):
            return BG_STATES.COMPLETED
        if status is MISSIONS_STATES.NOT_AVAILABLE:
            return BG_STATES.DISABLED
        return BG_STATES.IN_PROGRESS if status is MISSIONS_STATES.IN_PROGRESS else BG_STATES.DEFAULT

    def _getAwards(self, mainQuest=None, extended=False):
        pawnedTokensCount = self.event.getPawnCost() if self.event.areTokensPawned() else 0
        awards = _personalMissionsAwardsFormatter.getFormattedBonuses(self.event.getBonuses(isMain=True), size=AWARDS_SIZES.BIG, isObtained=self.event.isMainCompleted(), obtainedImage=RES_ICONS.MAPS_ICONS_LIBRARY_AWARDOBTAINED, obtainedImageOffset=16)
        if not extended:
            awardsFullyCompleted = _personalMissionsAwardsFormatter.getPawnedQuestBonuses(self.event.getBonuses(isMain=False), size=AWARDS_SIZES.BIG, isObtained=self.event.isFullCompleted(), pawnedTokensCount=pawnedTokensCount, freeTokenName=PM_BRANCH_TO_FREE_TOKEN_NAME[self.event.getQuestBranch()], obtainedImage=RES_ICONS.MAPS_ICONS_LIBRARY_AWARDOBTAINED, obtainedImageOffset=16)
        else:
            awardsFullyCompleted = _personalMissionsAwardsFormatter.getReturnTokensQuestBonuses(self.event.getBonuses(isMain=False), size=AWARDS_SIZES.BIG, isObtained=self.event.isFullCompleted(), returnedTokensCount=self.event.getPawnCost(), freeTokenName=PM_BRANCH_TO_FREE_TOKEN_NAME[self.event.getQuestBranch()], obtainedImage=RES_ICONS.MAPS_ICONS_LIBRARY_AWARDOBTAINED, obtainedImageOffset=16)
        return {'awards': awards,
         'awardsFullyCompleted': awardsFullyCompleted}

    def _getConditions(self):
        formatter = formatters.PMCardConditionsFormatter(self.event)
        self.__anyProgress = formatter.hasProgressForReset()
        return {'bodyProgress': formatter.bodyFormat(),
         'headerProgress': formatter.headerFormat()}

    def _getTitle(self, title):
        return text_styles.superPromoTitle(title)

    def _getInfo(self, statusData, isAvailable, errorMsg, mainQuest=None):
        data = super(_DetailedPersonalMissionInfo, self)._getInfo(statusData, isAvailable, errorMsg, mainQuest)
        data.update({'bottomStatusText': statusData.get('bottomStatusText', ''),
         'showIcon': statusData.get('showIcon', False),
         'addBottomStatusText': statusData.get('addBottomStatusText', ''),
         'bottomStatusTooltipData': statusData.get('bottomStatusTooltipData', ''),
         'retryBtnLabel': self.__getRetryBtnLabel(),
         'retryBtnTooltip': self.__getRetryBtnTooltip(isAvailable),
         'completeBtnLabel': _ms(PERSONAL_MISSIONS.DETAILEDVIEW_COMPLETEBTNLABEL, count=self.event.getPawnCost(), icon=getHtmlAwardSheetIcon(self.event.getQuestBranch())),
         'titleTooltip': self.__getDescription(),
         'holdAwardSheetBtnTooltipData': self.__getHoldAwardSheetBtnTooltipData()})
        data.update({'buttonState': self.__getBtnStates(isAvailable)})
        data.update({'onPauseBtnIcon': self.__getPauseBtnIcon()})
        return data

    def __getAddBottomInfo(self):
        quest = self.event
        pmCache = self._eventsCache.getPersonalMissions()
        curOperation = pmCache.getAllOperations().get(quest.getOperationID())
        vehType, minLevel, maxLevel = getChainVehTypeAndLevelRestrictions(curOperation, quest.getChainID())
        if quest.getQuestBranch() == PM_BRANCH.REGULAR:
            return text_styles.standard(_ms(QUESTS.PERSONALMISSION_STATUS_ADDBOTTOMINFO_REGULAR, vehType=vehType, minLevel=minLevel, maxLevel=maxLevel))
        return text_styles.standard(_ms(QUESTS.PERSONALMISSION_STATUS_ADDBOTTOMINFO_PM2, vehType=vehType, minLevel=minLevel, maxLevel=maxLevel)) if quest.getQuestBranch() == PM_BRANCH.PERSONAL_MISSION_2 else ''

    def __getAddBottomLocked(self):
        quest = self.event
        pmCache = self._eventsCache.getPersonalMissions()
        curOperation = pmCache.getAllOperations().get(quest.getOperationID())
        vehType, minLevel, maxLevel = getChainVehTypeAndLevelRestrictions(curOperation, quest.getChainID())
        if quest.getQuestBranch() == PM_BRANCH.REGULAR:
            return text_styles.error(_ms(QUESTS.PERSONALMISSION_STATUS_ADDBOTTOMLOCKED_REGULAR, vehType=vehType, minLevel=minLevel, maxLevel=maxLevel))
        return text_styles.error(_ms(QUESTS.PERSONALMISSION_STATUS_ADDBOTTOMLOCKED_PM2, vehType=vehType, minLevel=minLevel, maxLevel=maxLevel)) if quest.getQuestBranch() == PM_BRANCH.PERSONAL_MISSION_2 else ''

    def __getHoldAwardSheetBtnTooltipData(self):
        if self.__isPawnAvailable(self.event):
            specialAlias = TOOLTIPS_CONSTANTS.FREE_SHEET_RETURN
        else:
            specialAlias = TOOLTIPS_CONSTANTS.FREE_SHEET_NOT_ENOUGH
        return {'specialAlias': specialAlias,
         'isSpecial': True,
         'specialArgs': [self.event.getCampaignID()]}

    def __getRetryBtnLabel(self):
        if self.event.areTokensPawned():
            if self.event.getPawnCost() <= 1:
                return _ms(PERSONAL_MISSIONS.TASKDETAILSVIEW_BTNLABEL_RETURNAWARDSHEET)
            return _ms(PERSONAL_MISSIONS.TASKDETAILSVIEW_BTNLABEL_RETURNAWARDSHEETS)
        return _ms(PERSONAL_MISSIONS.DETAILEDVIEW_RETRYBTNLABEL)

    def __getRetryBtnTooltip(self, isAvailable):
        tooltip = PERSONAL_MISSIONS.DETAILEDVIEW_TOOLTIPS_RETRYBTN
        if not isAvailable:
            tooltipBody = TOOLTIPS.PERSONALMISSIONS_STATUS_LOCKEDBYVEHICLETYPE_BODY
            if self.event.getQuestBranch() == PM_BRANCH.PERSONAL_MISSION_2:
                tooltipBody = TOOLTIPS.PERSONALMISSIONS_STATUS_LOCKEDBYVEHICLEALLIANCE_BODY
            tooltip = makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_STATUS_LOCKEDBYVEHICLE_HEADER, body=_ms(tooltipBody, vehType=_ms(MENU.classesShort(self.event.getQuestClassifier().classificationAttr)), minLevel=int2roman(self.event.getVehMinLevel()), maxLevel=int2roman(self.event.getVehMaxLevel())))
        elif self.event.areTokensPawned():
            tooltip = PERSONAL_MISSIONS.DETAILEDVIEW_TOOLTIPS_RETURNAWARDLISTBTN
        return tooltip

    def __getDescription(self):
        description = '\n'.join([self.event.getUserDescription(), self.event.getUserAdvice()])
        return None if not description else makeTooltip(PERSONAL_MISSIONS.DETAILEDVIEW_INFOPANEL_HEADER, description)

    def __getBtnStates(self, isAvailable):
        quest = self.event
        isPawnAvailable = self.__isPawnAvailable(quest)
        states = PERSONAL_MISSIONS_BUTTONS.NO_BUTTONS
        if not quest.isUnlocked():
            states |= PERSONAL_MISSIONS_BUTTONS.START_BTN_VISIBLE
        elif quest.isInProgress() and isAvailable:
            if quest.getOperationID() in self.PAUSABLE_OPERATIONS_IDS:
                states |= PERSONAL_MISSIONS_BUTTONS.PAUSE_BTN_VISIBLE
            if quest.getOperationID() in self.DISCARDABLE_OPERATIONS_IDS:
                states |= PERSONAL_MISSIONS_BUTTONS.DISCARD_BTN_VISIBLE
                if self.__anyProgress:
                    states |= PERSONAL_MISSIONS_BUTTONS.DISCARD_BTN_ENABLED
            if not quest.isMainCompleted():
                states |= PERSONAL_MISSIONS_BUTTONS.HOLD_AWARD_SHEET_BTN_VISIBLE
                if not quest.areTokensPawned() and isPawnAvailable:
                    states |= PERSONAL_MISSIONS_BUTTONS.HOLD_AWARD_SHEET_BTN_ENABLED
        elif quest.isFullCompleted():
            states = PERSONAL_MISSIONS_BUTTONS.NO_BUTTONS
        elif quest.isMainCompleted():
            states |= PERSONAL_MISSIONS_BUTTONS.RETRY_BTN_VISIBLE
            if isAvailable:
                states |= PERSONAL_MISSIONS_BUTTONS.RETRY_BTN_ENABLED
        else:
            states |= PERSONAL_MISSIONS_BUTTONS.START_BTN_VISIBLE
            if isAvailable:
                states |= PERSONAL_MISSIONS_BUTTONS.START_BTN_ENABLED
        if quest.canBePawned():
            states |= PERSONAL_MISSIONS_BUTTONS.HOLD_AWARD_SHEET_BTN_VISIBLE
            if isPawnAvailable:
                states |= PERSONAL_MISSIONS_BUTTONS.HOLD_AWARD_SHEET_BTN_ENABLED
        return states

    def __getPauseBtnIcon(self):
        quest = self.event
        if quest.getOperationID() in self.PAUSABLE_OPERATIONS_IDS:
            if quest.isOnPause:
                return RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_BTN_ICON_PLAY
            return RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_BTN_ICON_PAUSE

    def __isPawnAvailable(self, quest):
        return self.eventsCache.getPersonalMissions().getFreeTokensCount(quest.getPMType().branch) >= quest.getPawnCost()


def getMissionInfoData(event):
    if event.getType() == constants.EVENT_TYPE.TOKEN_QUEST:
        return _TokenMissionInfo(event)
    elif event.getType() == constants.EVENT_TYPE.PERSONAL_QUEST:
        return _PrivateMissionInfo(event)
    elif isPremium(event.getID()):
        return _PremiumMissionInfo(event)
    elif event.getGroupID() == FRONTLINE_GROUP_ID:
        return _EpicDailyMissionInfo(event)
    elif isRankedQuestID(event.getID()):
        return _RankedMissionInfo(event)
    else:
        return _MissionInfo(event) if event.getType() in constants.EVENT_TYPE.LIKE_BATTLE_QUESTS else None


def getDetailedMissionData(event):
    if event.getType() == constants.EVENT_TYPE.TOKEN_QUEST:
        return _DetailedTokenMissionInfo(event)
    elif event.getType() == constants.EVENT_TYPE.PERSONAL_QUEST:
        return _DetailedPrivateMissionInfo(event)
    elif event.getType() == constants.EVENT_TYPE.PERSONAL_MISSION:
        return _DetailedPersonalMissionInfo(event)
    elif isPremium(event.getID()):
        return _PremiumDetailedMissionInfo(event)
    elif event.getGroupID() == FRONTLINE_GROUP_ID:
        return _EpicDetailedMissionInfo(event)
    elif isRankedQuestID(event.getID()):
        return _RankedDetailedMissionInfo(event)
    else:
        return _DetailedMissionInfo(event) if event.getType() in constants.EVENT_TYPE.LIKE_BATTLE_QUESTS else None


def getAwardsWindowBonuses(bonuses):
    result = _awardsWindowBonusFormatter.getFormattedBonuses(bonuses, AWARDS_SIZES.BIG)
    while len(result) % AWARDS_PER_SINGLE_PAGE != 0 and len(result) > AWARDS_PER_SINGLE_PAGE:
        result.append({})

    return result


def getEpicAwardsWindowBonuses(bonuses):
    result = _epicAwardsWindowBonusFormatter.getFormattedBonuses(bonuses, EPIC_AWARD_SIZE)
    while len(result) % AWARDS_PER_SINGLE_PAGE != 0 and len(result) > AWARDS_PER_SINGLE_PAGE:
        result.append({})

    return result


def getPersonalMissionAwardsFormatter():
    return _personalMissionsAwardsFormatter


def getMissionAwardsFormatter():
    return _awardsWindowBonusFormatter


def getLinkedSetBonuses(bonuses):
    result = _linkedSetAwardsComposer.getFormattedBonuses(bonuses, AWARDS_SIZES.BIG)
    while len(result) % AWARDS_PER_SINGLE_PAGE != 0 and len(result) > AWARDS_PER_SINGLE_PAGE:
        result.append({})

    return result


def getMapRegionTooltipData(state, quest):
    if quest.isDisabled():
        tooltipData = {'tooltip': makeTooltip(header=quest.getUserName(), body=_ms(TOOLTIPS.PERSONALMISSIONS_MAPREGION_DESCR_DISABLED)),
         'isSpecial': False,
         'specialArgs': []}
    elif quest.isFullCompleted():
        tooltipData = {'tooltip': makeTooltip(header=quest.getUserName(), body=_ms(TOOLTIPS.PERSONALMISSIONS_MAPREGION_DESCR_EXCELLENTDONE)),
         'isSpecial': False,
         'specialArgs': []}
    else:
        tooltipData = {'specialAlias': TOOLTIPS_CONSTANTS.PERSONAL_MISSIONS_MAP_REGION,
         'isSpecial': True,
         'specialArgs': [quest.getID(), state]}
    return tooltipData
