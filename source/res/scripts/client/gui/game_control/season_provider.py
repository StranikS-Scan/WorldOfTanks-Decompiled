# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/season_provider.py
from collections import defaultdict
from operator import itemgetter
import typing
import season_common
from shared_utils import first
from skeletons.gui.game_control import ISeasonProvider
from helpers import time_utils, dependency
from shared_utils import collapseIntervals
from season_common import GameSeason
from gui.periodic_battles.models import PrimeTime
from gui.ranked_battles.constants import PrimeTimeStatus
from predefined_hosts import g_preDefinedHosts, HOST_AVAILABILITY
from skeletons.connection_mgr import IConnectionManager

class SeasonProvider(ISeasonProvider):
    __connectionMgr = dependency.descriptor(IConnectionManager)

    def hasAnySeason(self):
        return bool(self.__getSeasonSettings().seasons)

    def getCurrentCycleID(self):
        now = self.__getNow()
        isCurrent, seasonInfo = season_common.getSeason(self.__getSeasonSettings().asDict(), now)
        if isCurrent:
            _, _, _, cycleID = seasonInfo
            return cycleID
        else:
            return None

    def getCurrentSeason(self):
        now = self.__getNow()
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

    def getNextSeason(self):
        now = self.__getNow()
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

    def getPreviousSeason(self):
        seasonsPassed = self.getSeasonPassed()
        if seasonsPassed:
            seasonID, _ = max(seasonsPassed, key=itemgetter(1))
            return self.getSeason(seasonID)
        else:
            return None

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

    def isWithinSeasonTime(self, seasonID):
        settings = self.__getSeasonSettings()
        return season_common.isWithinSeasonTime(settings.asDict(), seasonID, self.__getNow())

    def getSeasonPassed(self):
        now = self.__getNow()
        settings = self.__getSeasonSettings()
        seasonsPassed = []
        for seasonID, season in settings.seasons.iteritems():
            endSeason = season['endSeason']
            if now >= endSeason:
                seasonsPassed.append((seasonID, endSeason))

        return seasonsPassed

    def getClosestStateChangeTime(self):
        season = self.getCurrentSeason()
        now = self.__getNow()
        if season is not None:
            if season.hasActiveCycle(now):
                return season.getCycleEndDate()
            nextCycle = season.getNextByTimeCycle(now)
            if nextCycle:
                return nextCycle.startDate
            return season.getEndDate()
        else:
            season = self.getNextSeason()
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
        if self.hasPrimeTimesLeft():
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
        return timeLeft + 1 if timeLeft > 0 else 0

    def hasPrimeTimesLeft(self):
        season = self.getCurrentSeason()
        if season is not None and season.hasActiveCycle(int(self.__getNow())):
            seasonEnd = season.getEndDate()
            peripheryIDs = self.__getAllPeripheryIDs()
            for peripheryID, primeTime in self.getPrimeTimes().iteritems():
                if peripheryID in peripheryIDs and primeTime.getPeriodsBetween(int(self.__getNow()), seasonEnd):
                    return True

        return False

    def hasAvailablePrimeTimeServers(self):
        allPeripheryIDs = self.__getAllPeripheryIDs()
        for peripheryID in allPeripheryIDs:
            primeTimeStatus, _, _ = self.getPrimeTimeStatus(peripheryID)
            if primeTimeStatus == PrimeTimeStatus.AVAILABLE:
                return True

        return False

    def isInPrimeTime(self):
        _, _, isNow = self.getPrimeTimeStatus()
        return isNow

    def isFrozen(self):
        status, _, _ = self.getPrimeTimeStatus()
        return status == PrimeTimeStatus.FROZEN

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

    def __getSeasonSettings(self):
        return self.getModeSettings()

    def __getAllPeripheryIDs(self):
        if self.__connectionMgr.isStandalone():
            allPeripheryIDs = {self.__connectionMgr.peripheryID}
        else:
            allPeripheryIDs = {host.peripheryID for host in g_preDefinedHosts.hostsWithRoaming()}
        return allPeripheryIDs

    @staticmethod
    def __getNow():
        return time_utils.getCurrentLocalServerTimestamp()
