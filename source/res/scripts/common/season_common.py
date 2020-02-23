# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/season_common.py
from typing import Dict, Optional, Any, List
from collections import namedtuple

class CycleStatus(object):
    PAST = 'past'
    CURRENT = 'current'
    FUTURE = 'future'


class GameSeasonCycle(namedtuple('GameSeasonCycle', 'ID, status, startDate, endDate, ordinalNumber, announceOnly')):

    def __cmp__(self, other):
        return cmp(self.ID, other.ID)

    def getEpicCycleNumber(self):
        return int(self.ID % 100)


class GameSeason(object):

    def __init__(self, cycleInfo, seasonData):
        self.__cycleStartDate, self.__cycleEndDate, self.__seasonId, self.__cycleID = cycleInfo
        self.__data = seasonData
        self.__cycles = None
        return

    def hasActiveCycle(self, now):
        return self.__cycleStartDate <= now < self.__cycleEndDate

    def isLastCycle(self, cycleID):
        return self.getLastCycleInfo().ordinalNumber == self.getCycleInfo(cycleID).ordinalNumber

    def getSeasonID(self):
        return self.__seasonId

    def getCycleID(self):
        return self.__cycleID

    def getStartDate(self):
        return self.__data['startSeason']

    def getEndDate(self):
        return self.__data['endSeason']

    def getAllCycles(self):
        if self.__cycles is None:
            self._buildCycles()
        return self.__cycles

    def getCycleInfo(self, cycleID=None):
        if cycleID is None:
            cycleID = self.getCycleID()
        return self.getAllCycles().get(cycleID, None) if cycleID is not None else None

    def getNextCycleInfo(self, now, cycleID=None):
        if cycleID is None:
            cycleID = self.getCycleID() or self.getLastActiveCycleID(now)
        cycles = self.getAllCycles()
        if cycleID and cycleID in cycles:
            currentCycleOrdinalNumber = cycles[cycleID].ordinalNumber
            for cycle in sorted(cycles.values(), key=lambda c: c.ordinalNumber):
                if cycle.ordinalNumber > currentCycleOrdinalNumber:
                    return cycle

        return

    def getNextByTimeCycle(self, now):
        cycles = self.getAllCycles()
        for cycle in sorted(cycles.values(), key=lambda c: c.startDate):
            if cycle.startDate >= now:
                return cycle

        return None

    def getLastCycleInfo(self):
        lastCycleID = max(self.getAllCycles().iterkeys())
        return self.getAllCycles()[lastCycleID] if lastCycleID else None

    def getLastActiveCycleInfo(self, now):
        lastCycle = None
        if self.hasActiveCycle(now):
            return self.getCycleInfo()
        else:
            for cycle in self.getAllCycles().values():
                if cycle.endDate > now:
                    continue
                if lastCycle is None or lastCycle.endDate < cycle.endDate:
                    lastCycle = cycle

            return lastCycle

    def getLastActiveCycleID(self, now):
        cycleInfo = self.getLastActiveCycleInfo(now)
        return cycleInfo.ID if cycleInfo else None

    def getCycleStartDate(self):
        return self.__cycleStartDate

    def getCycleEndDate(self):
        return self.__cycleEndDate

    def getCycleOrdinalNumber(self):
        return self.getCycleInfo().ordinalNumber

    def getPassedCyclesNumber(self):
        return sum((1 for cycle in self.getAllCycles().values() if cycle.status == CycleStatus.PAST))

    def getNumber(self):
        return self.__data.get('number')

    def getUserName(self):
        return str(self.getNumber())

    def _buildCycles(self):
        cycles = self.__data.get('cycles', {})
        currID = self.getCycleID()
        self.__cycles = {}
        for number, idx in enumerate(sorted(cycles.keys()), 1):
            cycleRawData = cycles[idx]
            if idx < currID or currID is None:
                status = CycleStatus.PAST
            elif idx == currID:
                status = CycleStatus.CURRENT
            else:
                status = CycleStatus.FUTURE
            self.__cycles[idx] = self._buildCycle(idx, status, cycleRawData['start'], cycleRawData['end'], number, bool(cycleRawData.get('announce', False)))

        return

    def _buildCycle(self, idx, status, start, end, number, announceOnly):
        return GameSeasonCycle(idx, status, start, end, number, announceOnly)


def getSeason(config, now):
    if not config or not config.get('isEnabled', False) or not config.get('cycleTimes', []):
        return (False, None)
    else:
        now = int(now)
        for cycleInfo in config['cycleTimes']:
            startTime, endTime, seasonID, _ = cycleInfo
            if now >= endTime:
                if cycleInfo == config['cycleTimes'][-1] and isWithinSeasonTime(config, seasonID, now):
                    return (False, (None,
                      None,
                      seasonID,
                      None))
                continue
            cycleActive = now >= startTime
            if not cycleActive and not isWithinSeasonTime(config, seasonID, now):
                return (False, None)
            return (cycleActive, cycleInfo)

        return (False, None)


def getAllSeasonCycleInfos(config, inSeasonID):
    cycleInfoList = []
    for cycleInfo in config['cycleTimes']:
        _, _, seasonID, _ = cycleInfo
        if inSeasonID == seasonID:
            cycleInfoList.append(cycleInfo)

    return cycleInfoList


def getSeasonCycleInfo(config, inCycleID):
    for cycleInfo in config['cycleTimes']:
        _, _, _, cycleID = cycleInfo
        if inCycleID == cycleID:
            return cycleInfo

    return None


def isWithinSeasonTime(config, seasonID, now):
    if not config or not config.get('isEnabled', False) or not config.get('cycleTimes', []):
        return False
    seasons = config.get('seasons', {})
    seasonData = seasons.get(seasonID, None)
    if seasonData is not None:
        now = int(now)
        startTime = seasonData['startSeason']
        endTime = seasonData['endSeason']
        return startTime <= now < endTime
    else:
        return False


def getActiveCycleConfig(config, now):
    res, cycleInfo = getSeason(config, now)
    if not res:
        return None
    else:
        _, _, seasonID, cycleID = cycleInfo
        season = config['seasons'].get(seasonID)
        if not season:
            return None
        cycle = season['cycles'].get(cycleID)
        return cycle


def getDateFromCycleID(cycleID):
    cycleIDStr = str(cycleID)
    year = int(cycleIDStr[:4])
    month = int(cycleIDStr[4:6])
    day = int(cycleIDStr[6:8])
    return (year, month, day)


def getDateFromSeasonID(seasonID):
    cycleIDStr = str(seasonID)
    year = int(cycleIDStr[:4])
    month = int(cycleIDStr[4:6])
    return (year, month)


def getSeasonNumber(config, seasonID):
    seasons = config.get('seasons', {})
    if not seasons:
        return
    else:
        seasonData = seasons.get(seasonID, None)
        return seasonData.get('number', None)
