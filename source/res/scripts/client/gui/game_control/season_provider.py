# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/season_provider.py
from collections import defaultdict
from operator import itemgetter
import typing
import season_common
from shared_utils import first, findFirst
from skeletons.gui.game_control import ISeasonProvider
from helpers import time_utils, dependency
from shared_utils import collapseIntervals
from season_common import GameSeason
from gui.periodic_battles.models import PrimeTime, PeriodType, PeriodInfo, AlertData, PERIOD_TO_STANDALONE, PrimeTimeStatus
from predefined_hosts import g_preDefinedHosts, HOST_AVAILABILITY
from skeletons.connection_mgr import IConnectionManager

class SeasonProvider(ISeasonProvider):
    _ALERT_DATA_CLASS = AlertData
    __connectionMgr = dependency.descriptor(IConnectionManager)

    def isAvailable(self):
        return False

    def hasAnySeason(self):
        return bool(self.__getSeasonSettings().seasons)

    def hasAvailablePrimeTimeServers(self, now=None):
        return self._hasPrimeStatusServer((PrimeTimeStatus.AVAILABLE,), now)

    def hasConfiguredPrimeTimeServers(self, now=None):
        return self._hasPrimeStatusServer((PrimeTimeStatus.AVAILABLE, PrimeTimeStatus.NOT_AVAILABLE), now)

    def getCurrentCycleID(self):
        now = self.__getNow()
        isCurrent, seasonInfo = season_common.getSeason(self.__getSeasonSettings().asDict(), now)
        if isCurrent:
            _, _, _, cycleID = seasonInfo
            return cycleID
        else:
            return None

    def getCurrentSeason(self, now=None):
        now = now or self.__getNow()
        for seasonID, seasonData in self.__getSeasonSettings().seasons.iteritems():
            if seasonData['startSeason'] <= now < seasonData['endSeason']:
                currCycleInfo = (None,
                 None,
                 seasonID,
                 None)
                for cycleID, cycleTimes in seasonData['cycles'].iteritems():
                    if cycleTimes['start'] <= now < cycleTimes['end']:
                        currCycleInfo = (cycleTimes['start'],
                         cycleTimes['end'],
                         seasonID,
                         cycleID)

                return self._createSeason(currCycleInfo, seasonData)

        return

    def isWithinSeasonTime(self, seasonID):
        settings = self.__getSeasonSettings()
        return season_common.isWithinSeasonTime(settings.asDict(), seasonID, self.__getNow())

    def getClosestStateChangeTime(self, now=None):
        now = now or self.__getNow()
        season = self.getCurrentSeason(now)
        if season is not None:
            if season.hasActiveCycle(now):
                return season.getCycleEndDate()
            nextCycle = season.getNextByTimeCycle(now)
            if nextCycle:
                return nextCycle.startDate
            return season.getEndDate()
        else:
            season = self.getNextSeason(now)
            return season.getStartDate() if season else 0

    def getCurrentOrNextActiveCycleNumber(self, season):
        currTime = time_utils.getCurrentLocalServerTimestamp()
        if season.hasActiveCycle(currTime):
            return season.getCycleOrdinalNumber()
        else:
            cycle = season.getNextByTimeCycle(currTime)
            if cycle is None:
                cycle = season.getLastCycleInfo()
            return cycle.ordinalNumber if cycle else 0

    def getEventEndTimestamp(self):
        if self.hasPrimeTimesLeftForCurrentCycle():
            currServerTime = time_utils.getCurrentLocalServerTimestamp()
            actualSeason = self.getCurrentSeason() or self.getNextSeason()
            actualCycle = actualSeason.getCycleInfo() or actualSeason.getNextCycleInfo(currServerTime)
            lastPrimeTimeEnd = max([ period[1] for primeTime in self.getPrimeTimes().values() for period in primeTime.getPeriodsBetween(int(currServerTime), actualCycle.endDate) ])
            return lastPrimeTimeEnd
        else:
            return None

    def getCurrentCycleInfo(self):
        season = self.getCurrentSeason()
        if season is not None:
            if season.hasActiveCycle(time_utils.getCurrentLocalServerTimestamp()):
                return (season.getCycleEndDate(), True)
            return (season.getCycleStartDate(), False)
        else:
            return (None, False)

    def getNextSeason(self, now=None):
        now = now or self.__getNow()
        settings = self.__getSeasonSettings()
        seasonsComing = []
        for seasonID, season in settings.seasons.iteritems():
            startSeason = season['startSeason']
            if now < startSeason:
                seasonsComing.append((seasonID, startSeason))

        if seasonsComing:
            seasonID, _ = min(seasonsComing, key=itemgetter(1))
            return self.getSeason(seasonID)
        else:
            return None

    def getPeriodInfo(self, now=None, peripheryID=None):
        now = now or self.__getNow()
        if not self.hasAnySeason():
            return PeriodInfo(now, PeriodType.UNDEFINED)
        else:
            nextSeason = self.getNextSeason(now)
            currSeason = self.getCurrentSeason(now)
            prevSeason = self.getPreviousSeason(now)
            if currSeason is None:
                periodType = PeriodType.BETWEEN_SEASONS
                nextCycle = nextSeason.getFirstCycleInfo() if nextSeason is not None else None
                prevCycle = prevSeason.getLastCycleInfo() if prevSeason is not None else None
                if prevSeason is None:
                    periodType = PeriodType.BEFORE_SEASON
                elif nextSeason is None:
                    periodType = PeriodType.AFTER_SEASON
                return PeriodInfo(now, periodType, PeriodInfo.rightSeasonBorder(prevSeason), PeriodInfo.leftSeasonBorder(nextSeason), PeriodInfo.rightCycleBorder(prevCycle), PeriodInfo.leftCycleBorder(nextCycle))
            nextCycle = currSeason.getNextByTimeCycle(now)
            currCycle = currSeason.getCycleInfo()
            prevCycle = currSeason.getLastActiveCycleInfo(now)
            if currCycle is None:
                periodType = PeriodType.BETWEEN_CYCLES
                if prevCycle is None:
                    periodType = PeriodType.BEFORE_CYCLE
                elif nextCycle is None:
                    periodType = PeriodType.AFTER_CYCLE
                return PeriodInfo(now, periodType, PeriodInfo.leftSeasonBorder(currSeason), PeriodInfo.rightSeasonBorder(currSeason), PeriodInfo.rightCycleBorder(prevCycle), PeriodInfo.leftCycleBorder(nextCycle))
            periodType = PeriodType.AVAILABLE
            status, primeDelta, _ = self.getPrimeTimeStatus(now, peripheryID)
            if status in (PrimeTimeStatus.NOT_SET, PrimeTimeStatus.FROZEN):
                periodType = PeriodType.NOT_SET
                if not self.hasConfiguredPrimeTimeServers(now):
                    periodType = PeriodType.ALL_NOT_SET
                if status == PrimeTimeStatus.FROZEN:
                    periodType = PeriodType.FROZEN
            elif status == PrimeTimeStatus.NOT_AVAILABLE:
                timer = None
                periodType = PeriodType.NOT_AVAILABLE
                if not primeDelta:
                    primeDelta = timer = self.getTimer(now)
                    periodType = PeriodType.NOT_AVAILABLE_END
                if not self.hasAvailablePrimeTimeServers(now):
                    primeDelta = timer or self.getTimer(now)
                    periodType = PeriodType.ALL_NOT_AVAILABLE
                    if currCycle.endDate and now + primeDelta >= currCycle.endDate:
                        periodType = PeriodType.ALL_NOT_AVAILABLE_END
            if self.__connectionMgr.isStandalone():
                periodType = PERIOD_TO_STANDALONE.get(periodType, periodType)
            return PeriodInfo(now, periodType, PeriodInfo.leftSeasonBorder(currSeason), PeriodInfo.rightSeasonBorder(currSeason), PeriodInfo.leftCycleBorder(currCycle), PeriodInfo.rightCycleBorder(currCycle), primeDelta)

    def getPreviousSeason(self, now=None):
        seasonsPassed = self.getSeasonPassed(now)
        if seasonsPassed:
            seasonID, _ = max(seasonsPassed, key=itemgetter(1))
            return self.getSeason(seasonID)
        else:
            return None

    def getPrimeTimeStatus(self, now=None, peripheryID=None):
        if peripheryID is None:
            peripheryID = self.__connectionMgr.peripheryID
        primeTime = self.getPrimeTimes().get(peripheryID)
        if primeTime is None:
            return (PrimeTimeStatus.NOT_SET, 0, False)
        elif not primeTime.hasAnyPeriods():
            return (PrimeTimeStatus.FROZEN, 0, False)
        else:
            now = now or self.__getNow()
            season = self.getCurrentSeason(now)
            if season and season.hasActiveCycle(now):
                isNow, timeTillUpdate = primeTime.getAvailability(now, season.getCycleEndDate())
            else:
                isNow = False
                timeTillUpdate = 0
                if season:
                    nextCycle = season.getNextByTimeCycle(now)
                    if nextCycle:
                        primeTimeStart = primeTime.getNextPeriodStart(nextCycle.startDate, season.getEndDate(), includeBeginning=True)
                        if primeTimeStart:
                            timeTillUpdate = max(primeTimeStart, nextCycle.startDate) - now
            return (PrimeTimeStatus.AVAILABLE, timeTillUpdate, isNow) if isNow else (PrimeTimeStatus.NOT_AVAILABLE, timeTillUpdate, False)

    def getPrimeTimes(self):
        gameModeSettings = self.__getSeasonSettings()
        primeTimes = gameModeSettings.primeTimes
        peripheryIDs = gameModeSettings.peripheryIDs
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
        hostsList = self._getHostList()
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

    def getSeason(self, seasonID):
        settings = self.__getSeasonSettings()
        seasonCycleInfos = season_common.getAllSeasonCycleInfos(settings.asDict(), seasonID)
        seasonData = settings.seasons.get(seasonID, {})
        if seasonData:
            cycleInfo = first(seasonCycleInfos, (None,
             None,
             seasonID,
             None))
            return self._createSeason(cycleInfo, seasonData)
        else:
            return

    def getSeasonPassed(self, now=None):
        now = now or self.__getNow()
        settings = self.__getSeasonSettings()
        seasonsPassed = []
        for seasonID, season in settings.seasons.iteritems():
            endSeason = season['endSeason']
            if now >= endSeason:
                seasonsPassed.append((seasonID, endSeason))

        return seasonsPassed

    def getTimer(self, now=None):
        now = now or self.__getNow()
        primeTimeStatus, timeLeft, _ = self.getPrimeTimeStatus(now)
        if primeTimeStatus != PrimeTimeStatus.AVAILABLE and not self.__connectionMgr.isStandalone():
            for peripheryID in self._getAllPeripheryIDs():
                peripheryStatus, peripheryTime, _ = self.getPrimeTimeStatus(now, peripheryID)
                if peripheryStatus == PrimeTimeStatus.NOT_AVAILABLE and peripheryTime < timeLeft:
                    timeLeft = peripheryTime

        seasonsChangeTime = self.getClosestStateChangeTime(now)
        if seasonsChangeTime and (now + timeLeft > seasonsChangeTime or timeLeft == 0):
            timeLeft = seasonsChangeTime - now
        return timeLeft + 1 if timeLeft > 0 else 0

    def _getAlertBlockData(self):
        periodInfo = self.getPeriodInfo()
        return None if periodInfo.periodType in (PeriodType.AVAILABLE, PeriodType.UNDEFINED) else self._ALERT_DATA_CLASS.construct(periodInfo, self.__connectionMgr.serverUserNameShort)

    def isInPrimeTime(self):
        _, _, isNow = self.getPrimeTimeStatus()
        return isNow

    def isFrozen(self):
        status, _, _ = self.getPrimeTimeStatus()
        return status == PrimeTimeStatus.FROZEN

    def hasPrimeTimesLeftForCurrentCycle(self):
        currentCycleEndTime, isCycleActive = self.getCurrentCycleInfo()
        if not isCycleActive:
            return False
        primeTimes = self.getPrimeTimes()
        currentTime = time_utils.getCurrentLocalServerTimestamp()
        return findFirst(lambda primeTime: primeTime.getNextPeriodStart(currentTime, currentCycleEndTime), primeTimes.values(), default=False)

    def hasPrimeTimesPassedForCurrentCycle(self):
        season = self.getCurrentSeason()
        if season is not None:
            if season.hasActiveCycle(time_utils.getCurrentLocalServerTimestamp()):
                startDate = season.getStartDate()
                primeTimes = self.getPrimeTimes()
                currentTime = time_utils.getCurrentLocalServerTimestamp()
                return findFirst(lambda primeTime: bool(primeTime.getPeriodsBetween(startDate, currentTime, includeEnd=False)), primeTimes.values(), default=False)
        return False

    def _getHostList(self):
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming(), withShortName=True)
        if self.__connectionMgr.isStandalone():
            hostsList.insert(0, (self.__connectionMgr.url,
             self.__connectionMgr.serverUserName,
             self.__connectionMgr.serverUserNameShort,
             HOST_AVAILABILITY.IGNORED,
             0))
        return hostsList

    def _createSeason(self, cycleInfo, seasonData):
        return GameSeason(cycleInfo, seasonData)

    def _hasPrimeStatusServer(self, states, now=None):
        for peripheryID in self._getAllPeripheryIDs():
            primeTimeStatus, _, _ = self.getPrimeTimeStatus(now, peripheryID)
            if primeTimeStatus in states:
                return True

        return False

    def __getSeasonSettings(self):
        return self.getModeSettings()

    def _getAllPeripheryIDs(self):
        if self.__connectionMgr.isStandalone():
            return {self.__connectionMgr.peripheryID}
        return set([ host.peripheryID for host in g_preDefinedHosts.hostsWithRoaming() ])

    @staticmethod
    def __getNow():
        return time_utils.getCurrentLocalServerTimestamp()
