# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/date_time.py
import re
import time
import enum
from gui.impl.gen import R
from gui.impl import backport
from constants import CURRENT_REALM
from soft_exception import SoftException
from gui.shared.utils.functions import replaceMultiple
from gui.impl.gen.view_models.constants.date_time_formats import DateTimeFormatsEnum

class _MonthFormatKeysEnum(enum.Enum):
    FULL = '%B'
    ABBREVIATED = '%b'


class _WeekdayFormatKeysEnum(enum.Enum):
    FULL = '%A'
    ABBREVIATED = '%a'


__FORMAT_STRING_WITH_TIME = '{}, {}'

def __getRealmLocale(path):
    accessor = path.dyn(CURRENT_REALM)
    return accessor() if accessor.isValid() else path()


def __getRegionalTime(timestamp, isShort):
    timeStructInLocal = time.localtime(timestamp)
    isWithMinutes = True if timeStructInLocal.tm_min != 0 else False
    isPm = timeStructInLocal.tm_hour >= 12
    shortFullLocale = R.strings.datetime_formats.regionalTime.short if isShort else R.strings.datetime_formats.regionalTime.full
    withMinutesLocale = shortFullLocale.withMinutes if isShort and isWithMinutes else shortFullLocale
    return backport.text(__getRealmLocale(withMinutesLocale.pm)) if isPm else backport.text(__getRealmLocale(withMinutesLocale.am))


__formatMap = {DateTimeFormatsEnum.DAYMONTHNUMERIC: lambda _: backport.text(__getRealmLocale(R.strings.datetime_formats.regionalDate.dayMonthNumeric)),
 DateTimeFormatsEnum.DAYMONTHFULL: lambda _: backport.text(__getRealmLocale(R.strings.datetime_formats.regionalDate.dayMonthFull)),
 DateTimeFormatsEnum.DAYMONTHFULLTIME: lambda timestamp: __FORMAT_STRING_WITH_TIME.format(backport.text(__getRealmLocale(R.strings.datetime_formats.regionalDate.dayMonthFull)), __getRegionalTime(timestamp, isShort=True)),
 DateTimeFormatsEnum.DAYMONTHABBREVIATED: lambda _: backport.text(__getRealmLocale(R.strings.datetime_formats.regionalDate.dayMonthAbbreviated)),
 DateTimeFormatsEnum.DAYMONTHABBREVIATEDTIME: lambda timestamp: __FORMAT_STRING_WITH_TIME.format(backport.text(__getRealmLocale(R.strings.datetime_formats.regionalDate.dayMonthAbbreviated)), __getRegionalTime(timestamp, isShort=True)),
 DateTimeFormatsEnum.SHORTDATE: lambda _: backport.text(__getRealmLocale(R.strings.datetime_formats.regionalDate.shortDate)),
 DateTimeFormatsEnum.SHORTTIME: lambda timestamp: __getRegionalTime(timestamp, isShort=True),
 DateTimeFormatsEnum.SHORTDATETIME: lambda timestamp: __FORMAT_STRING_WITH_TIME.format(backport.text(__getRealmLocale(R.strings.datetime_formats.regionalDate.shortDate)), __getRegionalTime(timestamp, isShort=True)),
 DateTimeFormatsEnum.FULLDATE: lambda _: backport.text(__getRealmLocale(R.strings.datetime_formats.regionalDate.fullDate)),
 DateTimeFormatsEnum.FULLTIME: lambda timestamp: __getRegionalTime(timestamp, isShort=False),
 DateTimeFormatsEnum.FULLDATETIME: lambda timestamp: __FORMAT_STRING_WITH_TIME.format(backport.text(__getRealmLocale(R.strings.datetime_formats.regionalDate.fullDate)), __getRegionalTime(timestamp, isShort=True)),
 DateTimeFormatsEnum.MONTH: lambda _: '%B',
 DateTimeFormatsEnum.MONTHYEAR: lambda _: '%B %Y',
 DateTimeFormatsEnum.WEEKDAY: lambda _: '%A',
 DateTimeFormatsEnum.WEEKDAYTIME: lambda timestamp: __FORMAT_STRING_WITH_TIME.format('%A', __getRegionalTime(timestamp, isShort=True)),
 DateTimeFormatsEnum.MONTHDAY: lambda _: '%#d',
 DateTimeFormatsEnum.YEAR: lambda _: '%Y'}
__declensionMap = {_MonthFormatKeysEnum.FULL.value: R.strings.menu.dateTime.months,
 _MonthFormatKeysEnum.ABBREVIATED.value: R.strings.menu.dateTime.months.shortSmall}
__MONTH_SEARCH_REGEXP = backport.text(R.strings.datetime_formats.regionalDate.declensionRegexp()).format('|'.join((e.value for e in _MonthFormatKeysEnum)))

def __getLocalizationDict(formatString, month, weekday):
    localizationDict = {str(_MonthFormatKeysEnum.FULL.value): backport.text(R.strings.menu.dateTime.months.full.num(month)()),
     str(_MonthFormatKeysEnum.ABBREVIATED.value): backport.text(R.strings.menu.dateTime.months.short.num(month)()),
     str(_WeekdayFormatKeysEnum.FULL.value): backport.text(R.strings.menu.dateTime.weekDays.full.num(weekday)()),
     str(_WeekdayFormatKeysEnum.ABBREVIATED.value): backport.text(R.strings.menu.dateTime.weekDays.short.num(weekday)())}
    monthDayMatch = re.search(__MONTH_SEARCH_REGEXP, formatString)
    if monthDayMatch:
        localizationDict[monthDayMatch.group(1)] = backport.text(__declensionMap[monthDayMatch.group(1)].num(month)())
    return localizationDict


def getRegionalDateTime(timestamp, dateTimeFormat, isConvertedToLocal=True):
    dateTimeFormatEnum = DateTimeFormatsEnum(dateTimeFormat)
    if dateTimeFormatEnum not in __formatMap:
        raise SoftException('Provided date format constant is not present in format map')
    dateTimeFormatString = __formatMap[dateTimeFormatEnum](timestamp)
    timeStructInLocal = time.localtime(timestamp) if isConvertedToLocal else time.gmtime(timestamp)
    localizationDict = __getLocalizationDict(str(dateTimeFormatString), timeStructInLocal.tm_mon, timeStructInLocal.tm_wday + 1)
    localizedFormat = replaceMultiple(str(dateTimeFormatString), localizationDict)
    return time.strftime(str(localizedFormat), timeStructInLocal)
