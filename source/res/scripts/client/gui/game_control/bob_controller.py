# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/bob_controller.py
import logging
from collections import defaultdict
import typing
import Event
import season_common
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.bob.bob_constants import BOB_TOKEN_PREFIX
from gui.bob.bob_helpers import getTeamIDFromTeamToken
from gui.bob.bob_requesters import TeamSkillsRequester, TeamsRequester
from gui.marathon.marathon_constants import ZERO_TIME
from gui.periodic_battles.models import PrimeTime
from gui.prb_control import prbEntityProperty
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.shared.gui_items.processors.common import BobRewardClaimer
from gui.shared.prime_time_constants import PrimeTimeStatus
from gui.shared.utils import decorators
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from helpers import dependency, time_utils
from predefined_hosts import g_preDefinedHosts, HOST_AVAILABILITY
from season_provider import SeasonProvider
from shared_utils import collapseIntervals, first, findFirst
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IBobController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class BobController(IBobController, Notifiable, SeasonProvider):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        super(BobController, self).__init__()
        self._setSeasonSettingsProvider(self.getConfig)
        self.__serverSettings = None
        self.__bobConfig = None
        self.__eventsManager = Event.EventManager()
        self.onPrimeTimeStatusUpdated = Event.Event(self.__eventsManager)
        self.onUpdated = Event.Event(self.__eventsManager)
        self.onTokensUpdated = Event.Event(self.__eventsManager)
        self.__teamSkillsRequester = TeamSkillsRequester(self)
        self.__teamsRequester = TeamsRequester(self)
        self.__lastOpenedBobUrl = ''
        return

    def init(self):
        super(BobController, self).init()
        self.addNotificator(SimpleNotifier(self.__getTimer, self.__timerUpdate))
        self.addNotificator(SimpleNotifier(self.getClosestStateChangeTime, self.__updateStates))

    def fini(self):
        self.__clear()
        self.clearNotification()
        self.__teamSkillsRequester.stop()
        self.__teamsRequester.stop()
        super(BobController, self).fini()

    def getCurrentSeason(self):
        isCycleActive, seasonInfo = season_common.getSeason(self.getConfig().asDict(), time_utils.getCurrentLocalServerTimestamp())
        if isCycleActive:
            _, _, seasonID, _ = seasonInfo
            return season_common.GameSeason(seasonInfo, self.getConfig().seasons.get(seasonID, {}))
        else:
            return None

    @property
    def teamTokens(self):
        return self.getConfig().teamTokens

    @property
    def leaderTokens(self):
        return self.getConfig().leaderTokens

    @property
    def pointsToken(self):
        return self.getConfig().pointsToken

    @property
    def tokenToClaimPersonalReward(self):
        return self.getConfig().claimPersonalRewardToken

    @property
    def personalRewardQuestName(self):
        return self.getConfig().personalRewardQuest

    @property
    def teamRewardQuestPrefix(self):
        return self.getConfig().teamRewardQuestPrefix

    @property
    def personalLevel(self):
        return self.getTeamLevelTokensCount() + 1

    @property
    def lactOpenedBobUrl(self):
        return self.__lastOpenedBobUrl

    @lactOpenedBobUrl.setter
    def lactOpenedBobUrl(self, value):
        self.__lastOpenedBobUrl = value

    @property
    def leaderTokenFirstType(self):
        return self.getConfig().leaderTokenFirstType

    @property
    def teamsChannelName(self):
        return self.getConfig().teamsChannel

    @property
    def teamSkillsChannelName(self):
        return self.getConfig().teamSkillsChannel

    @property
    def teamsRequester(self):
        return self.__teamsRequester

    @property
    def teamSkillsRequester(self):
        return self.__teamSkillsRequester

    @prbEntityProperty
    def prbEntity(self):
        return None

    def onLobbyStarted(self, ctx):
        super(BobController, self).onLobbyStarted(ctx)
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdated})
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__updateBobSettings
        self.__tryToStartRequesters()

    def onDisconnected(self):
        self.__clear()
        self.clearNotification()
        self.__teamSkillsRequester.stop()
        self.__teamsRequester.stop()
        super(BobController, self).onDisconnected()

    def onAvatarBecomePlayer(self):
        self.__clear()
        self.__teamSkillsRequester.suspend()
        self.__teamsRequester.suspend()
        super(BobController, self).onAvatarBecomePlayer()

    def onAccountBecomePlayer(self):
        self.__resetTimer()
        self.__teamSkillsRequester.resume()
        self.__teamsRequester.resume()
        super(BobController, self).onAccountBecomePlayer()

    def isEnabled(self):
        return self.__lobbyContext.getServerSettings().bobConfig.isEnabled

    def isFrozen(self):
        return False if findFirst(lambda primeTime: primeTime.hasAnyPeriods(), self.getPrimeTimes().values()) else True

    def isModeActive(self):
        return self.isEnabled() and bool(self.getCurrentSeason())

    def isRegistrationEnabled(self):
        return self.isEnabled() and self.isRegistrationPeriodEnabled()

    def isRegistrationPeriodEnabled(self):
        startTime, endTime = self.getTimeTillRegistrationStartOrEnd()
        return startTime <= ZERO_TIME < endTime

    def isRegistered(self):
        return bool(self.__getTeamToken())

    def isPlayerBlogger(self):
        token = findFirst(self.__itemsCache.items.tokens.getToken, self.leaderTokens)
        return token is not None

    def isPostEventTime(self):
        return self.isEnabled() and not self.isRegistrationEnabled() and self.getSeasonPassed()

    def needShowEventTab(self):
        return self.isEnabled() and not (self.isPostEventTime() and not self.isRegistered()) and not self.__isPreRegistration()

    def getPlayerPoints(self):
        return self.__itemsCache.items.tokens.getTokenCount(self.pointsToken)

    def getReceivedTeamRewards(self):
        if not self.getConfig().teamRewardTokenPrefix:
            _logger.warning('Bob config has not teamReward -> rewardTokenPrefix.')
            return 0
        teamRewardTokenPrefix = self.getConfig().teamRewardTokenPrefix
        return len([ tokenID for tokenID in self.__itemsCache.items.tokens.getTokens().keys() if tokenID.startswith(teamRewardTokenPrefix) ])

    def isAvailable(self):
        return self.isEnabled() and not self.isFrozen() and self.getCurrentSeason() is not None

    def isValidBattleType(self):
        return False if self.prbEntity is None else bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.BOB)

    def getConfig(self):
        return self.__lobbyContext.getServerSettings().bobConfig

    def getCurrentTeamID(self):
        return getTeamIDFromTeamToken(self.__getTeamToken())

    def getPrimeTimes(self):
        if not self.hasAnySeason():
            return {}
        config = self.getConfig()
        primeTimes = config.primeTimes
        peripheryIDs = config.peripheryIDs
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
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming(), withShortName=True)
        if self.__connectionMgr.peripheryID == 0:
            hostsList.insert(0, (self.__connectionMgr.url,
             self.__connectionMgr.serverUserName,
             self.__connectionMgr.serverUserNameShort,
             HOST_AVAILABILITY.IGNORED,
             0))
        primeTimes = self.getPrimeTimes()
        dayStart, dayEnd = time_utils.getDayTimeBoundsForLocal(selectedTime)
        dayEnd += 1
        serversPeriodsMapping = {}
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
            season = self.getCurrentSeason() or self.getNextSeason()
            currTime = time_utils.getServerUTCTime()
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

    def hasAvailablePrimeTimeServers(self):
        if self.__connectionMgr.isStandalone():
            allPeripheryIDs = {self.__connectionMgr.peripheryID}
        else:
            allPeripheryIDs = set([ host.peripheryID for host in g_preDefinedHosts.hostsWithRoaming() ])
        for peripheryID in allPeripheryIDs:
            primeTimeStatus, _, _ = self.getPrimeTimeStatus(peripheryID)
            if primeTimeStatus == PrimeTimeStatus.AVAILABLE:
                return True

        return False

    def hasAnyPeripheryWithPrimeTime(self):
        if not self.isAvailable():
            return False
        currentSeason = self.getCurrentSeason()
        currentTime = time_utils.getServerUTCTime()
        endTime = currentSeason.getCycleEndDate()
        for primeTime in self.getPrimeTimes().itervalues():
            if primeTime.hasAnyPeriods():
                isAvailable, _ = primeTime.getAvailability(currentTime, endTime)
                if isAvailable:
                    return True

        return False

    @decorators.process('bob/claimReward')
    def claimReward(self, token):
        result = yield BobRewardClaimer(token).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def getAvailablePersonalRewardCount(self):
        return self.__itemsCache.items.tokens.getTokenCount(self.getConfig().addPersonalRewardToken)

    def getTeamLevelTokensCount(self):
        return self.__itemsCache.items.tokens.getTokenCount(self.getConfig().teamLevelToken)

    def getClosestStateChangeTime(self):
        seasonClosestTime = super(BobController, self).getClosestStateChangeTime()
        seasonClosestTime = seasonClosestTime - time_utils.getServerUTCTime()
        seasonClosestTimes = [seasonClosestTime] if seasonClosestTime > 0 else []
        if seasonClosestTimes:
            timeLeft = min(seasonClosestTimes)
            return timeLeft + 1

    def isBobPointsToken(self, tokenID):
        return tokenID.startswith(self.pointsToken) if self.pointsToken else False

    def isAllZeroScore(self):
        return all((teamData.score == 0 for teamData in self.teamsRequester.getTeamsList())) if not self.teamsRequester.isCacheEmpty() else False

    def getTimeTillRegistrationStartOrEnd(self):
        config = self.getConfig()
        if config.registration:
            startTimeLeft = config.registration['start'] - time_utils.getServerUTCTime()
            startTimeLeft = startTimeLeft if startTimeLeft > 0 else ZERO_TIME
            endTimeLeft = config.registration['end'] - time_utils.getServerUTCTime()
            endTimeLeft = endTimeLeft if endTimeLeft > 0 else ZERO_TIME
            return (startTimeLeft, endTimeLeft)
        return (ZERO_TIME, ZERO_TIME)

    def __onSyncCompleted(self, _, diff):
        if 'bob' in diff:
            self.__updateStates()

    def __updateStates(self):
        self.onUpdated()

    def __getTeamToken(self):
        return first(set(self.__itemsCache.items.tokens.getTokens().keys()) & self.teamTokens)

    def __updateBobSettings(self, diff):
        if 'bob_config' in diff:
            self.__updateStates()
            self.__resetTimer()

    def __onTokensUpdated(self, diff):
        if any((tokenID.startswith(BOB_TOKEN_PREFIX) for tokenID in diff)):
            self.__tryToStartRequesters()
            self.onTokensUpdated()

    def __clear(self):
        self.stopNotification()
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__updateBobSettings
        self.__eventsManager.clear()
        self.__lastOpenedBobUrl = ''

    def __getTimer(self):
        _, timeLeft, _ = self.getPrimeTimeStatus()
        return timeLeft + 1 if timeLeft > 0 else time_utils.ONE_MINUTE

    def __resetTimer(self):
        self.startNotification()
        self.__updateStates()
        self.__timerUpdate()

    def __timerUpdate(self):
        status, _, _ = self.getPrimeTimeStatus()
        self.onPrimeTimeStatusUpdated(status)

    def __isPreRegistration(self):
        startTimeLeft, _ = self.getTimeTillRegistrationStartOrEnd()
        isRegistrationInFuture = ZERO_TIME < startTimeLeft
        return isRegistrationInFuture

    def __tryToStartRequesters(self):
        self.__teamSkillsRequester.start()
        self.__teamsRequester.start()
