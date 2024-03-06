# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/constants/date_time_formats.py
from enum import Enum
from frameworks.wulf import ViewModel

class DateTimeFormatsEnum(Enum):
    DAYMONTHNUMERIC = 'dayMonthNumeric'
    DAYMONTHFULL = 'dayMonthFull'
    DAYMONTHFULLTIME = 'dayMonthFullTime'
    DAYMONTHABBREVIATED = 'dayMonthAbbreviated'
    DAYMONTHABBREVIATEDTIME = 'dayMonthAbbreviatedTime'
    SHORTDATE = 'shortDate'
    SHORTTIME = 'ShortTime'
    SHORTDATETIME = 'ShortDateTime'
    FULLDATE = 'fullDate'
    FULLTIME = 'fullTime'
    FULLDATETIME = 'fullDateTime'
    MONTH = 'month'
    MONTHYEAR = 'monthYear'
    WEEKDAY = 'weekDay'
    WEEKDAYTIME = 'weekDayTime'
    MONTHDAY = 'monthDay'
    YEAR = 'year'


class DateTimeFormats(ViewModel):
    __slots__ = ()

    def __init__(self, properties=0, commands=0):
        super(DateTimeFormats, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(DateTimeFormats, self)._initialize()
