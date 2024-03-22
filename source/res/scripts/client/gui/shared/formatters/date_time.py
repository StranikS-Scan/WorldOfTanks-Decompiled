# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/date_time.py
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


__SHORT_TIME_FORMAT_KEY = '%TIME'
__FULL_TIME_FORMAT_KEY = '%FULL_TIME'
__FULL_DECLENSION_MONTH_NAME = '%Bd'
__ABBREVIATED_DECLENSION_MONTH_NAME = '%bd'
__FULL_SMALL_MONTH_NAME = '%Bs'
__ABBREVIATED_SMALL_MONTH_NAME = '%bs'
__TIME_KEYS = [__SHORT_TIME_FORMAT_KEY, __FULL_TIME_FORMAT_KEY]

def __getRealmLocale(path):
    accessor = path.dyn(CURRENT_REALM)
    return accessor() if accessor.isValid() else path()


def __getRegionalTime(hour, minute, isShort):
    isWithMinutes = minute != 0
    isPm = hour >= 12
    shortFullLocale = R.strings.datetime_formats.regionalTime.short if isShort else R.strings.datetime_formats.regionalTime.full
    withMinutesLocale = shortFullLocale.withMinutes if isShort and isWithMinutes else shortFullLocale
    return backport.text(__getRealmLocale(withMinutesLocale.pm)) if isPm else backport.text(__getRealmLocale(withMinutesLocale.am))


__formatMap = {DateTimeFormatsEnum.DAYMONTHNUMERIC: __getRealmLocale(R.strings.datetime_formats.regionalDate.dayMonthNumeric),
 DateTimeFormatsEnum.DAYMONTHFULL: __getRealmLocale(R.strings.datetime_formats.regionalDate.dayMonthFull),
 DateTimeFormatsEnum.DAYMONTHFULLTIME: __getRealmLocale(R.strings.datetime_formats.regionalDate.dayMonthFullTime),
 DateTimeFormatsEnum.DAYMONTHABBREVIATED: __getRealmLocale(R.strings.datetime_formats.regionalDate.dayMonthAbbreviated),
 DateTimeFormatsEnum.DAYMONTHABBREVIATEDTIME: __getRealmLocale(R.strings.datetime_formats.regionalDate.dayMonthAbbreviatedTime),
 DateTimeFormatsEnum.SHORTDATE: __getRealmLocale(R.strings.datetime_formats.regionalDate.shortDate),
 DateTimeFormatsEnum.SHORTTIME: __SHORT_TIME_FORMAT_KEY,
 DateTimeFormatsEnum.SHORTDATETIME: __getRealmLocale(R.strings.datetime_formats.regionalDate.shortDateTime),
 DateTimeFormatsEnum.FULLDATE: __getRealmLocale(R.strings.datetime_formats.regionalDate.fullDate),
 DateTimeFormatsEnum.FULLTIME: __FULL_TIME_FORMAT_KEY,
 DateTimeFormatsEnum.FULLDATETIME: __getRealmLocale(R.strings.datetime_formats.regionalDate.fullDateTime)}

def __getLocalizationDict(month, weekday, hour, minute):
    localizationDict = {str(_MonthFormatKeysEnum.FULL.value): backport.text(R.strings.menu.dateTime.months.full.num(month)()),
     str(_MonthFormatKeysEnum.ABBREVIATED.value): backport.text(R.strings.menu.dateTime.months.short.num(month)()),
     str(_WeekdayFormatKeysEnum.FULL.value): backport.text(R.strings.menu.dateTime.weekDays.full.num(weekday)()),
     str(_WeekdayFormatKeysEnum.ABBREVIATED.value): backport.text(R.strings.menu.dateTime.weekDays.short.num(weekday)()),
     __SHORT_TIME_FORMAT_KEY: __getRegionalTime(hour, minute, True),
     __FULL_TIME_FORMAT_KEY: __getRegionalTime(hour, minute, False),
     __FULL_DECLENSION_MONTH_NAME: backport.text(R.strings.menu.dateTime.months.num(month)()),
     __ABBREVIATED_DECLENSION_MONTH_NAME: backport.text(R.strings.menu.dateTime.months.shortSmall.num(month)()),
     __FULL_SMALL_MONTH_NAME: backport.text(R.strings.menu.dateTime.months.fullSmall.num(month)()),
     __ABBREVIATED_SMALL_MONTH_NAME: backport.text(R.strings.menu.dateTime.months.shortSmall.num(month)())}
    return localizationDict


def getFormattedDateTime(timestamp, formatString, isConvertedToLocal=True):
    timeStructInLocal = time.localtime(timestamp) if isConvertedToLocal else time.gmtime(timestamp)
    localizationDict = __getLocalizationDict(timeStructInLocal.tm_mon, timeStructInLocal.tm_wday + 1, timeStructInLocal.tm_hour, timeStructInLocal.tm_min)
    localizedFormat = replaceMultiple(formatString, localizationDict)
    return time.strftime(str(localizedFormat), timeStructInLocal)


def getRegionalDateTime(timestamp, dateTimeFormat, isConvertedToLocal=True):
    dateTimeFormatEnum = DateTimeFormatsEnum(dateTimeFormat)
    if dateTimeFormatEnum not in __formatMap:
        raise SoftException('Provided date format constant is not present in format map')
    key = __formatMap[dateTimeFormatEnum]
    return getFormattedDateTime(timestamp, key, isConvertedToLocal) if key in __TIME_KEYS else getFormattedDateTime(timestamp, backport.text(key), isConvertedToLocal)
