# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/date_time.py
import time
import re
from gui.impl.gen import R
from gui.impl import backport
from constants import CURRENT_REALM
from soft_exception import SoftException
from gui.impl.gen.view_models.constants.date_time_formats import DateTimeFormatsEnum

def __getRealmLocale(path):
    accessor = path.dyn(CURRENT_REALM)
    return accessor() if accessor.isValid() else path()


class _MonthFormatKeys(object):
    FULL = '%B'
    FULL_D = '%Bd'
    FULL_S = '%Bs'
    ABBR = '%b'
    ABBR_D = '%bd'
    ABBR_S = '%bs'


class _WeekdayFormatKeys(object):
    FULL = '%A'
    ABBR = '%a'


class _TimeFormatKeys(object):
    SHORT = '%TIME'
    FULL = '%FULL_TIME'
    ALL = (SHORT, FULL)


_R_MONTHS = R.strings.menu.dateTime.months
_R_WEEKDAYS = R.strings.menu.dateTime.weekDays
_R_REG_DATE = R.strings.datetime_formats.regionalDate
_FORMAT_REXP = re.compile('%TIME|%FULL_TIME|%#?[a-zA-Z][ds]?')
_FORMAT_ARGS_DICT = {_TimeFormatKeys.SHORT: lambda ts: _getRegionalTime(ts, True),
 _TimeFormatKeys.FULL: lambda ts: _getRegionalTime(ts, False),
 _MonthFormatKeys.FULL: lambda ts: backport.text(_R_MONTHS.full.num(ts.tm_mon)()),
 _MonthFormatKeys.FULL_D: lambda ts: backport.text(_R_MONTHS.num(ts.tm_mon)()),
 _MonthFormatKeys.FULL_S: lambda ts: backport.text(_R_MONTHS.fullSmall.num(ts.tm_mon)()),
 _MonthFormatKeys.ABBR: lambda ts: backport.text(_R_MONTHS.short.num(ts.tm_mon)()),
 _MonthFormatKeys.ABBR_D: lambda ts: backport.text(_R_MONTHS.shortSmall.num(ts.tm_mon)()),
 _MonthFormatKeys.ABBR_S: lambda ts: backport.text(_R_MONTHS.shortSmall.num(ts.tm_mon)()),
 _WeekdayFormatKeys.FULL: lambda ts: backport.text(_R_WEEKDAYS.full.num(ts.tm_wday + 1)()),
 _WeekdayFormatKeys.ABBR: lambda ts: backport.text(_R_WEEKDAYS.short.num(ts.tm_wday + 1)())}
_DATE_TIME_FMT_MAP = {DateTimeFormatsEnum.DAYMONTHNUMERIC: __getRealmLocale(_R_REG_DATE.dayMonthNumeric),
 DateTimeFormatsEnum.DAYMONTHFULL: __getRealmLocale(_R_REG_DATE.dayMonthFull),
 DateTimeFormatsEnum.DAYMONTHFULLTIME: __getRealmLocale(_R_REG_DATE.dayMonthFullTime),
 DateTimeFormatsEnum.DAYMONTHABBREVIATED: __getRealmLocale(_R_REG_DATE.dayMonthAbbreviated),
 DateTimeFormatsEnum.DAYMONTHABBREVIATEDTIME: __getRealmLocale(_R_REG_DATE.dayMonthAbbreviatedTime),
 DateTimeFormatsEnum.SHORTDATE: __getRealmLocale(_R_REG_DATE.shortDate),
 DateTimeFormatsEnum.SHORTTIME: _TimeFormatKeys.SHORT,
 DateTimeFormatsEnum.SHORTDATETIME: __getRealmLocale(_R_REG_DATE.shortDateTime),
 DateTimeFormatsEnum.FULLDATE: __getRealmLocale(_R_REG_DATE.fullDate),
 DateTimeFormatsEnum.FULLTIME: _TimeFormatKeys.FULL,
 DateTimeFormatsEnum.FULLDATETIME: __getRealmLocale(_R_REG_DATE.fullDateTime)}

def _getRegionalTime(ts, isShort):
    hour = ts.tm_hour
    minute = ts.tm_min
    isWithMinutes = minute != 0
    isPm = hour >= 12
    shortFullLocale = R.strings.datetime_formats.regionalTime.short if isShort else R.strings.datetime_formats.regionalTime.full
    withMinutesLocale = shortFullLocale.withMinutes if isShort and isWithMinutes else shortFullLocale
    regionalFmt = backport.text(__getRealmLocale(withMinutesLocale.pm)) if isPm else backport.text(__getRealmLocale(withMinutesLocale.am))
    return formatTimeString(regionalFmt, ts)


def _fallbackArgHandler(specifier, ts):
    return time.strftime(specifier, ts)


def _expandTimeFmtArguments(rePattern, fmtStr, customArgsDict, ts):

    def replaceMatch(match):
        specifier = match.group(0)
        handler = customArgsDict.get(specifier, None)
        return handler(ts) if handler else _fallbackArgHandler(specifier, ts)

    return rePattern.sub(replaceMatch, fmtStr)


def formatTimeString(fmtStr, ts):
    return _expandTimeFmtArguments(_FORMAT_REXP, fmtStr, _FORMAT_ARGS_DICT, ts)


def getFormattedDateTime(timestamp, formatString, isConvertedToLocal=True):
    timeStructInLocal = time.localtime(timestamp) if isConvertedToLocal else time.gmtime(timestamp)
    return formatTimeString(formatString, timeStructInLocal)


def getRegionalDateTime(timestamp, dateTimeFormat, isConvertedToLocal=True):
    dateTimeFormatEnum = DateTimeFormatsEnum(dateTimeFormat)
    if dateTimeFormatEnum not in _DATE_TIME_FMT_MAP:
        raise SoftException('Provided date format constant is not present in format map')
    key = _DATE_TIME_FMT_MAP[dateTimeFormatEnum]
    return getFormattedDateTime(timestamp, key, isConvertedToLocal) if key in _TimeFormatKeys.ALL else getFormattedDateTime(timestamp, backport.text(key), isConvertedToLocal)
