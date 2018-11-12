# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/season_common.py
import time
from typing import Dict, Optional, Any, List
from collections import namedtuple
from constants import IS_CLIENT

class CycleStatus(object):
    PAST = 'past'
    CURRENT = 'current'
    FUTURE = 'future'


class GameSeasonCycle(namedtuple('GameSeasonCycle', 'ID, status, startDate, endDate, ordinalNumber')):

    def __cmp__(self, other):
        return cmp(self.ID, other.ID)


class GameSeason(object):

    def __init__(self, seasonInfo, seasonData):
        self.__cycleStartDate, self.__cycleEndDate, self.__seasonId, self.__cycleID = seasonInfo
        self.__data = seasonData
        self.__cycles = None
        return

    def hasActiveCycle(self, now):
        return self.__cycleStartDate <= now < self.__cycleEndDate

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

    def getCycleInfo(self):
        return None if not self.getCycleID() else self.getAllCycles()[self.getCycleID()]

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
            self.__cycles[idx] = self._buildCycle(idx, status, cycleRawData['start'], cycleRawData['end'], number)

        return

    def _buildCycle(self, idx, status, start, end, number):
        return GameSeasonCycle(idx, status, start, end, number)


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
