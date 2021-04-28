# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/weekend_brawl_controller.py
import typing
from collections import defaultdict
import Event
from CurrentVehicle import g_currentVehicle
from constants import AUTH_REALM, WEEKEND_BRAWL_CONFIG
from gui.prb_control import prbEntityProperty
from gui.ranked_battles.constants import PrimeTimeStatus
from gui.periodic_battles.models import PrimeTime
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency, time_utils
from predefined_hosts import g_preDefinedHosts, HOST_AVAILABILITY
from season_provider import SeasonProvider
from shared_utils import collapseIntervals
from skeletons.gui.game_control import IWeekendBrawlController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.connection_mgr import IConnectionManager

class WeekendBrawlController(IWeekendBrawlController, Notifiable, SeasonProvider):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        super(WeekendBrawlController, self).__init__()
        self._setSeasonSettingsProvider(self.getConfig)
        self.__serverSettings = None
        self.__wBrawlConfig = None
        self.onPrimeTimeStatusUpdated = Event.Event()
        self.onUpdated = Event.Event()
        return

    def init(self):
        super(WeekendBrawlController, self).init()
        self.addNotificator(SimpleNotifier(self.__getTimer, self.__timerUpdate))
        self.addNotificator(SimpleNotifier(self.getClosestStateChangeTime, self.__updateStates))

    def fini(self):
        self.onUpdated.clear()
        self.onPrimeTimeStatusUpdated.clear()
        self.clearNotification()
        self.__clear()
        super(WeekendBrawlController, self).fini()

    @prbEntityProperty
    def prbEntity(self):
        return None

    def getCurrentRealm(self):
        return AUTH_REALM

    def onLobbyStarted(self, ctx):
        super(WeekendBrawlController, self).onLobbyStarted(ctx)
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
        self.__onSyncCompleted()

    def onDisconnected(self):
        self.__clear()
        super(WeekendBrawlController, self).onDisconnected()

    def onAvatarBecomePlayer(self):
        self.__clear()
        super(WeekendBrawlController, self).onAvatarBecomePlayer()

    def onAccountBecomePlayer(self):
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())
        super(WeekendBrawlController, self).onAccountBecomePlayer()

    def isEnabled(self):
        return self.__lobbyContext.getServerSettings().weekendBrawl.isEnabled

    def isModeActive(self):
        return self.isEnabled() and self.getCurrentSeason()

    def isAvailable(self):
        return self.isEnabled() and not self.isFrozen() and self.getCurrentSeason() is not None

    def getConfig(self):
        return self.__wBrawlConfig

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

    def getSuitableVehicles(self):
        requiredLevel = self.getConfig().levels
        vehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(requiredLevel))
        return vehs

    def hasSuitableVehicles(self):
        return bool(self.getSuitableVehicles())

    def isSuitableVehicle(self):
        return g_currentVehicle.item and g_currentVehicle.item.level in self.__wBrawlConfig.levels

    def isFrozen(self):
        for primeTime in self.getPrimeTimes().values():
            if primeTime.hasAnyPeriods():
                return False

        return True

    def getClosestStateChangeTime(self):
        seasonClosestTime = super(WeekendBrawlController, self).getClosestStateChangeTime()
        seasonClosestTime = seasonClosestTime - time_utils.getServerUTCTime()
        seasonClosestTimes = [seasonClosestTime] if seasonClosestTime > 0 else []
        if seasonClosestTimes:
            timeLeft = min(seasonClosestTimes)
            return timeLeft + 1

    def __onSyncCompleted(self, *args):
        self.onUpdated()

    def __updateStates(self):
        self.onUpdated()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateWeekendBrawlSettings
        self.__serverSettings = serverSettings
        self.__wBrawlConfig = self.__serverSettings.weekendBrawl
        self.__serverSettings.onServerSettingsChange += self.__updateWeekendBrawlSettings
        self.__resetTimer()
        return

    def __updateWeekendBrawlSettings(self, diff):
        if WEEKEND_BRAWL_CONFIG in diff:
            self.__wBrawlConfig = self.__serverSettings.weekendBrawl
            self.onUpdated()
            self.__resetTimer()

    def __clear(self):
        self.stopNotification()
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateWeekendBrawlSettings
        self.__serverSettings = None
        return

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
