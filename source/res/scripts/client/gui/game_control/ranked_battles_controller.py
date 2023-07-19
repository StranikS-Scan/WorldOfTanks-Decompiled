# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/ranked_battles_controller.py
import logging
import operator
import sys
from collections import defaultdict
import typing
import BigWorld
import Event
import season_common
from account_helpers import AccountSettings
from account_helpers.AccountSettings import RANKED_LAST_CYCLE_ID, RANKED_WEB_INFO, RANKED_WEB_INFO_UPDATE
from adisp import adisp_process
from constants import ARENA_BONUS_TYPE, EVENT_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.periodic_battles.models import PrimeTimeStatus
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, PRE_QUEUE_RESTRICTION, SELECTOR_BATTLE_TYPES
from gui.ranked_battles import ranked_helpers
from gui.ranked_battles.constants import ENTITLEMENT_EVENT_TOKEN, FINAL_LEADER_QUEST, FINAL_QUEST_PATTERN, MAX_GROUPS_IN_DIVISION, NOT_IN_LEAGUES_QUEST, STANDARD_POINTS_COUNT, YEAR_AWARDS_ORDER, YEAR_AWARD_SELECTABLE_OPT_DEVICE_PREFIX, YEAR_POINTS_TOKEN, YEAR_STRIPE_CLIENT_TOKEN, YEAR_STRIPE_SERVER_TOKEN, ZERO_RANK_ID
from gui.ranked_battles.ranked_builders.postbattle_awards_vos import AwardBlock
from gui.ranked_battles.ranked_formatters import getRankedAwardsFormatter
from gui.ranked_battles.ranked_helpers.sound_manager import RankedSoundManager, Sounds
from gui.ranked_battles.ranked_helpers.stats_composer import RankedBattlesStatsComposer
from gui.ranked_battles.ranked_helpers.web_season_provider import RankedWebSeasonProvider, UNDEFINED_LEAGUE_ID, UNDEFINED_WEB_INFO
from gui.ranked_battles.ranked_helpers.year_position_provider import RankedYearPositionProvider
from gui.ranked_battles.ranked_models import BattleRankInfo, Division, Rank, RankChangeStates, RankData, RankProgress, RankState, RankStep, RankedAlertData, RankedSeason, ShieldStatus
from gui.selectable_reward.common import RankedSelectableRewardManager
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.event_items import RankedQuest
from gui.server_events.events_helpers import EventInfoModel
from gui.shared import EVENT_BUS_SCOPE, event_dispatcher, events, g_eventBus
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.money import Currency
from gui.shared.utils.SelectorBattleTypesUtils import setBattleTypeAsUnknown
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier, TimerNotifier
from helpers import dependency, time_utils
from ranked_common import SwitchState
from season_provider import SeasonProvider
from shared_utils import findFirst, first
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
from web.web_client_api.ranked_battles import createRankedBattlesWebHandlers
if typing.TYPE_CHECKING:
    from gui.ranked_battles.constants import YearAwardsNames
    from gui.ranked_battles.ranked_helpers.web_season_provider import WebSeasonInfo
    from gui.ranked_battles.ranked_models import PostBattleRankInfo
    from season_common import GameSeason
    from helpers.server_settings import RankedBattlesConfig
_logger = logging.getLogger(__name__)
ZERO_RANK_COUNT = 1
DEFAULT_RANK = RankData(0, 0)

def _showRankedBattlePage(ctx):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(RANKEDBATTLES_ALIASES.RANKED_BATTLES_PAGE_ALIAS), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)


def _showRankedBattlePageSeasonOff(ctx):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(RANKEDBATTLES_ALIASES.RANKED_BATTLES_PAGE_SEASON_OFF_ALIAS), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)


def _showSeparateWebView(url, alias):
    event_dispatcher.showBrowserOverlayView(url, alias=alias, webHandlers=createRankedBattlesWebHandlers())


class ShowRankedPageCallback(object):

    def __init__(self, ctx):
        self.__ctx = ctx

    def __call__(self, *args, **kwargs):
        _showRankedBattlePage(self.__ctx)


class RankedBattlesController(IRankedBattlesController, Notifiable, SeasonProvider, IGlobalListener):
    _ALERT_DATA_CLASS = RankedAlertData
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __battleResultsService = dependency.descriptor(IBattleResultsService)
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __clansController = dependency.descriptor(IWebController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(RankedBattlesController, self).__init__()
        self.onUpdated = Event.Event()
        self.onGameModeStatusTick = Event.Event()
        self.onGameModeStatusUpdated = Event.Event()
        self.onYearPointsChanges = Event.Event()
        self.onEntitlementEvent = Event.Event()
        self.onKillWebOverlays = Event.Event()
        self.onSelectableRewardsChanged = Event.Event()
        self.__serverSettings = None
        self.__rankedSettings = None
        self.__battlesGroups = None
        self.__rankedWelcomeCallback = None
        self.__rankedWebOpenPageCtx = None
        self.__clientValuesInited = False
        self.__clientRank = DEFAULT_RANK
        self.__clientShields = {}
        self.__clientMaxRank = DEFAULT_RANK
        self.__clientWebSeasonInfo = UNDEFINED_WEB_INFO
        self.__clientWebSeasonInfoUpdateTime = None
        self.__clientEfficiency = None
        self.__clientEfficiencyDiff = None
        self.__clientBonusBattlesCount = None
        self.__ranksCache = []
        self.__divisions = None
        self.__statsComposer = None
        self.__webSeasonProvider = RankedWebSeasonProvider()
        self.__yearPositionProvider = RankedYearPositionProvider()
        self.__soundManager = RankedSoundManager()
        self.__isRankedSoundMode = False
        self.__arenaBattleResultsWasShown = set()
        return

    def init(self):
        super(RankedBattlesController, self).init()
        self.addNotificator(SimpleNotifier(self.getTimer, self.__timerUpdate))
        self.addNotificator(TimerNotifier(self.getTimer, self.__timerTick))

    def fini(self):
        self.onUpdated.clear()
        self.onGameModeStatusTick.clear()
        self.onGameModeStatusUpdated.clear()
        self.onYearPointsChanges.clear()
        self.onEntitlementEvent.clear()
        self.onKillWebOverlays.clear()
        self.clearNotification()
        super(RankedBattlesController, self).fini()

    def onAccountBecomePlayer(self):
        self.__clearCaches()
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())
        self.__statsComposer = RankedBattlesStatsComposer(self.__rankedSettings, self.__getCurrentOrPreviousSeason())
        self.__battleResultsService.onResultPosted += self.__onShowBattleResults

    def onAccountBecomeNonPlayer(self):
        self.__clearCaches()
        self.__clear()
        self.__battleResultsService.onResultPosted -= self.__onShowBattleResults

    def onAvatarBecomePlayer(self):
        if self.__serverSettings is None:
            self.__lobbyContext.onServerSettingsChanged += self.__onServerSettingsChanged
        return

    def onDisconnected(self):
        self.__clearCaches()
        self.__clearClientValues()
        self.__clear()
        self.__lobbyContext.onServerSettingsChanged -= self.__onServerSettingsChanged

    def onLobbyInited(self, event):
        if not self.__clientValuesInited:
            self.__resizeRanksCache(self.__rankedSettings)
            self.__clientWebSeasonInfo = AccountSettings.getSettings(RANKED_WEB_INFO)
            self.__clientWebSeasonInfoUpdateTime = AccountSettings.getSettings(RANKED_WEB_INFO_UPDATE)
            self.__webSeasonProvider.clear()
            self.updateClientValues()
            self.__clientValuesInited = True
        shouldInitPrefs = self.__clientWebSeasonInfo is None
        isDefinedLeague = not shouldInitPrefs and self.__clientWebSeasonInfo.league != UNDEFINED_LEAGUE_ID
        shouldFlushPrefs = isDefinedLeague and not self.isAccountMastered()
        if shouldInitPrefs or shouldFlushPrefs:
            self.__webSeasonProvider.clear()
            self.__clientWebSeasonInfo = UNDEFINED_WEB_INFO
            self.__clientWebSeasonInfoUpdateTime = None
            AccountSettings.setSettings(RANKED_WEB_INFO, self.__clientWebSeasonInfo)
            AccountSettings.setSettings(RANKED_WEB_INFO_UPDATE, self.__clientWebSeasonInfoUpdateTime)
        if self.isAccountMastered() and not self.__webSeasonProvider.isStarted:
            self.__webSeasonProvider.start()
        if not self.__yearPositionProvider.isStarted:
            self.__yearPositionProvider.start()
        self.__isRankedSoundMode = False
        self.__updateSounds(self.isRankedPrbActive())
        g_clientUpdateManager.addCallbacks({'ranked': self.__onUpdateRanked,
         'ranked.accRank': self.__onUpdateLeagueSync,
         'tokens': self.__onTokensUpdate})
        self.startNotification()
        self.startGlobalListening()
        return

    def onPrbEntitySwitching(self):
        switchedFromRanked = self.isRankedPrbActive()
        if switchedFromRanked:
            self.__updateSounds(False)

    def onPrbEntitySwitched(self):
        isRankedSoundMode = self.isRankedPrbActive()
        if isRankedSoundMode:
            self.__updateSounds(True)
        if self.isRankedPrbActive():
            self.updateClientValues()

    def getModeSettings(self):
        return self.__rankedSettings

    def isAvailable(self):
        return self.isEnabled() and not self.isFrozen() and self.getCurrentSeason() is not None

    def isAccountMastered(self):
        currentRank, _ = self.__itemsCache.items.ranked.accRank
        return currentRank == self.getMaxPossibleRank() != ZERO_RANK_ID

    def isBattlesPossible(self):
        return self.isEnabled() and self.getCurrentSeason() is not None

    def isEnabled(self):
        return self.__rankedSettings.isEnabled

    def isRankedPrbActive(self):
        return False if self.prbEntity is None else bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.RANKED)

    def isRankedShopEnabled(self):
        return self.__rankedSettings.shopState == SwitchState.ENABLED

    def isSeasonRewarding(self):
        prevSeason = self.getPreviousSeason()
        notInLeaguesQuestID = NOT_IN_LEAGUES_QUEST.format(prevSeason.getSeasonID() if prevSeason is not None else '')
        notInLeaguesQuest = self.__eventsCache.getHiddenQuests().get(notInLeaguesQuestID)
        return notInLeaguesQuest is not None and notInLeaguesQuest.getStartTimeLeft() != 0

    def isSuitableVehicle(self, vehicle):
        ctx = {}
        restriction = None
        config = self.__getRankedSettings()
        state, _ = vehicle.getState()
        if state == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE or vehicle.compactDescr in config.forbiddenVehTypes:
            restriction = PRE_QUEUE_RESTRICTION.LIMIT_VEHICLE_TYPE
            ctx = {'forbiddenType': vehicle.shortUserName}
        if vehicle.type in config.forbiddenClassTags:
            restriction = PRE_QUEUE_RESTRICTION.LIMIT_VEHICLE_CLASS
            ctx = {'forbiddenClass': vehicle.type}
        if vehicle.level < config.minLevel or config.maxLevel < vehicle.level:
            restriction = PRE_QUEUE_RESTRICTION.LIMIT_LEVEL
            ctx = {'levels': range(config.minLevel, config.maxLevel + 1)}
        return ValidationResult(False, restriction, ctx) if restriction is not None else None

    def isUnset(self):
        status, _, _ = self.getPrimeTimeStatus()
        return status == PrimeTimeStatus.NOT_SET

    def isYearGap(self):
        prevSeason = self.getPreviousSeason()
        isPrevFinal = prevSeason is not None and prevSeason.getNumber() == self.getExpectedSeasons()
        finalLeaderQuest = self.__eventsCache.getHiddenQuests().get(FINAL_LEADER_QUEST)
        return isPrevFinal and finalLeaderQuest is not None and finalLeaderQuest.getStartTimeLeft() == 0

    def isYearLBEnabled(self):
        return self.__rankedSettings.yearLBState == SwitchState.ENABLED

    def getYearLBState(self):
        return self.__rankedSettings.yearLBState

    def isYearRewardEnabled(self):
        return self.__rankedSettings.yearRewardState == SwitchState.ENABLED

    def hasSpecialSeason(self):
        return self.__rankedSettings.hasSpecialSeason

    def hasPrimeTimesTotalLeft(self):
        return self.__hasPrimeTimesLeft(time_utils.getCurrentLocalServerTimestamp())

    def hasPrimeTimesNextDayLeft(self):
        nextGameDay = time_utils.getCurrentLocalServerTimestamp() + EventInfoModel.getDailyProgressResetTimeDelta()
        return self.__hasPrimeTimesLeft(nextGameDay)

    def hasSuitableVehicles(self):
        criteria = self.__filterEnabledVehiclesCriteria(REQ_CRITERIA.INVENTORY)
        return len(self.__itemsCache.items.getVehicles(criteria)) > 0

    def suitableVehicleIsAvailable(self):
        return self.vehicleIsAvailableForBuy() or self.vehicleIsAvailableForRestore()

    def vehicleIsAvailableForBuy(self):
        criteria = self.__filterEnabledVehiclesCriteria(REQ_CRITERIA.UNLOCKED)
        criteria |= ~REQ_CRITERIA.VEHICLE.SECRET | ~REQ_CRITERIA.HIDDEN
        vUnlocked = self.__itemsCache.items.getVehicles(criteria)
        return len(vUnlocked) > 0

    def vehicleIsAvailableForRestore(self):
        criteria = self.__filterEnabledVehiclesCriteria(REQ_CRITERIA.VEHICLE.IS_RESTORE_POSSIBLE)
        vResorePossible = self.__itemsCache.items.getVehicles(criteria)
        return len(vResorePossible) > 0

    def hasVehicleRankedBonus(self, compactDescr):
        bonusUsed = compactDescr in self.__itemsCache.items.stats.multipliedRankedVehicles
        return not bonusUsed and self.getStatsComposer().bonusBattlesCount > 0

    def getAlertBlock(self):
        alertData = self._getAlertBlockData()
        buttonCallback = event_dispatcher.showRankedPrimeTimeWindow
        if not self.hasSuitableVehicles():
            buttonCallback = g_eventDispatcher.loadRankedUnreachable
        return (buttonCallback, alertData or self._ALERT_DATA_CLASS(), alertData is not None)

    def getAwardTypeByPoints(self, points):
        pointMap = self.getYearAwardsPointsMap()
        awardType = None
        for boxName in YEAR_AWARDS_ORDER:
            minPoints, _ = pointMap[boxName]
            if minPoints <= points:
                awardType = boxName

        return awardType

    def getBonusBattlesMultiplier(self):
        return self.__rankedSettings.bonusBattlesMultiplier

    def getClientRank(self):
        return self.__clientRank

    def getClientMaxRank(self):
        return self.__clientMaxRank

    def getClientShields(self):
        return self.__clientShields

    def getClientSeasonInfo(self):
        return self.__clientWebSeasonInfo

    def getClientSeasonInfoUpdateTime(self):
        return self.__clientWebSeasonInfoUpdateTime

    def getClientEfficiency(self):
        return self.__clientEfficiency

    def getClientEfficiencyDiff(self):
        return self.__clientEfficiencyDiff

    def getClientBonusBattlesCount(self):
        return self.__clientBonusBattlesCount

    def getCompensation(self, points):
        pointMap = self.getYearAwardsPointsMap()
        awardPoints = 0
        for boxName in YEAR_AWARDS_ORDER:
            minPoints, _ = pointMap[boxName]
            if minPoints <= points:
                awardPoints = minPoints

        return points - awardPoints

    def getCurrentDivision(self):
        return findFirst(operator.methodcaller('isCurrent'), self.getDivisions())

    def getCurrentPointToCrystalRate(self):
        rate = 0
        bonuses = self.getYearRewards(STANDARD_POINTS_COUNT)
        for bonus in bonuses:
            if bonus.getName() == Currency.CRYSTAL:
                rate = bonus.getCount()

        return rate

    def getCurrentRank(self):
        return RankData(*self.__itemsCache.items.ranked.accRank)

    def getCurrentSeason(self, now=None):
        now = now or time_utils.getCurrentLocalServerTimestamp()
        isCycleActive, seasonInfo = season_common.getSeason(self.__rankedSettings.asDict(), now)
        if isCycleActive:
            _, _, seasonID, _ = seasonInfo
            return self._createSeason(seasonInfo, self.__rankedSettings.seasons.get(seasonID, {}))
        else:
            return None

    def getDivision(self, rankID):
        if rankID == ZERO_RANK_ID:
            return first(self.getDivisions())
        else:
            for division in self.getDivisions():
                if rankID in division.getRanksIDs():
                    return division

            return None

    def getDivisions(self):
        if self.__divisions is None:
            self.__divisions = self.__buildDivisions()
        return self.__divisions

    def getEntitlementEvents(self):
        return self.__getTokensAmount(ENTITLEMENT_EVENT_TOKEN)

    def getExpectedSeasons(self):
        return self.__rankedSettings.expectedSeasons

    def getWebSeasonProvider(self):
        return self.__webSeasonProvider

    def getLeagueRewards(self, bonusName=None):
        now = time_utils.getCurrentLocalServerTimestamp()
        isCurrent, seasonInfo = season_common.getSeason(self.__rankedSettings.asDict(), now)
        result = []
        if isCurrent:
            _, _, seasonID, _ = seasonInfo
            seasonQuests = self.__eventsCache.getHiddenQuests(lambda q: q.getType() == EVENT_TYPE.TOKEN_QUEST and ranked_helpers.isRankedQuestID(q.getID()) and ranked_helpers.isSeasonTokenQuest(q.getID()))
            for qID in sorted(seasonQuests, reverse=True):
                season, leagueID, isSprinter = ranked_helpers.getDataFromSeasonTokenQuestID(qID)
                if season == seasonID and not isSprinter:
                    quest = seasonQuests[qID]
                    result.append({'league': leagueID,
                     'awards': quest.getBonuses(bonusName=bonusName)})

        return result

    def getMaxPossibleRank(self):
        return self.__rankedSettings.accRanks

    def getMaxRank(self):
        return RankData(*self.__itemsCache.items.ranked.maxRank)

    def getRank(self, rankID):
        return self.getRanksChain(rankID, rankID)[rankID]

    def getRankChangeStatus(self, changeInfo):
        isBonusBattle = changeInfo.isBonusBattle
        stepChanges = changeInfo.stepChanges
        updatedStepChanges = changeInfo.updatedStepChanges
        if changeInfo.accRank > changeInfo.prevAccRank:
            if self.getDivision(changeInfo.prevAccRank + 1).isQualification():
                if updatedStepChanges == 0 and stepChanges < updatedStepChanges:
                    return RankChangeStates.QUAL_UNBURN_EARNED
                return RankChangeStates.QUAL_EARNED
        if updatedStepChanges > 0:
            if changeInfo.accRank > changeInfo.prevAccRank:
                if changeInfo.accRank == self.getMaxPossibleRank():
                    return RankChangeStates.LEAGUE_EARNED
                prevDivisionID = self.getDivision(changeInfo.prevAccRank + 1).getID()
                currDivisionID = self.getDivision(changeInfo.accRank + 1).getID()
                if currDivisionID > prevDivisionID:
                    return RankChangeStates.DIVISION_EARNED
                return RankChangeStates.RANK_EARNED
            if stepChanges > 1:
                if isBonusBattle:
                    return RankChangeStates.BONUS_STEPS_EARNED
                return RankChangeStates.STEPS_EARNED
            if isBonusBattle:
                return RankChangeStates.BONUS_STEP_EARNED
            return RankChangeStates.STEP_EARNED
        if updatedStepChanges < 0:
            if changeInfo.accRank < changeInfo.prevAccRank:
                return RankChangeStates.RANK_LOST
            return RankChangeStates.STEP_LOST
        if stepChanges < updatedStepChanges:
            if changeInfo.shieldState in (RANKEDBATTLES_ALIASES.SHIELD_LOSE, RANKEDBATTLES_ALIASES.SHIELD_LOSE_STEP):
                return RankChangeStates.RANK_SHIELD_PROTECTED
            return RankChangeStates.RANK_UNBURN_PROTECTED
        return RankChangeStates.NOTHING_CHANGED

    def getRankDisplayInfoForBattle(self, rankID):
        division = self.getDivision(rankID)
        if division is None:
            _logger.warning('Wrong ranked_config.xml, cannot be found division for rank %s.', rankID)
            return BattleRankInfo(-1, -1, False)
        else:
            divisionID = division.getID()
            if division.isQualification() and rankID == ZERO_RANK_ID:
                return BattleRankInfo(rankID, divisionID, False)
            if rankID == self.getMaxPossibleRank():
                return BattleRankInfo(ZERO_RANK_ID, divisionID + 1, False)
            isShifted = False
            if rankID == division.lastRank:
                isShifted = True
                division = self.getDivision(rankID + 1)
                divisionID += 1
            groups = self.__getGroupsForBattle()
            if self.__hasMatchMakerGroups(division, groups[divisionID]):
                for idx, ranksRange in enumerate(reversed(groups[divisionID]), start=1):
                    if rankID in ranksRange:
                        return BattleRankInfo(idx, divisionID, True)

            else:
                if isShifted:
                    return BattleRankInfo(ZERO_RANK_ID, divisionID, False)
                level = division.getRankUserId(rankID) if rankID else rankID
                return BattleRankInfo(level, divisionID, False)
            _logger.error('Wrong ranked_config.xml, wrong rankGroups section!!!')
            return BattleRankInfo(-1, -1, False)

    def getRankedWelcomeCallback(self):
        return self.__rankedWelcomeCallback

    def setRankedWelcomeCallback(self, value):
        self.__rankedWelcomeCallback = value

    def getRanksChanges(self, isLoser=False):
        return self.__rankedSettings.loserRankChanges if isLoser else self.__rankedSettings.winnerRankChanges

    def getRanksChain(self, leftRequiredBorder, rightRequiredBorder):
        leftRequiredBorder = max(0, leftRequiredBorder)
        rightRequiredBorder = min(self.getMaxPossibleRank(), rightRequiredBorder)
        invalidRanksIDs = set()
        for rankID in range(leftRequiredBorder, rightRequiredBorder + 1):
            if self.__ranksCache[rankID] is None:
                invalidRanksIDs.add(rankID)

        if invalidRanksIDs:
            currentProgress = self.__itemsCache.items.ranked.accRank
            lastProgress = self.getClientRank()
            maxProgress = self.__itemsCache.items.ranked.maxRank
            shields = self.__itemsCache.items.ranked.shields
            lastShields = self.getClientShields()
            for rankID in invalidRanksIDs:
                self.__ranksCache[rankID] = self.__getRank(currentProgress, lastProgress, maxProgress, lastShields.get(rankID), shields.get(rankID), rankID)

        return self.__ranksCache[:]

    def getRanksChainExt(self, currentProgress, lastProgress, maxProgress, shields, lastShields, isBonusBattle):
        cacheCopy = self.__ranksCache[:]
        settings = self.__rankedSettings
        leftRequiredBorder = max(0, min(lastProgress[0], currentProgress[0]))
        rightRequiredBorder = min(settings.accRanks, max(lastProgress[0], currentProgress[0]) + 1)
        bonusStepsToProgress = None
        if isBonusBattle:
            bonusStepsToProgress = self.__getBonusSteps(lastProgress, currentProgress, settings.accRanks, settings.accSteps)
        for rankID in range(leftRequiredBorder, rightRequiredBorder + 1):
            cacheCopy[rankID] = self.__getRank(currentProgress, lastProgress, maxProgress, lastShields.get(rankID), shields.get(rankID), rankID, bonusStepsToProgress)

        return cacheCopy

    def getRanksTops(self, isLoser=False, stepDiff=None):
        rankChanges = self.__rankedSettings.loserRankChanges if isLoser else self.__rankedSettings.winnerRankChanges
        if stepDiff is None:
            return len(rankChanges)
        else:
            if stepDiff == RANKEDBATTLES_ALIASES.STEP_VALUE_EARN:
                total = sum((1 for i in rankChanges if i > 0))
            elif stepDiff == RANKEDBATTLES_ALIASES.STEP_VALUE_NO_CHANGE:
                total = sum((1 for i in rankChanges if i == 0))
            else:
                total = sum((1 for i in rankChanges if i < 0))
            return total

    def getSoundManager(self):
        return self.__soundManager

    def getStatsComposer(self):
        return self.__statsComposer

    def getSuitableVehicleLevels(self):
        return (self.__rankedSettings.minLevel, self.__rankedSettings.maxLevel)

    def getTotalQualificationBattles(self):
        return self.__rankedSettings.qualificationBattles

    def getWebOpenPageCtx(self):
        return self.__rankedWebOpenPageCtx

    def getYearAwardsPointsMap(self):
        result = {}
        awardsMarks = self.__rankedSettings.yearAwardsMarks[:]
        awardsMarks.append(sys.maxint)
        for idx, name in enumerate(YEAR_AWARDS_ORDER):
            result[name] = (awardsMarks[idx], awardsMarks[idx + 1] - 1)

        return result

    def getYearLBSize(self):
        return self.__rankedSettings.yearLBSize

    def getYearRewardPoints(self):
        return self.__getTokensAmount(YEAR_POINTS_TOKEN)

    def getYearRewards(self, points):
        quests = self.__eventsCache.getHiddenQuests()
        finalTokenQuest = quests.get(FINAL_QUEST_PATTERN.format(points))
        return finalTokenQuest.getBonuses() if finalTokenQuest else []

    def getCompletedYearQuest(self):
        quests = self.__eventsCache.getHiddenQuests()
        maxPoints, _ = self.getYearAwardsPointsMap().get(YEAR_AWARDS_ORDER[-1], (0, 0))
        rankedFinalQuests = {points:quests.get(FINAL_QUEST_PATTERN.format(points)) for points in xrange(0, maxPoints + 1)}
        for points, quest in rankedFinalQuests.iteritems():
            if quest is not None and quest.isCompleted():
                return {points: quest}

        return

    def getQualificationQuests(self, quests=None):
        if quests is None:
            qualificationQuests = self.getQuestsForRank(ZERO_RANK_ID) or {}
        else:
            qualificationQuests = {quest.getID():quest for quest in quests}
        return {value.getQualificationBattlesCount():value for key, value in qualificationQuests.iteritems() if value.isQualificationQuest()}

    def awardWindowShouldBeShown(self, rankChangeInfo):
        if rankChangeInfo.prevAccRank == ZERO_RANK_ID:
            return True
        if rankChangeInfo.accRank == self.getMaxPossibleRank():
            return True
        return True if rankChangeInfo.stepChanges > 0 and rankChangeInfo.prevMaxRank < rankChangeInfo.accRank else False

    def clearRankedWelcomeCallback(self):
        self.__rankedWelcomeCallback = None
        return

    def clearWebOpenPageCtx(self):
        self.__rankedWebOpenPageCtx = None
        return

    def runQuests(self, quests):
        notCompletedQuests = []
        for quest in quests:
            if not quest.isCompleted():
                notCompletedQuests.append(quest.getID())
            _logger.warning('Quest is already completed: %s', quest.getID())

        if notCompletedQuests:
            BigWorld.player().runQuest(EVENT_TYPE.RANKED_QUEST, notCompletedQuests, lambda *args: None)

    def showRankedAwardWindow(self, rankedInfo, questsProgress):
        season = self.getCurrentSeason()
        if season is None:
            return
        else:
            awardsSequence = []
            quests = self.__eventsCache.getRankedQuests(lambda q: q.isHidden() and q.isForRank() and q.getSeasonID() == season.getSeasonID())
            formatter = getRankedAwardsFormatter(maxRewardsCount=6)
            for qID, qProgress in questsProgress.iteritems():
                _, pPrev, pCur = qProgress
                isCompleted = pCur.get('bonusCount', 0) - pPrev.get('bonusCount', 0) > 0
                quest = quests.get(qID)
                if quest is not None and quest.isForRank() and isCompleted:
                    awardsSequence.append(AwardBlock(quest.getRank(), formatter.getFormattedBonuses(quest.getBonuses(), AWARDS_SIZES.BIG), qID))

            if awardsSequence:
                event_dispatcher.showRankedAwardWindow(awardsSequence=awardsSequence, rankedInfo=rankedInfo)
            return

    def showRankedBattlePage(self, ctx):
        if not self.__canShowRankedPage():
            _logger.info("Can't open ranked battles page. Forwarding ctx to web fallback.")
            self.__openWebPageByCtx(ctx)
            return
        elif not self.__canShowSelectedPageID(ctx):
            _logger.info("Can't open ranked battles page on selected tab. Call is skipped.")
            return
        else:
            if self.getCurrentSeason() is not None:
                if not self.isRankedPrbActive():
                    self.__rankedWelcomeCallback = ShowRankedPageCallback(ctx)
                    self.__saveWebOpenPageCtx(ctx)
                    self.__switchForcedToRankedPrb()
                else:
                    self.__saveWebOpenPageCtx(ctx)
                    _showRankedBattlePage(ctx)
            else:
                prevSeason = self.getPreviousSeason()
                if prevSeason:
                    ctx.update({'prevSeason': prevSeason})
                    self.__saveWebOpenPageCtx(ctx)
                    _showRankedBattlePageSeasonOff(ctx)
                else:
                    _logger.warning('There is no current or previous season to show RankedMainSeasonOn(Off)Page')
            return

    def updateClientValues(self):
        rankChanges = self.__clientRank != self.getCurrentRank()
        maxRankChanges = self.__clientMaxRank != self.getMaxRank()
        shieldsChanges = self.__clientShields != self.__itemsCache.items.ranked.shields
        shouldFlushCache = rankChanges or maxRankChanges or shieldsChanges
        if shouldFlushCache:
            self.__partialFlushRanksCache()
        self.__clientRank = self.getCurrentRank()
        self.__clientMaxRank = self.getMaxRank()
        self.__clientShields = {}
        for key in self.__itemsCache.items.ranked.shields:
            shield = self.__itemsCache.items.ranked.shields.get(key)
            if shield is not None and isinstance(shield, tuple):
                self.__clientShields[key] = shield[:]

        if self.__webSeasonProvider.seasonInfo.league != UNDEFINED_LEAGUE_ID:
            self.__clientWebSeasonInfo = self.__webSeasonProvider.seasonInfo
            AccountSettings.setSettings(RANKED_WEB_INFO, self.__clientWebSeasonInfo)
        if self.__webSeasonProvider.lastUpdateTime is not None:
            self.__clientWebSeasonInfoUpdateTime = self.__webSeasonProvider.lastUpdateTime
            AccountSettings.setSettings(RANKED_WEB_INFO_UPDATE, self.__clientWebSeasonInfoUpdateTime)
        statsComposer = self.getStatsComposer()
        self.__clientEfficiency = statsComposer.currentSeasonEfficiency.efficiency
        self.__clientEfficiencyDiff = statsComposer.currentSeasonEfficiencyDiff
        self.__clientBonusBattlesCount = statsComposer.bonusBattlesCount
        return

    def doActionOnEntryPointClick(self):
        isEnabled = self.isEnabled()
        isYearGap = self.isYearGap()
        isYearLBEnabled = self.isYearLBEnabled()
        hasCurSeason = self.getCurrentSeason() is not None
        passedSeasons = self.getSeasonPassed()
        if isEnabled:
            if self.isFrozen() or not passedSeasons and not hasCurSeason:
                self.__showPreSeason()
            elif hasCurSeason:
                self.__switchForcedToRankedPrb()
            elif isYearGap and isYearLBEnabled:
                self.__showYearlyLeaders()
            else:
                self.__showBetweenSeason()
        else:
            self.__showYearlyLeaders()
        return

    def getYearRewardCount(self):
        return RankedSelectableRewardManager.getRemainedChoicesForFeature()

    def _createSeason(self, cycleInfo, seasonData):
        return RankedSeason(cycleInfo, seasonData, self.hasSpecialSeason())

    def _getAlertBlockData(self):
        if not self.hasSuitableVehicles():
            minLvl, maxLvl = self.getSuitableVehicleLevels()
            levelsStr = toRomanRangeString(range(minLvl, maxLvl + 1))
            return self._ALERT_DATA_CLASS.constructForVehicle(levelsStr=levelsStr, vehicleIsAvailableForBuy=self.vehicleIsAvailableForBuy(), vehicleIsAvailableForRestore=self.vehicleIsAvailableForRestore())
        return super(RankedBattlesController, self)._getAlertBlockData()

    @adisp_process
    def __switchForcedToRankedPrb(self):
        result = yield g_prbLoader.getDispatcher().doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANKED))
        if not result:
            self.clearRankedWelcomeCallback()

    def __onTokensUpdate(self, diff):
        if YEAR_POINTS_TOKEN in diff:
            self.onYearPointsChanges()
        if YEAR_STRIPE_SERVER_TOKEN in diff and not self.__yearPositionProvider.isStarted:
            self.__yearPositionProvider.start()
        if YEAR_STRIPE_CLIENT_TOKEN in diff and self.__yearPositionProvider.isStarted:
            self.__yearPositionProvider.stop()
        if ENTITLEMENT_EVENT_TOKEN in diff:
            self.onEntitlementEvent()
        if any((key.startswith(YEAR_AWARD_SELECTABLE_OPT_DEVICE_PREFIX) for key in diff.keys())):
            self.onSelectableRewardsChanged()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onUpdateRankedSettings
        self.__serverSettings = serverSettings
        self.__rankedSettings = self.__getRankedSettings()
        self.__storeCycle()
        self.__serverSettings.onServerSettingsChange += self.__onUpdateRankedSettings
        return

    def __onShowBattleResults(self, reusableInfo, composer, resultsWindow):
        arenaBonusType = reusableInfo.common.arenaBonusType
        arenaUniqueID = reusableInfo.arenaUniqueID
        if arenaBonusType == ARENA_BONUS_TYPE.RANKED and arenaUniqueID not in self.__arenaBattleResultsWasShown:
            self.updateClientValues()
            rankInfo = reusableInfo.personal.getRankInfo()
            questsProgress = reusableInfo.personal.getQuestsProgress()
            rankedResultsVO = composer.getResultsTeamsVO()
            event_dispatcher.showRankedBattleResultsWindow(rankedResultsVO, rankInfo, questsProgress, resultsWindow)
            self.__arenaBattleResultsWasShown.add(reusableInfo.arenaUniqueID)
        else:
            _logger.debug('Ranked Overlay windows will not be shown, received arenaBonusType: %s', arenaBonusType)

    def __onUpdateLeagueSync(self, _):
        if self.isAccountMastered() and not self.__webSeasonProvider.isStarted:
            self.__partialFlushRanksCache()
            self.__divisions = None
            self.__battlesGroups = None
            self.__webSeasonProvider.start()
            self.__soundManager.setProgressSound()
        return

    def __onUpdateRanked(self, _):
        self.__partialFlushRanksCache()
        self.__divisions = None
        self.__battlesGroups = None
        self.onUpdated()
        self.__resetTimer()
        return

    def __onUpdateRankedSettings(self, diff):
        if 'ranked_config' in diff:
            self.__rankedSettings = self.__getRankedSettings()
            self.__storeCycle()
            self.__statsComposer = RankedBattlesStatsComposer(self.__rankedSettings, self.__getCurrentOrPreviousSeason())
            self.__resizeRanksCache(self.__rankedSettings)
            self.__divisions = None
            self.__battlesGroups = None
            self.onUpdated()
            self.__resetTimer()
        return

    def __canShowRankedPage(self):
        isEnabled = self.isEnabled()
        hasCurSeason = self.getCurrentSeason() is not None
        hasPrevSeason = self.getPreviousSeason() is not None
        canShowSeasonOn = isEnabled and hasCurSeason
        canShowSeasonOff = isEnabled and not hasCurSeason and hasPrevSeason
        return canShowSeasonOn or canShowSeasonOff

    def __canShowSelectedPageID(self, ctx):
        selectedItemID = ctx.get('selectedItemID', '')
        if selectedItemID == RANKEDBATTLES_CONSTS.RANKED_BATTLES_YEAR_RATING_ID and not self.isYearLBEnabled():
            _logger.info("Can't open ranked battles page on year leaderboard tab.")
            return False
        elif selectedItemID == RANKEDBATTLES_CONSTS.RANKED_BATTLES_SHOP_ID and not self.isRankedShopEnabled():
            _logger.info("Can't open ranked battles page on ranked shop tab.")
            return False
        else:
            if selectedItemID == RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_ID and not self.isYearRewardEnabled():
                rewardsSelectedTab = ctx.get('rewardsSelectedTab', '')
                if rewardsSelectedTab == RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_YEAR_UI:
                    _logger.info("Can't open ranked battles page on year reward tab without year rewards.")
                    return False
                if self.getCurrentSeason() is None:
                    _logger.info("Can't open ranked battles page on rewards tab in season gap without year rewards.")
                    return False
            return True

    def __hasMatchMakerGroups(self, division, divisionLayout):
        matchMakerUnits = len(divisionLayout)
        amountRanks = len(division.getRanksIDs())
        return matchMakerUnits != amountRanks and matchMakerUnits <= MAX_GROUPS_IN_DIVISION

    def __hasPrimeTimesLeft(self, currTime):
        season = self.getCurrentSeason()
        if season is not None and season.hasActiveCycle(currTime):
            seasonEnd = season.getEndDate()
            peripheryIDs = self._getAllPeripheryIDs()
            for peripheryID, primeTime in self.getPrimeTimes().iteritems():
                if peripheryID in peripheryIDs and primeTime.getPeriodsBetween(currTime, seasonEnd):
                    return True

        return False

    def __getBonusSteps(self, lastProgress, currentProgress, maxAccRank, stepsToProgress, isBonusBattle=True):
        result = [ 0 for _ in range(maxAccRank) ]
        bonusBattlesMultiplier = self.getBonusBattlesMultiplier()
        lastID, lastSteps = lastProgress
        currentID, currentSteps = currentProgress
        if lastID == maxAccRank or currentProgress <= lastProgress or bonusBattlesMultiplier <= 0 or not isBonusBattle:
            return result
        totalSteps = currentSteps - lastSteps
        for rankID in range(lastID, currentID):
            totalSteps += stepsToProgress[rankID]

        bonusSteps = totalSteps - totalSteps // bonusBattlesMultiplier
        if currentSteps <= bonusSteps:
            result[currentID] = currentSteps
        else:
            result[currentID] = bonusSteps
        bonusSteps -= result[currentID]
        rankID = currentID - 1
        while bonusSteps > 0 and rankID >= 0:
            if stepsToProgress[rankID] <= bonusSteps:
                result[rankID] = stepsToProgress[rankID]
            else:
                result[rankID] = bonusSteps
            bonusSteps -= stepsToProgress[rankID]
            rankID -= 1

        return result

    def __getCurrentOrPreviousSeason(self):
        return self.getCurrentSeason() or self.getPreviousSeason()

    def __getDynamicShieldStatus(self, rankID, isCurrentRank, currentShield, prevShield):
        shieldsConfig = self.__rankedSettings.shields
        shieldConfig = shieldsConfig.get(rankID, None)
        if shieldConfig is None:
            return
        _, maxHP = shieldConfig
        shieldState = RANKEDBATTLES_ALIASES.SHIELD_DISABLED
        newShieldState = None
        if not isCurrentRank and currentShield is not None:
            hp, _ = currentShield
            if hp > 0:
                shieldState = RANKEDBATTLES_ALIASES.SHIELD_ENABLED
                newShieldState = RANKEDBATTLES_ALIASES.SHIELD_ENABLED
            return ShieldStatus(hp, hp, maxHP, shieldState, newShieldState)
        elif currentShield is not None:
            accPrevShieldHP, _ = prevShield
            hp, _ = currentShield
            if accPrevShieldHP is None:
                _logger.warning('Info about rank shield not available for %s in clientShields', rankID)
                accPrevShieldHP = hp
            if accPrevShieldHP == hp:
                if hp > 0:
                    shieldState = RANKEDBATTLES_ALIASES.SHIELD_ENABLED
                    newShieldState = RANKEDBATTLES_ALIASES.SHIELD_ENABLED
            elif accPrevShieldHP < hp:
                if accPrevShieldHP == 0:
                    shieldState = RANKEDBATTLES_ALIASES.SHIELD_FULL_RENEW
                    newShieldState = RANKEDBATTLES_ALIASES.SHIELD_ENABLED
                else:
                    shieldState = RANKEDBATTLES_ALIASES.SHIELD_RENEW
                    newShieldState = RANKEDBATTLES_ALIASES.SHIELD_ENABLED
            elif accPrevShieldHP > hp:
                if hp == 0:
                    shieldState = RANKEDBATTLES_ALIASES.SHIELD_LOSE
                    newShieldState = RANKEDBATTLES_ALIASES.SHIELD_DISABLED
                else:
                    shieldState = RANKEDBATTLES_ALIASES.SHIELD_LOSE_STEP
                    newShieldState = RANKEDBATTLES_ALIASES.SHIELD_ENABLED
            return ShieldStatus(accPrevShieldHP, hp, maxHP, shieldState, newShieldState)
        else:
            return

    def __getGroupsForBattle(self):
        if self.__battlesGroups is None:
            self.__battlesGroups = self.__buildGroupsForBattle()
        return self.__battlesGroups

    def getQuestsForRank(self, rankId):
        season = self.getCurrentSeason()
        return None if season is None else self.__eventsCache.getRankedQuests(lambda q: q.getRank() == rankId and q.isHidden() and q.isForRank() and q.getSeasonID() == season.getSeasonID())

    def __getRank(self, currentProgress, lastProgress, maxProgress, lastShield, shield, rankID, bonusSteps=None):
        stepsToProgress = self.__rankedSettings.accSteps
        rankIdx = rankID - 1
        stepsCount = 0
        bonusStepsCount = 0
        if rankIdx >= 0:
            stepsCount = stepsToProgress[rankIdx]
            bonusStepsCount = bonusSteps[rankIdx] if bonusSteps else None
        isCurrent = True if rankID == currentProgress[0] else False
        shieldStatus = self.__getDynamicShieldStatus(rankID, isCurrent, shield, lastShield)
        quests = self.getQuestsForRank(rankID)
        quests = quests.values() if quests is not None else None
        rank = Rank(division=self.getDivision(rankID), quests=quests, shield=shieldStatus, isUnburnable=(rankID in self.__rankedSettings.unburnableRanks), *self.__buildRank(rankID, stepsCount, bonusStepsCount, currentProgress, maxProgress, lastProgress))
        return rank

    def __getRankedDossier(self):
        return self.__itemsCache.items.getAccountDossier().getDossierDescr()['rankedSeasons']

    def __getRankedSettings(self):
        generalSettings = self.__serverSettings.rankedBattles
        cycleID = self.__getCurrentCycleID()
        for season in generalSettings.seasons.values():
            if cycleID in season.get('cycles', {}):
                return generalSettings.replace(season).replace(season['cycles'][cycleID])

        return generalSettings

    def __getCurrentCycleID(self):
        cycleID = None
        now = time_utils.getCurrentLocalServerTimestamp()
        _, cycleInfo = season_common.getSeason(self.__serverSettings.rankedBattles.asDict(), now)
        if cycleInfo:
            _, _, _, cycleID = cycleInfo
        return cycleID

    def __getTokensAmount(self, tokenName):
        tokenInfo = self.__itemsCache.items.tokens.getTokens().get(tokenName)
        if tokenInfo:
            _, count = tokenInfo
            return count

    def __clear(self):
        self.clearWebOpenPageCtx()
        self.stopNotification()
        self.stopGlobalListening()
        self.clearRankedWelcomeCallback()
        self.__webSeasonProvider.stop()
        self.__yearPositionProvider.stop()
        self.__soundManager.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __clearCaches(self):
        self.__ranksCache = [ None for _ in self.__ranksCache ]
        self.__divisions = None
        self.__battlesGroups = None
        return

    def __clearClientValues(self):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onUpdateRankedSettings
        self.__serverSettings = None
        self.__clientRank = DEFAULT_RANK
        self.__clientShields = {}
        self.__clientMaxRank = DEFAULT_RANK
        self.__clientWebSeasonInfo = UNDEFINED_WEB_INFO
        self.__clientWebSeasonInfoUpdateTime = None
        self.__clientEfficiency = None
        self.__clientEfficiencyDiff = None
        self.__clientBonusBattlesCount = None
        self.__clientValuesInited = False
        if self.__statsComposer:
            self.__statsComposer.clear()
            self.__statsComposer = None
        return

    def __buildDivisions(self):
        divisions = []
        maxPossibleRank = self.__rankedSettings.accRanks
        startRanks = sorted([ data['startRank'] for data in self.__rankedSettings.divisions.itervalues() if not data['isLeague'] ])
        numDivisions = len(startRanks)
        lastDivisionIdx = numDivisions - 1
        rank, _ = self.__itemsCache.items.ranked.accRank
        for i in range(numDivisions):
            firstRankInDivision = startRanks[i] + 1
            lastRankInDivision = startRanks[i + 1] if i < lastDivisionIdx else maxPossibleRank
            isFinal = i == lastDivisionIdx
            divisions.append(Division(i, firstRankInDivision, lastRankInDivision, rank, isFinal))

        if not divisions:
            divisions.append(Division(0, 1, maxPossibleRank, rank, True))
        return divisions

    def __buildGroupsForBattle(self):
        groups = self.__rankedSettings.rankGroups
        divisionsGroups = defaultdict(list)
        position = 0
        previousPosition = 0
        for ranksNum in groups:
            position += ranksNum
            maxRankInGroup = position - 1
            division = self.getDivision(maxRankInGroup)
            divisionID = division.getID()
            if maxRankInGroup == division.lastRank:
                divisionID += 1
            divisionsGroups[divisionID].append(range(previousPosition, position))
            previousPosition = position

        return divisionsGroups

    def __buildProgress(self, rankID, stepsCount, bonusStepsCount, currentProgress, maxProgress, lastProgress):
        result = []
        for stepID in reversed(range(1, stepsCount + 1)):
            stepState = RankState.UNDEFINED
            stepUniqueID = (rankID - 1, stepID)
            if stepUniqueID < currentProgress:
                stepState |= RankState.ACQUIRED
                if stepUniqueID > lastProgress:
                    stepState |= RankState.NEW_FOR_PLAYER
            elif stepUniqueID == currentProgress:
                stepState |= RankState.ACQUIRED | RankState.CURRENT
                if stepUniqueID > lastProgress:
                    stepState |= RankState.NEW_FOR_PLAYER
            else:
                stepState |= RankState.NOT_ACQUIRED
                if stepUniqueID <= lastProgress:
                    stepState |= RankState.NEW_FOR_PLAYER
            if currentProgress < stepUniqueID <= maxProgress:
                stepState |= RankState.LOST
            if bonusStepsCount > 0 and stepState & RankState.ACQUIRED:
                stepState |= RankState.BONUS
                bonusStepsCount -= 1
            result.append(RankStep(stepID, stepState))

        return RankProgress(result[::-1])

    def __buildRank(self, rankID, stepsCount, bonusStepsCount, currentProgress, maxProgress, lastProgress):
        currentRank, _ = currentProgress
        maxRank, _ = maxProgress
        lastRank, _ = lastProgress
        rankState = RankState.UNDEFINED
        if rankID < currentRank:
            rankState |= RankState.ACQUIRED
            if rankID > lastRank:
                rankState |= RankState.NEW_FOR_PLAYER
        elif rankID == currentRank:
            rankState |= RankState.ACQUIRED | RankState.CURRENT
            if rankID != lastRank:
                rankState |= RankState.NEW_FOR_PLAYER
        else:
            rankState |= RankState.NOT_ACQUIRED
            if rankID <= lastRank:
                rankState |= RankState.NEW_FOR_PLAYER
        if currentRank < rankID <= maxRank:
            rankState |= RankState.LOST
        progress = self.__buildProgress(rankID, stepsCount, bonusStepsCount, currentProgress, maxProgress, lastProgress)
        return (rankID, rankState, progress)

    def __openWebPageByCtx(self, ctx):
        url = alias = None
        selectedItemID = ctx.get('selectedItemID', '')
        clientParams = ctx.get('clientParams', {})
        clientParams['isLobbySub'] = True
        if selectedItemID == RANKEDBATTLES_CONSTS.RANKED_BATTLES_YEAR_RATING_ID and self.isYearLBEnabled():
            url = ranked_helpers.getRankedBattlesYearRatingUrl(**clientParams)
            alias = RANKEDBATTLES_ALIASES.RANKED_BATTLE_YEAR_RATING_LANDING
        elif selectedItemID == RANKEDBATTLES_CONSTS.RANKED_BATTLES_SHOP_ID and self.isRankedShopEnabled():
            url = ranked_helpers.getRankedBattlesShopUrl(**clientParams)
            alias = RANKEDBATTLES_ALIASES.RANKED_BATTLE_SHOP_LANDING
        if url and alias is not None:
            _showSeparateWebView(url, alias)
        return

    def __partialFlushRanksCache(self):
        leftFlushBorder = min(self.__clientRank[0], self.getCurrentRank()[0])
        leftFlushBorder = max(ZERO_RANK_ID, leftFlushBorder)
        rightFlushBorder = max(self.__clientRank[0], self.getCurrentRank()[0]) + 1
        rightFlushBorder = min(self.getMaxPossibleRank(), rightFlushBorder)
        for rankID in range(leftFlushBorder, rightFlushBorder + 1):
            self.__ranksCache[rankID] = None

        return

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()
        self.__timerTick()

    def __resizeRanksCache(self, settings):
        self.__ranksCache = [None] * (len(settings.accSteps) + ZERO_RANK_COUNT)
        return

    def __saveWebOpenPageCtx(self, ctx):
        if self.__rankedWebOpenPageCtx is not None:
            logging.error("Previous open ranked page web ctx wasn't processed. Too frequent requests from web.")
        self.__rankedWebOpenPageCtx = ctx if ctx.get('webParams', '') or ctx.get('clientParams', {}) else None
        return

    def __timerUpdate(self):
        status, _, _ = self.getPrimeTimeStatus()
        self.onGameModeStatusUpdated(status)

    def __timerTick(self):
        self.onGameModeStatusTick()

    def __updateSounds(self, isRankedSoundMode):
        if isRankedSoundMode != self.__isRankedSoundMode:
            self.__soundManager.onSoundModeChanged(isRankedSoundMode, Sounds.PROGRESSION_STATE_LEAGUES if self.isAccountMastered() else Sounds.PROGRESSION_STATE_DEFAULT)
            self.__isRankedSoundMode = isRankedSoundMode

    def __filterEnabledVehiclesCriteria(self, criteria):
        minLevel, maxLevel = self.getSuitableVehicleLevels()
        vehLevels = range(minLevel, maxLevel + 1)
        criteria = criteria | REQ_CRITERIA.VEHICLE.LEVELS(vehLevels)
        criteria |= ~REQ_CRITERIA.VEHICLE.CLASSES(self.__rankedSettings.forbiddenClassTags)
        criteria |= ~REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(self.__rankedSettings.forbiddenVehTypes)
        criteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE | ~REQ_CRITERIA.VEHICLE.EPIC_BATTLE
        return criteria

    def __showBetweenSeason(self):
        ctx = {'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID}
        self.showRankedBattlePage(ctx)

    def __showPreSeason(self):
        event_dispatcher.showRankedBattleIntro()

    def __showYearlyLeaders(self):
        ctx = {'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_YEAR_RATING_ID}
        self.showRankedBattlePage(ctx)

    def __storeCycle(self):
        lastCycleID = AccountSettings.getSettings(RANKED_LAST_CYCLE_ID)
        cycleID = self.__getCurrentCycleID()
        if not self.isEnabled() or cycleID is None:
            AccountSettings.setSettings(RANKED_LAST_CYCLE_ID, None)
        elif lastCycleID != cycleID:
            AccountSettings.setSettings(RANKED_LAST_CYCLE_ID, cycleID)
            setBattleTypeAsUnknown(SELECTOR_BATTLE_TYPES.RANKED)
        return
