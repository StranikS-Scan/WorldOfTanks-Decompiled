# Embedded file name: scripts/client/helpers/time_utils.py
import time
import datetime
import calendar
import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG
from helpers import i18n
ONE_MINUTE = 60
QUARTER_HOUR = 15 * ONE_MINUTE
ONE_HOUR = 60 * ONE_MINUTE
ONE_DAY = 24 * ONE_HOUR
ONE_WEEK = 7 * ONE_DAY
HALF_YEAR = 183 * ONE_DAY
ONE_YEAR = 365 * ONE_DAY
WEEK_START = 1
WEEK_END = 7
WHOLE_DAY_INTERVAL = (1, ONE_DAY)

class _TimeCorrector(object):

    def __init__(self):
        self._evalTimeCorrection(time.time())

    def _evalTimeCorrection(self, serverUTCTime):
        self.__clientLoginTime = BigWorld.time()
        self.__serverLoginUTCTime = serverUTCTime

    def __loginDelta(self):
        return BigWorld.time() - self.__clientLoginTime

    timeCorrection = property(lambda self: self.serverUTCTime - time.time())
    serverUTCTime = property(lambda self: self.__serverLoginUTCTime + self.__loginDelta())

    @property
    def serverRegionalTime(self):
        regionalSecondsOffset = 0
        try:
            serverRegionalSettings = BigWorld.player().serverSettings['regional_settings']
            regionalSecondsOffset = serverRegionalSettings['starting_time_of_a_new_day']
        except Exception:
            LOG_CURRENT_EXCEPTION()

        return _g_instance.serverUTCTime + regionalSecondsOffset


_g_instance = _TimeCorrector()

def setTimeCorrection(serverUTCTime):
    _g_instance._evalTimeCorrection(serverUTCTime)


def makeLocalServerTime(serverTime):
    if serverTime:
        return serverTime - _g_instance.timeCorrection
    else:
        return None


def makeLocalServerDatetime(serverDatetime):
    if isinstance(serverDatetime, datetime.datetime):
        return serverDatetime - datetime.timedelta(seconds=_g_instance.timeCorrection)
    else:
        return None


def getServerRegionalTime():
    return _g_instance.serverRegionalTime


def getServerRegionalTimeCurrentDay():
    ts = time.gmtime(_g_instance.serverRegionalTime)
    return ts.tm_hour * ONE_HOUR + ts.tm_min * ONE_MINUTE + ts.tm_sec


def getServerRegionalWeekDay():
    return datetime.datetime.utcfromtimestamp(_g_instance.serverRegionalTime).isoweekday()


def getTimeDeltaFromNow(t):
    if t and datetime.datetime.utcfromtimestamp(t) > datetime.datetime.utcnow():
        delta = datetime.datetime.utcfromtimestamp(t) - datetime.datetime.utcnow()
        return delta.days * ONE_DAY + delta.seconds
    return 0


def getTimeDeltaTilNow(t):
    if t and datetime.datetime.utcnow() > datetime.datetime.utcfromtimestamp(t):
        delta = datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(t)
        return delta.days * ONE_DAY + delta.seconds
    return 0


def getTillTimeString(timeValue, keyNamespace):
    gmtime = time.gmtime(timeValue)
    if timeValue >= ONE_DAY:
        fmtKey = 'days'
        gmtime = time.gmtime(timeValue - ONE_DAY)
    elif ONE_DAY > timeValue >= ONE_HOUR:
        fmtKey = 'hours'
    else:
        fmtKey = 'min'
    fmtValues = {'day': str(time.struct_time(gmtime).tm_yday),
     'hour': time.strftime('%H', gmtime),
     'min': time.strftime('%M', gmtime),
     'sec': time.strftime('%S', gmtime)}
    return i18n.makeString(('%s/%s' % (keyNamespace, fmtKey)), **fmtValues)


def getCurrentTimestamp():
    return time.time()


def getTimeStructInUTC(timestamp):
    return time.gmtime(timestamp)


def getTimeStructInLocal(timestamp):
    return time.localtime(timestamp)


def getTimestampFromUTC(timeStructInUTC):
    return calendar.timegm(timeStructInUTC)


def getTimestampFromLocal(timeStructInLocal):
    return time.mktime(timeStructInLocal)


def getDateTimeInUTC(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp)


def getDateTimeInLocal(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


def utcToLocalDatetime(dateTimeInUTC):
    return getDateTimeInLocal(getTimestampFromUTC(dateTimeInUTC.timetuple()))


def localToUtcDateTime(dateTimeInLocal):
    return getDateTimeInUTC(getTimestampFromLocal(dateTimeInLocal.timetuple()))


def isFuture(timestamp):
    return getCurrentTimestamp() < timestamp


def isPast(timestamp):
    return getCurrentTimestamp() > timestamp


def isToday(timestamp):
    todayStart, todayEnd = getDayTimeBounds(getCurrentTimestamp())
    return todayStart <= timestamp <= todayEnd


def getDayTimeBounds(timestamp = None):
    if timestamp is not None:
        dateTime = getDateTimeInLocal(timestamp)
    else:
        dateTime = datetime.datetime.now()
    return (_getTimestampForUTC(dateTime.year, dateTime.month, dateTime.day), _getTimestampForUTC(dateTime.year, dateTime.month, dateTime.day, 23, 59, 59))


def isTimeThisDay(timestamp):
    start, end = getDayTimeBounds()
    return start <= timestamp <= end


def isTimeNextDay(timestamp):
    return isTimeThisDay(timestamp - ONE_DAY)


def getTimeTodayForUTC(hour = 0, minute = 0, second = 0, microsecond = 0):
    date = datetime.datetime.now()
    return _getTimestampForUTC(date.year, date.month, date.day, hour, minute, second, microsecond)


def getTimeTodayForLocal(hour = 0, minute = 0, second = 0, microsecond = 0):
    date = datetime.datetime.now()
    return _getTimestampForLocal(date.year, date.month, date.day, hour, minute, second, microsecond)


class ActivityIntervalsIterator(object):

    def __init__(self, currentTime, currentDay, weekDays = None, timeIntervals = None):
        self._currentTime = currentTime
        self._currentDay = currentDay
        self._timeIntervals = timeIntervals or [WHOLE_DAY_INTERVAL]
        self._weekDays = weekDays or set(range(WEEK_START, WEEK_END + 1))
        self._timeLeft = 0

    def __iter__(self):
        return self

    def next(self):
        interval = None
        if self._currentDay in self._weekDays:
            interval = self.__trySearchValidTimeInterval(self._currentTime)
        if interval is not None:
            self._timeLeft += interval[0] - self._currentTime
            self._currentTime = interval[1]
        else:
            self._currentDay += 1
            self._timeLeft += ONE_DAY - self._currentTime
            while True:
                if self._currentDay > WEEK_END:
                    self._currentDay = WEEK_START
                if self._currentDay in self._weekDays:
                    break
                self._currentDay += 1
                self._timeLeft += ONE_DAY

            interval = self.__trySearchValidTimeInterval(0)
            if interval is not None:
                self._timeLeft += interval[0]
                self._currentTime = interval[1]
            else:
                self._currentTime = 0
                interval = WHOLE_DAY_INTERVAL
        timeLeft = self._timeLeft
        self._timeLeft += interval[1] - interval[0]
        return (timeLeft, interval)

    def __trySearchValidTimeInterval(self, curTime):
        for low, high in self._timeIntervals:
            if curTime < high:
                return (low, high)

        return None


class DaysAvailabilityIterator(object):

    def __init__(self, currentTimestamp, weekDaysToExclude = None, intervalsToExclude = None, minDelta = 0):
        self._weekDaysToExclude = weekDaysToExclude or ()
        self._intervalsToExclude = intervalsToExclude or ()
        self._currentDay = 0
        self._currentTimestamp = currentTimestamp
        self._minDelta = minDelta

    def __iter__(self):
        return self

    def next(self):
        while True:
            currentGMTime = getDateTimeInUTC(self._currentTimestamp)
            currentLocalTimestamp = time.time()
            if self._currentTimestamp - currentLocalTimestamp >= self._minDelta and currentGMTime.isoweekday() not in self._weekDaysToExclude and self._checkIntervals(self._currentTimestamp):
                start, finish = getDayTimeBounds(currentLocalTimestamp)
                if finish < self._currentTimestamp:
                    self._currentDay = max(1, int((self._currentTimestamp - finish) / ONE_DAY))
                break
            self._currentDay += 1
            self._currentTimestamp += ONE_DAY

        return (self._currentDay, self._currentTimestamp)

    def _checkIntervals(self, timeStamp):
        for start, finish in self._intervalsToExclude:
            if start <= timeStamp <= finish:
                return False

        return True


def _getTimestampForUTC(year, month, day, hour = 0, minute = 0, second = 0, microsecond = 0):
    return getTimestampFromUTC((year,
     month,
     day,
     hour,
     minute,
     second,
     microsecond))


def _getTimestampForLocal(year, month, day, hour = 0, minute = 0, second = 0, microsecond = 0):
    return getTimestampFromLocal(datetime.datetime(year, month, day, hour, minute, second, microsecond).timetuple())
