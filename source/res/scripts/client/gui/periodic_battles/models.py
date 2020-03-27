# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/periodic_battles/models.py
from collections import namedtuple
from helpers import time_utils
from shared_utils import collapseIntervals, findFirst, first

class PrimeTime(object):

    def __init__(self, peripheryID, periods=None):
        super(PrimeTime, self).__init__()
        self.__peripheryID = peripheryID
        self.__periods = periods or {}

    def hasAnyPeriods(self):
        return bool(self.__periods)

    def getAvailability(self, forTime, cycleEnd):
        periods = self.getPeriodsBetween(forTime, cycleEnd)
        if periods:
            periodsIter = iter(periods)
            currentPeriod = findFirst(lambda (pS, pE): pS <= forTime < pE, periodsIter)
            if currentPeriod is not None:
                _, currentPeriodEnd = currentPeriod
                return (True, currentPeriodEnd - forTime)
            nextPeriod = first(periods)
            if nextPeriod is not None:
                nextPeriodStart, _ = nextPeriod
                return (False, nextPeriodStart - forTime)
        return (False, 0)

    def getNextPeriodStart(self, fromTime, tillTime, includeBeginning=False):
        periods = self.getPeriodsBetween(fromTime, tillTime, includeBeginning=includeBeginning)
        if periods:
            nextPeriod = first(periods)
            if nextPeriod is not None:
                nextPeriodStart, _ = nextPeriod
                return nextPeriodStart
        return

    def getPeriodsActiveForTime(self, periodTime, preferPeriodBounds=False):
        return self.getPeriodsBetween(periodTime, periodTime, preferPeriodBounds=preferPeriodBounds)

    def getPeriodsBetween(self, startTime, endTime, includeBeginning=True, includeEnd=True, preferPeriodBounds=False):
        periods = []
        startDateTime = time_utils.getDateTimeInUTC(startTime)
        startTimeDayStart, _ = time_utils.getDayTimeBoundsForUTC(startTime)
        weekDay = startDateTime.isoweekday()
        while startTimeDayStart <= endTime:
            if weekDay in self.__periods:
                for (startH, startM), (endH, endM) in self.__periods[weekDay]:
                    periodStartTime = startTimeDayStart + startH * time_utils.ONE_HOUR + startM * time_utils.ONE_MINUTE
                    periodEndTime = startTimeDayStart + endH * time_utils.ONE_HOUR + endM * time_utils.ONE_MINUTE
                    if startTime < periodEndTime and periodStartTime <= endTime:
                        if not includeBeginning and startTime > periodStartTime:
                            continue
                        if not includeEnd and endTime < periodEndTime:
                            continue
                        if preferPeriodBounds:
                            periods.append((periodStartTime, periodEndTime))
                        else:
                            periods.append((max(startTime, periodStartTime), min(endTime, periodEndTime)))

            if weekDay == time_utils.WEEK_END:
                weekDay = time_utils.WEEK_START
            else:
                weekDay += 1
            startTimeDayStart += time_utils.ONE_DAY

        return collapseIntervals(periods)


CalendarStatusVO = namedtuple('CalendarStatusVO', ('alertIcon', 'buttonIcon', 'buttonLabel', 'buttonVisible', 'buttonTooltip', 'statusText', 'popoverAlias', 'bgVisible', 'shadowFilterVisible', 'tooltip'))
