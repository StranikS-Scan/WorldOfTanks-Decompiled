# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/event_boards/event_boards_timer.py
import BigWorld
import time
import datetime
from helpers import time_utils
FORMAT_EMPTY_STR = ''
FORMAT_DAY_STR = 'day'
FORMAT_HOUR_STR = 'hour'
FORMAT_MINUTE_STR = 'minute'
FORMAT_TOMORROW_STR = 'tomorrow'
FORMAT_TODAY_STR = 'today'
FORMAT_YESTERDAY_STR = 'yesterday'

def getTimeStampFromDate(strDate):
    return int(time_utils.getTimestampFromUTC(_stringToStruct(strDate)))


def isPeripheryActiveAtCurrentMoment(primeTime):
    """
    Check is periphery active and return timestamp to start and end periphery activation
    """
    currentTimeUTC = _getCurrentUTCTime()
    if primeTime.getStartTime() and primeTime.getEndTime():
        prStartTimeUTC, prEndTimeUTC = _calculatePeripheryTimeHelper(currentTimeUTC, primeTime)
        active = prStartTimeUTC <= currentTimeUTC <= prEndTimeUTC
        return (active, int((prStartTimeUTC - currentTimeUTC).total_seconds()), int((prEndTimeUTC - currentTimeUTC).total_seconds()))
    return (False, 0, 0)


def getPeripheryTime(primeTime):
    currentTimeUTC = _getCurrentUTCTime()
    prStartTimeUTC, prEndTimeUTC = _calculatePeripheryTimeHelper(currentTimeUTC, primeTime)
    dateStartTimestamp = int(time_utils.getTimestampFromUTC(prStartTimeUTC.utctimetuple()))
    dateEndTimestamp = int(time_utils.getTimestampFromUTC(prEndTimeUTC.utctimetuple()))
    return (BigWorld.wg_getShortTimeFormat(dateStartTimestamp), BigWorld.wg_getShortTimeFormat(dateEndTimestamp))


def isCurrentTimeInPeriod(strStartDate, strEndDate):
    """
    :param strStartDate: UTC date represents as string (2017-01-22T23:23:00)
    :param strEndDate: UTC date represents as string (2017-01-22T23:23:00)
    """
    if strStartDate and strEndDate:
        endDate = getTimeStampFromDate(strEndDate)
        startDate = getTimeStampFromDate(strStartDate)
        currentTime = _getCurrentUTCTime()
        return startDate <= int(time_utils.getTimestampFromUTC(currentTime.timetuple())) <= endDate
    return False


def isPeriodCloseToEnd(strStartDate, strEndDate, percents=0.1):
    """
    :param strStartDate: UTC date represents as string (2017-01-22T23:23:00)
    :param strEndDate: UTC date represents as string (2017-01-22T23:23:00)
    :param percents: percents to end value (1..100)
    
    according to confluence: https://confluence.wargaming.net/pages/viewpage.action?pageId=473439182
    """
    if strStartDate and strEndDate:
        periodTime = getTimeStampFromDate(strEndDate) - getTimeStampFromDate(strStartDate)
        if periodTime >= 0:
            periodTime *= percents
            currentTimeUTC = _getCurrentUTCTime()
            currentTimestampUTC = int(time_utils.getTimestampFromUTC(currentTimeUTC.timetuple()))
            endDate = _stringToStruct(strEndDate)
            dtime = int(time_utils.getTimestampFromUTC(endDate)) - currentTimestampUTC
            if periodTime >= dtime >= 0 or dtime < 0:
                return True
    return False


def getFormattedRemainingTime(strEndDate, isRoundUp=False):
    """
    :param strEndDate: UTC date represents as string (2017-01-22T23:23:00)
    :param isRoundUp: round up time
    based on time_utils.getTillTimeString()
    get numeric data (days left, hours left etc) and string with id data (day, hour, minute)
    according to confluence: https://confluence.wargaming.net/pages/viewpage.action?pageId=463366746
    TLEL-02
    """
    if strEndDate:
        endDate = _stringToStruct(strEndDate)
        endDate = time_utils.getTimestampFromUTC(endDate)
        currentTimeUTC = _getCurrentUTCTime()
        currentTimestampUTC = time_utils.getTimestampFromUTC(currentTimeUTC.timetuple())
        dtime = endDate - currentTimestampUTC
        if dtime >= 0 and dtime != float('inf'):
            return _remainingTimeToEndHelper(dtime, isRoundUp)
    return (0, FORMAT_EMPTY_STR)


def getTimeStatus(strDate):
    """
    :param strDate: UTC date represents as string (2017-01-22T23:23:00)
    
    get numeric data (+days left, +hours left etc) if it before current time
    or numeric data (-days left, -hours left etc) if it after current time
    and string with id data (day, hour, minute)
    """
    if strDate:
        value, txtid = getFormattedRemainingTime(strDate, False)
        if txtid:
            return (value, txtid)
        endDate = _stringToStruct(strDate)
        endDate = time_utils.getTimestampFromUTC(endDate)
        currentTimeUTC = _getCurrentUTCTime()
        currentTimestampUTC = time_utils.getTimestampFromUTC(currentTimeUTC.timetuple())
        dtime = endDate - currentTimestampUTC
        if dtime < 0:
            value, txtid = _remainingTimeToEndHelper(-dtime, False)
            if txtid:
                return (-value, txtid)
    return (0, FORMAT_EMPTY_STR)


def getUpdateStatus_ts(tsUpdateDate):
    """
    get string with update status: 'today', 'yesterday' or 'tomorrow'
    according to confluence: https://confluence.wargaming.net/display/WGCGK/Excel+View#ExcelView-5
    paragraph 5
    
    :param tsUpdateDate: UTC date represents as timestamp (1259453)
    """
    if tsUpdateDate is not None:
        currentTime = _getCurrentUTCTime()
        currentTimestamp = int(time_utils.getTimestampFromUTC(currentTime.timetuple()))
        currDayStart, currDayEnd = time_utils.getDayTimeBoundsForUTC(tsUpdateDate)
        if currDayStart - time_utils.ONE_DAY <= currentTimestamp <= currDayEnd - time_utils.ONE_DAY:
            return FORMAT_TOMORROW_STR
        if currDayStart <= currentTimestamp <= currDayEnd:
            return FORMAT_TODAY_STR
        if currDayStart + time_utils.ONE_DAY <= currentTimestamp <= currDayEnd + time_utils.ONE_DAY:
            return FORMAT_YESTERDAY_STR
    return


def getDayMonthYear(strDate):
    """
    get (day, month, year) from date ('2017-01-22T13:15:00' -> 22, 1, 2017)
    
    :param strDate : UTC date represents as string (2017-01-22T13:15:00)
    """
    if strDate:
        dateLocal = time.localtime(getTimeStampFromDate(strDate))
        return (dateLocal.tm_mday, dateLocal.tm_mon, dateLocal.tm_year)


def getShortTimeString(strDate):
    """
    get string with short time format (01:15 AM)
    
    :param strDate : UTC date represents as string (2017-01-22T13:15:00)
    """
    if strDate:
        dateTimestamp = getTimeStampFromDate(strDate)
        return BigWorld.wg_getShortTimeFormat(dateTimestamp)
    return FORMAT_EMPTY_STR


def getShortTimeString_ts(tsDate):
    """
    get string with short time format (01:15 AM)
    
    :param tsDate : UTC date represents as timestamp (1000000)
    """
    return BigWorld.wg_getShortTimeFormat(tsDate)


def _remainingTimeToEndHelper(dtime, isRoundUp):
    lctime = time.localtime(dtime)
    if isRoundUp and lctime.tm_sec > 0:
        dtime += time_utils.ONE_MINUTE
    if dtime >= time_utils.ONE_DAY:
        lctime = time.localtime(dtime - time_utils.ONE_DAY)
        return (time.struct_time(lctime).tm_yday, FORMAT_DAY_STR)
    if dtime >= time_utils.ONE_HOUR:
        return (int(dtime / time_utils.ONE_HOUR), FORMAT_HOUR_STR)
    return (int(dtime / time_utils.ONE_MINUTE), FORMAT_MINUTE_STR) if dtime >= 0 else (0, FORMAT_EMPTY_STR)


def _getCurrentUTCTime():
    return time_utils.getDateTimeInUTC(time_utils.getServerUTCTime())


def getCurrentUTCTimeTs():
    return time_utils.getServerUTCTime()


def _stringToStruct(strDate):
    return time.strptime(strDate, '%Y-%m-%dT%H:%M:%S')


def _calculatePeripheryTimeHelper(baseTimeUTC, primeTimes):
    """
    This function converts periphery string 'h:m' format data to datetime format based on baseTimeUTC
    and return normalized to baseTimeUTC periphery start and end time
    """
    peripheryStartTimeUTC = time.strptime(primeTimes.getStartTime(), '%H:%M:%S')
    peripheryEndTimeUTC = time.strptime(primeTimes.getEndTime(), '%H:%M:%S')
    peripheryStartTimeUTC = baseTimeUTC.replace(hour=peripheryStartTimeUTC.tm_hour, minute=peripheryStartTimeUTC.tm_min, second=0, microsecond=0)
    peripheryEndTimeUTC = baseTimeUTC.replace(hour=peripheryEndTimeUTC.tm_hour, minute=peripheryEndTimeUTC.tm_min, second=0, microsecond=0)
    if peripheryStartTimeUTC > peripheryEndTimeUTC:
        shiftedStartTimeUTC = peripheryStartTimeUTC - datetime.timedelta(days=1)
        if shiftedStartTimeUTC <= baseTimeUTC <= peripheryEndTimeUTC:
            peripheryStartTimeUTC = shiftedStartTimeUTC
        else:
            peripheryEndTimeUTC += datetime.timedelta(days=1)
    if baseTimeUTC > peripheryEndTimeUTC and baseTimeUTC > peripheryStartTimeUTC:
        peripheryEndTimeUTC += datetime.timedelta(days=1)
        peripheryStartTimeUTC += datetime.timedelta(days=1)
    return (peripheryStartTimeUTC, peripheryEndTimeUTC)
