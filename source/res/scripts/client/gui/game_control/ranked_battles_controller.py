# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/ranked_battles_controller.py
import logging
import typing
import operator
import sys
from collections import defaultdict
import BigWorld
import Event
import season_common
from adisp import process
from account_helpers import AccountSettings
from account_helpers.AccountSettings import RANKED_WEB_LEAGUE, RANKED_WEB_LEAGUE_UPDATE
from constants import ARENA_BONUS_TYPE, EVENT_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.periodic_battles.models import PrimeTime
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.prb_control.dispatcher import g_prbLoader
from gui.ranked_battles import ranked_helpers
from gui.ranked_battles.constants import PrimeTimeStatus, ZERO_RANK_ID, YEAR_POINTS_TOKEN, YEAR_AWARDS_ORDER, FINAL_QUEST_PATTERN, STANDARD_POINTS_COUNT, MAX_GROUPS_IN_DIVISION
from gui.ranked_battles.ranked_builders.postbattle_awards_vos import AwardBlock
from gui.ranked_battles.ranked_formatters import getRankedAwardsFormatter
from gui.ranked_battles.ranked_helpers.league_provider import RankedBattlesLeagueProvider, UNDEFINED_WEB_LEAGUE, UNDEFINED_LEAGUE_ID
from gui.ranked_battles.ranked_helpers.sound_manager import RankedSoundManager, Sounds
from gui.ranked_battles.ranked_helpers.stats_composer import RankedBattlesStatsComposer
from gui.ranked_battles.ranked_models import RankChangeStates, ShieldStatus, Division, RankedSeason, Rank, RankState, RankStep, RankProgress, RankData, BattleRankInfo
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.event_items import RankedQuest
from gui.shared import event_dispatcher, events, EVENT_BUS_SCOPE, g_eventBus
from gui.shared.money import Currency
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier, PeriodicNotifier
from helpers import dependency, time_utils
from predefined_hosts import g_preDefinedHosts, HOST_AVAILABILITY
from season_provider import SeasonProvider
from shared_utils import first, findFirst, collapseIntervals
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
    from gui.ranked_battles.constants import YearAwardsNames
ZERO_RANK_COUNT = 1
if typing.TYPE_CHECKING:
    from gui.ranked_battles.ranked_helpers.league_provider import WebLeague
    from season_common import GameSeason
    from gui.ranked_battles.ranked_models import PostBattleRankInfo
_logger = logging.getLogger(__name__)
DEFAULT_RANK = RankData(0, 0)

def _showRankedBattlePage(ctx):
    g_eventBus.handleEvent(events.LoadViewEvent(RANKEDBATTLES_ALIASES.RANKED_BATTLES_PAGE_ALIAS, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)


def _showRankedBattlePageSeasonOff(ctx):
    g_eventBus.handleEvent(events.LoadViewEvent(RANKEDBATTLES_ALIASES.RANKED_BATTLES_PAGE_SEASON_OFF_ALIAS, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)


class ShowRankedPageCallback(object):

    def __init__(self, ctx):
        self.__ctx = ctx

    def __call__(self, *args, **kwargs):
        _showRankedBattlePage(self.__ctx)


class RankedBattlesController(IRankedBattlesController, Notifiable, SeasonProvider, IGlobalListener):
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
        self._setSeasonSettingsProvider(self.__getCachedSettings)
        self.__rankedWelcomeCallback = None
        self.__clientValuesInited = False
        self.__clientRank = DEFAULT_RANK
        self.__clientShields = {}
        self.__clientMaxRank = DEFAULT_RANK
        self.__clientLeague = UNDEFINED_WEB_LEAGUE
        self.__clientLeagueUpdateTime = None
        self.__clientEfficiency = None
        self.__clientEfficiencyDiff = None
        self.__clientBonusBattlesCount = None
        self.__leagueProvider = RankedBattlesLeagueProvider()
        self.__isRankedSoundMode = False
        self.__soundManager = RankedSoundManager()
        self.__arenaBattleResultsWasShown = set()
        self.__ranksCache = []
        self.__divisions = None
        self.__serverSettings = None
        self.__rankedSettings = None
        self.__statsComposer = None
        self.__battlesGroups = None
        return

    def init(self):
        super(RankedBattlesController, self).init()
        self.addNotificator(SimpleNotifier(self.getTimer, self.__timerUpdate))
        self.addNotificator(PeriodicNotifier(self.getTimer, self.__timerTick))

    def fini(self):
        self.onUpdated.clear()
        self.onGameModeStatusTick.clear()
        self.onGameModeStatusUpdated.clear()
        self.onYearPointsChanges.clear()
        self.clearNotification()
        super(RankedBattlesController, self).fini()

    def onAccountBecomePlayer(self):
        self.__clearCaches()
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())
        self.__battleResultsService.onResultPosted += self.__showBattleResults

    def onAvatarBecomePlayer(self):
        if self.__serverSettings is None:
            self.__lobbyContext.onServerSettingsChanged += self.__onServerSettingsChanged
        self.__clearCaches()
        self.__clear()
        self.__battleResultsService.onResultPosted -= self.__showBattleResults
        return

    def onDisconnected(self):
        self.__clearCaches()
        self.__clearClientValues()
        self.__clear()
        self.__lobbyContext.onServerSettingsChanged -= self.__onServerSettingsChanged

    def onLobbyInited(self, event):
        self.__isRankedSoundMode = False
        self.__statsComposer = RankedBattlesStatsComposer(self.__rankedSettings, self.__getCurrentOrPreviousSeason())
        if not self.__clientValuesInited:
            self.__resizeRanksCache(self.__rankedSettings)
            self.__clientLeague = AccountSettings.getSettings(RANKED_WEB_LEAGUE)
            self.__clientLeagueUpdateTime = AccountSettings.getSettings(RANKED_WEB_LEAGUE_UPDATE)
            self.__leagueProvider.clear()
            self.updateClientValues()
            self.__clientValuesInited = True
        shouldInitPrefs = self.__clientLeague is None
        isDefinedLeague = not shouldInitPrefs and self.__clientLeague.league != UNDEFINED_LEAGUE_ID
        shouldFlushPrefs = isDefinedLeague and not self.isAccountMastered()
        if shouldInitPrefs or shouldFlushPrefs:
            self.__leagueProvider.clear()
            self.__clientLeague = UNDEFINED_WEB_LEAGUE
            self.__clientLeagueUpdateTime = None
            AccountSettings.setSettings(RANKED_WEB_LEAGUE, self.__clientLeague)
            AccountSettings.setSettings(RANKED_WEB_LEAGUE_UPDATE, self.__clientLeagueUpdateTime)
        if self.isAccountMastered() and not self.__leagueProvider.isStarted:
            self.__leagueProvider.start()
        self.__updateSounds()
        g_clientUpdateManager.addCallbacks({'ranked': self.__updateRanked,
         'ranked.accRank': self.__updateLeagueSync,
         'tokens': self.__onTokensUpdate})
        self.startNotification()
        self.startGlobalListening()
        return

    def onPrbEntitySwitched(self):
        self.__updateSounds()
        if self.isRankedPrbActive():
            self.updateClientValues()

    def isAvailable(self):
        return self.isEnabled() and not self.isFrozen() and self.getCurrentSeason() is not None

    def isAccountMastered(self):
        currentRank, _ = self.__itemsCache.items.ranked.accRank
        return currentRank == self.getMaxPossibleRank() != ZERO_RANK_ID

    def isEnabled(self):
        return self.__rankedSettings.isEnabled

    def isUnset(self):
        status, _, _ = self.getPrimeTimeStatus()
        return status == PrimeTimeStatus.NOT_SET

    def isFrozen(self):
        status, _, _ = self.getPrimeTimeStatus()
        return status == PrimeTimeStatus.FROZEN

    def isRankedPrbActive(self):
        return False if self.prbEntity is None else bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.RANKED)

    def hasAnySeason(self):
        return bool(self.__rankedSettings.seasons)

    def getRanksCount(self):
        return self.getMaxPossibleRank() + ZERO_RANK_COUNT

    def hasVehicleRankedBonus(self, compactDescr):
        items = self.__itemsCache.items
        return compactDescr not in items.stats.multipliedRankedVehicles and items.ranked.bonusBattlesCount > 0

    def hasSuitableVehicles(self):
        minLevel, maxLevel = self.getSuitableVehicleLevels()
        vehLevels = range(minLevel, maxLevel + 1)
        vehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(vehLevels))
        return len(vehs) > 0

    def clearRankedWelcomeCallback(self):
        self.__rankedWelcomeCallback = None
        return

    def getRankedWelcomeCallback(self):
        return self.__rankedWelcomeCallback

    def getBonusBattlesMultiplier(self):
        return self.__rankedSettings.bonusBattlesMultiplier

    def getClientRank(self):
        return self.__clientRank

    def getClientMaxRank(self):
        return self.__clientMaxRank

    def getClientShields(self):
        return self.__clientShields

    def getClientLeague(self):
        return self.__clientLeague

    def getClientLeagueUpdateTime(self):
        return self.__clientLeagueUpdateTime

    def getClientEfficiency(self):
        return self.__clientEfficiency

    def getClientEfficiencyDiff(self):
        return self.__clientEfficiencyDiff

    def getClientBonusBattlesCount(self):
        return self.__clientBonusBattlesCount

    def getCurrentDivision(self):
        return findFirst(operator.methodcaller('isCurrent'), self.getDivisions())

    def getCurrentRank(self):
        return RankData(*self.__itemsCache.items.ranked.accRank)

    def getCurrentSeason(self):
        now = time_utils.getCurrentLocalServerTimestamp()
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

    def getDivisions(self):
        if self.__divisions is None:
            self.__divisions = self.__buildDivisions()
        return self.__divisions

    def getExpectedSeasons(self):
        return self.__rankedSettings.expectedSeasons

    def getLeagueProvider(self):
        return self.__leagueProvider

    def getLeagueRewards(self, bonusName=None):
        now = time_utils.getCurrentLocalServerTimestamp()
        isCurrent, seasonInfo = season_common.getSeason(self.__rankedSettings.asDict(), now)
        result = []
        if isCurrent:
            _, _, seasonID, _ = seasonInfo
            seasonQuests = self.__eventsCache.getHiddenQuests(lambda q: q.getType() == EVENT_TYPE.TOKEN_QUEST and ranked_helpers.isRankedQuestID(q.getID()) and ranked_helpers.isSeasonTokenQuest(q.getID()))
            for qID in sorted(seasonQuests):
                season, leagueID, isSprinter = ranked_helpers.getDataFromSeasonTokenQuestID(qID)
                if season == seasonID and not isSprinter:
                    quest = seasonQuests[qID]
                    result.append({'league': leagueID,
                     'awards': quest.getBonuses(bonusName=bonusName)})

        return result

    def getYearRewards(self, points):
        quests = self.__eventsCache.getHiddenQuests()
        finalTokenQuest = quests.get(FINAL_QUEST_PATTERN.format(points))
        return finalTokenQuest.getBonuses() if finalTokenQuest else []

    def getMaxPossibleRank(self):
        return self.__rankedSettings.accRanks

    def getMaxRank(self):
        return RankData(*self.__itemsCache.items.ranked.maxRank)

    def getRank(self, rankID):
        return self.getRanksChain(rankID, rankID)[rankID]

    def getRanksChanges(self, isLoser=False):
        return self.__rankedSettings.loserRankChanges if isLoser else self.__rankedSettings.winnerRankChanges

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
                self.__ranksCache[rankID] = self.__createRank(currentProgress, lastProgress, maxProgress, lastShields.get(rankID), shields.get(rankID), rankID)

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
            cacheCopy[rankID] = self.__createRank(currentProgress, lastProgress, maxProgress, lastShields.get(rankID), shields.get(rankID), rankID, bonusStepsToProgress)

        return cacheCopy

    def getSoundManager(self):
        return self.__soundManager

    def getStatsComposer(self):
        return self.__statsComposer

    def getSuitableVehicleLevels(self):
        return (self.__rankedSettings.minLevel, self.__rankedSettings.maxLevel)

    def getTotalQualificationBattles(self):
        return self.__rankedSettings.qualificationBattles

    def getYearRewardPoints(self):
        yearPointToken = self.__itemsCache.items.tokens.getTokens().get(YEAR_POINTS_TOKEN)
        if yearPointToken:
            _, count = yearPointToken
            return count

    def getYearAwardsPointsMap(self):
        result = {}
        awardsMarks = self.__rankedSettings.yearAwardsMarks[:]
        awardsMarks.append(sys.maxint)
        for idx, name in enumerate(YEAR_AWARDS_ORDER):
            result[name] = (awardsMarks[idx], awardsMarks[idx + 1] - 1)

        return result

    def awardWindowShouldBeShown(self, rankChangeInfo):
        if rankChangeInfo.prevAccRank == ZERO_RANK_ID:
            return True
        if rankChangeInfo.accRank == self.getMaxPossibleRank():
            return True
        return True if rankChangeInfo.stepChanges > 0 and rankChangeInfo.prevMaxRank < rankChangeInfo.accRank else False

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
                    awardsSequence.append(AwardBlock(quest.getRank(), formatter.getFormattedBonuses(quest.getBonuses(), AWARDS_SIZES.BIG)))

            if awardsSequence:
                event_dispatcher.showRankedAwardWindow(awardsSequence=awardsSequence, rankedInfo=rankedInfo)
            return

    def showRankedBattlePage(self, ctx):
        if self.isEnabled() and self.getCurrentSeason() is not None:
            if not self.isRankedPrbActive():
                if not self.hasSuitableVehicles():
                    g_eventDispatcher.loadRankedUnreachable()
                    return
                self.__rankedWelcomeCallback = ShowRankedPageCallback(ctx)
                self.__switchForcedToRankedPrb()
            else:
                _showRankedBattlePage(ctx)
        else:
            prevSeason = self.getPreviousSeason()
            if prevSeason:
                ctx.update({'prevSeason': prevSeason})
                _showRankedBattlePageSeasonOff(ctx)
            else:
                _logger.error('There is no current or previous season to show RankedMainSeasonOn(Off)Page')
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

        if self.getLeagueProvider().webLeague.league != UNDEFINED_LEAGUE_ID:
            self.__clientLeague = self.getLeagueProvider().webLeague
            AccountSettings.setSettings(RANKED_WEB_LEAGUE, self.__clientLeague)
        if self.getLeagueProvider().lastUpdateTime is not None:
            self.__clientLeagueUpdateTime = self.getLeagueProvider().lastUpdateTime
            AccountSettings.setSettings(RANKED_WEB_LEAGUE_UPDATE, self.__clientLeagueUpdateTime)
        statsComposer = self.getStatsComposer()
        self.__clientEfficiency = statsComposer.currentSeasonEfficiency.efficiency
        self.__clientEfficiencyDiff = statsComposer.currentSeasonEfficiencyDiff
        self.__clientBonusBattlesCount = statsComposer.bonusBattlesCount
        return

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

    def getTimer(self):
        primeTimeStatus, timeLeft, _ = self.getPrimeTimeStatus()
        if primeTimeStatus != PrimeTimeStatus.AVAILABLE and not self.__connectionMgr.isStandalone():
            allPeripheryIDs = set([ host.peripheryID for host in g_preDefinedHosts.hostsWithRoaming() ])
            for peripheryID in allPeripheryIDs:
                peripheryStatus, peripheryTime, _ = self.getPrimeTimeStatus(peripheryID)
                if peripheryStatus == PrimeTimeStatus.NOT_AVAILABLE and peripheryTime < timeLeft:
                    timeLeft = peripheryTime

        seasonsChangeTime = self.getClosestStateChangeTime()
        currTime = time_utils.getCurrentLocalServerTimestamp()
        if seasonsChangeTime and (currTime + timeLeft > seasonsChangeTime or timeLeft == 0):
            timeLeft = seasonsChangeTime - currTime
        return timeLeft + 1 if timeLeft > 0 else time_utils.ONE_MINUTE

    def getPrimeTimes(self):
        primeTimes = self.__rankedSettings.primeTimes
        peripheryIDs = self.__rankedSettings.peripheryIDs
        primeTimesPeriods = defaultdict(lambda : defaultdict(list))
        for primeTime in primeTimes.itervalues():
            period = (primeTime['start'], primeTime['end'])
            weekdays = primeTime['weekdays']
            for pID in primeTime['peripheryIDs']:
                if pID not in peripheryIDs:
                    continue
                periphery = primeTimesPeriods[pID]
                for wDay in weekdays:
                    periphery[wDay].append(period)

        return {pID:PrimeTime(pID, {wDay:collapseIntervals(periods) for wDay, periods in pPeriods.iteritems()}) for pID, pPeriods in primeTimesPeriods.iteritems()}

    def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
        primeTimes = self.getPrimeTimes()
        dayStart, dayEnd = time_utils.getDayTimeBoundsForLocal(selectedTime)
        dayEnd += 1
        serversPeriodsMapping = {}
        hostsList = self.__getHostList()
        for _, _, serverShortName, _, peripheryID in hostsList:
            if peripheryID not in primeTimes:
                continue
            dayPeriods = primeTimes[peripheryID].getPeriodsBetween(dayStart, dayEnd)
            if groupIdentical and dayPeriods in serversPeriodsMapping.values():
                for name, period in serversPeriodsMapping.iteritems():
                    serverInMapping = name if period == dayPeriods else None
                    if serverInMapping:
                        newName = '{0}, {1}'.format(serverInMapping, serverShortName)
                        serversPeriodsMapping[newName] = serversPeriodsMapping.pop(serverInMapping)
                        break

            serversPeriodsMapping[serverShortName] = dayPeriods

        return serversPeriodsMapping

    def getPrimeTimeStatus(self, peripheryID=None):
        if peripheryID is None:
            peripheryID = self.__connectionMgr.peripheryID
        primeTime = self.getPrimeTimes().get(peripheryID)
        if primeTime is None:
            return (PrimeTimeStatus.NOT_SET, 0, False)
        elif not primeTime.hasAnyPeriods():
            return (PrimeTimeStatus.FROZEN, 0, False)
        else:
            season = self.getCurrentSeason()
            currTime = time_utils.getCurrentLocalServerTimestamp()
            if season and season.hasActiveCycle(currTime):
                isNow, timeTillUpdate = primeTime.getAvailability(currTime, season.getCycleEndDate())
            else:
                timeTillUpdate = 0
                if season:
                    nextCycle = season.getNextByTimeCycle(currTime)
                    if nextCycle:
                        primeTimeStart = primeTime.getNextPeriodStart(nextCycle.startDate, season.getEndDate(), includeBeginning=True)
                        if primeTimeStart:
                            timeTillUpdate = max(primeTimeStart, nextCycle.startDate) - currTime
                isNow = False
            return (PrimeTimeStatus.AVAILABLE, timeTillUpdate, isNow) if isNow else (PrimeTimeStatus.NOT_AVAILABLE, timeTillUpdate, False)

    def hasConfiguredPrimeTimeServers(self):
        return self.__hasPrimeStatusServer((PrimeTimeStatus.AVAILABLE, PrimeTimeStatus.NOT_AVAILABLE))

    def hasAvailablePrimeTimeServers(self):
        return self.__hasPrimeStatusServer((PrimeTimeStatus.AVAILABLE,))

    def getCurrentPointToCrystalRate(self):
        rate = 0
        bonuses = self.getYearRewards(STANDARD_POINTS_COUNT)
        for bonus in bonuses:
            if bonus.getName() == Currency.CRYSTAL:
                rate = bonus.getCount()

        return rate

    def calculateCompensation(self, points):
        pointMap = self.getYearAwardsPointsMap()
        awardPoints = 0
        for boxName in YEAR_AWARDS_ORDER:
            minPoints, _ = pointMap[boxName]
            if minPoints <= points:
                awardPoints = minPoints

        return points - awardPoints

    def getAwardTypeByPoints(self, points):
        pointMap = self.getYearAwardsPointsMap()
        awardType = None
        for boxName in YEAR_AWARDS_ORDER:
            minPoints, _ = pointMap[boxName]
            if minPoints <= points:
                awardType = boxName

        return awardType

    def _createSeason(self, cycleInfo, seasonData):
        return RankedSeason(cycleInfo, seasonData)

    @staticmethod
    def __buildProgress(rankID, stepsCount, bonusStepsCount, currentProgress, maxProgress, lastProgress):
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

    def __getCachedSettings(self):
        return self.__rankedSettings

    def __getRankedSettings(self):
        generalSettings = self.__serverSettings.rankedBattles
        cycleID = None
        now = time_utils.getCurrentLocalServerTimestamp()
        _, cycleInfo = season_common.getSeason(generalSettings.asDict(), now)
        if cycleInfo:
            _, _, _, cycleID = cycleInfo
        for season in generalSettings.seasons.values():
            if cycleID in season.get('cycles', {}):
                return generalSettings.replace(season).replace(season['cycles'][cycleID])

        return generalSettings

    def __hasPrimeStatusServer(self, states):
        if self.__connectionMgr.isStandalone():
            allPeripheryIDs = {self.__connectionMgr.peripheryID}
        else:
            allPeripheryIDs = set([ host.peripheryID for host in g_preDefinedHosts.hostsWithRoaming() ])
        for peripheryID in allPeripheryIDs:
            primeTimeStatus, _, _ = self.getPrimeTimeStatus(peripheryID)
            if primeTimeStatus in states:
                return True

        return False

    @process
    def __switchForcedToRankedPrb(self):
        result = yield g_prbLoader.getDispatcher().doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANKED))
        if not result:
            self.clearRankedWelcomeCallback()

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

    def __clear(self):
        self.stopNotification()
        self.stopGlobalListening()
        self.clearRankedWelcomeCallback()
        self.__leagueProvider.stop()
        self.__soundManager.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __clearCaches(self):
        self.__ranksCache = [ None for _ in self.__ranksCache ]
        self.__divisions = None
        self.__battlesGroups = None
        return

    def __clearClientValues(self):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateRankedSettings
        self.__serverSettings = None
        self.__clientRank = DEFAULT_RANK
        self.__clientShields = {}
        self.__clientMaxRank = DEFAULT_RANK
        self.__clientLeague = UNDEFINED_WEB_LEAGUE
        self.__clientLeagueUpdateTime = None
        self.__clientEfficiency = None
        self.__clientEfficiencyDiff = None
        self.__clientBonusBattlesCount = None
        self.__clientValuesInited = False
        if self.__statsComposer:
            self.__statsComposer.clear()
            self.__statsComposer = None
        return

    def __createRank(self, currentProgress, lastProgress, maxProgress, lastShield, shield, rankID, bonusStepsToProgress=None):
        stepsToProgress = self.__rankedSettings.accSteps
        rankIdx = rankID - 1
        stepsCount = 0
        bonusStepsCount = 0
        if rankIdx >= 0:
            stepsCount = stepsToProgress[rankIdx]
            bonusStepsCount = bonusStepsToProgress[rankIdx] if bonusStepsToProgress else None
        isCurrent = True if rankID == currentProgress[0] else False
        shieldStatus = self.__getDynamicShieldStatus(rankID, isCurrent, shield, lastShield)
        rank = Rank(division=self.getDivision(rankID), quest=self.__getQuestForRank(rankID), shield=shieldStatus, isUnburnable=(rankID in self.__rankedSettings.unburnableRanks), *self.__buildRank(rankID, stepsCount, bonusStepsCount, currentProgress, maxProgress, lastProgress))
        return rank

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

    def __getDivisionsList(self, division):
        return [division] if division is not None else self.getDivisions()

    def __getQuestForRank(self, rankId):
        season = self.getCurrentSeason()
        return None if season is None else first(self.__eventsCache.getRankedQuests(lambda q: q.getRank() == rankId and q.isHidden() and q.isForRank() and q.getSeasonID() == season.getSeasonID()).values())

    def __getRankedDossier(self):
        return self.__itemsCache.items.getAccountDossier().getDossierDescr()['rankedSeasons']

    def __onTokensUpdate(self, diff):
        if YEAR_POINTS_TOKEN in diff:
            self.onYearPointsChanges()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateRankedSettings
        self.__serverSettings = serverSettings
        self.__rankedSettings = self.__getRankedSettings()
        self.__serverSettings.onServerSettingsChange += self.__updateRankedSettings
        return

    def __partialFlushRanksCache(self):
        leftFlushBorder = min(self.__clientRank[0], self.getCurrentRank()[0])
        leftFlushBorder = max(ZERO_RANK_ID, leftFlushBorder)
        rightFlushBorder = max(self.__clientRank[0], self.getCurrentRank()[0]) + 1
        rightFlushBorder = min(self.getMaxPossibleRank(), rightFlushBorder)
        for rankID in range(leftFlushBorder, rightFlushBorder + 1):
            self.__ranksCache[rankID] = None

        return

    def __resizeRanksCache(self, settings):
        self.__ranksCache = [None] * (len(settings.accSteps) + ZERO_RANK_COUNT)
        return

    def __showBattleResults(self, reusableInfo, composer):
        arenaBonusType = reusableInfo.common.arenaBonusType
        arenaUniqueID = reusableInfo.arenaUniqueID
        if arenaBonusType == ARENA_BONUS_TYPE.RANKED and arenaUniqueID not in self.__arenaBattleResultsWasShown:
            self.updateClientValues()
            rankInfo = reusableInfo.personal.getRankInfo()
            questsProgress = reusableInfo.personal.getQuestsProgress()
            rankedResultsVO = composer.getResultsTeamsVO()
            event_dispatcher.showRankedBattleResultsWindow(rankedResultsVO, rankInfo, questsProgress)
            self.__arenaBattleResultsWasShown.add(reusableInfo.arenaUniqueID)
        else:
            _logger.debug('Ranked Overlay windows will not be shown, received arenaBonusType: %s', arenaBonusType)

    def __updateLeagueSync(self, _):
        if self.isAccountMastered() and not self.__leagueProvider.isStarted:
            self.__partialFlushRanksCache()
            self.__divisions = None
            self.__battlesGroups = None
            self.__leagueProvider.start()
            self.__soundManager.setProgressSound()
        return

    def __updateRanked(self, _):
        self.__partialFlushRanksCache()
        self.__divisions = None
        self.__battlesGroups = None
        self.onUpdated()
        self.__resetTimer()
        return

    def __updateRankedSettings(self, diff):
        if 'ranked_config' in diff:
            self.__rankedSettings = self.__getRankedSettings()
            self.__statsComposer = RankedBattlesStatsComposer(self.__rankedSettings, self.__getCurrentOrPreviousSeason())
            self.__resizeRanksCache(self.__rankedSettings)
            self.__divisions = None
            self.__battlesGroups = None
            self.onUpdated()
            self.__resetTimer()
        return

    def __updateSounds(self):
        isRankedSoundMode = self.isRankedPrbActive()
        if isRankedSoundMode != self.__isRankedSoundMode:
            self.__soundManager.onSoundModeChanged(isRankedSoundMode, Sounds.PROGRESSION_STATE_LEAGUES if self.isAccountMastered() else Sounds.PROGRESSION_STATE_DEFAULT)
            self.__isRankedSoundMode = isRankedSoundMode

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()
        self.__timerTick()

    def __timerUpdate(self):
        status, _, _ = self.getPrimeTimeStatus()
        self.onGameModeStatusUpdated(status)

    def __timerTick(self):
        self.onGameModeStatusTick()

    def __getHostList(self):
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming(), withShortName=True)
        if self.__connectionMgr.isStandalone():
            hostsList.insert(0, (self.__connectionMgr.url,
             self.__connectionMgr.serverUserName,
             self.__connectionMgr.serverUserNameShort,
             HOST_AVAILABILITY.IGNORED,
             0))
        return hostsList

    def __getCurrentOrPreviousSeason(self):
        return self.getCurrentSeason() or self.getPreviousSeason()

    def __getGroupsForBattle(self):
        if self.__battlesGroups is None:
            self.__battlesGroups = self.__makeGroupsForBattle()
        return self.__battlesGroups

    def __hasMatchMakerGroups(self, division, divisionLayout):
        matchMakerUnits = len(divisionLayout)
        amountRanks = len(division.getRanksIDs())
        return matchMakerUnits != amountRanks and matchMakerUnits <= MAX_GROUPS_IN_DIVISION

    def __makeGroupsForBattle(self):
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
