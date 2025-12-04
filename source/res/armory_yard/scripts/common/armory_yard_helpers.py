# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/common/armory_yard_helpers.py
from datetime import timedelta
import calendar
import time

def getNextFreeRerollUpdateTimestamp(dailyFreeRerollUpdate, freeRerollDaysDelta, currentDatetime):
    datetimeObj = time.strptime(dailyFreeRerollUpdate, '%H:%M')
    nextRerollDatetime = currentDatetime.replace(hour=datetimeObj.tm_hour, minute=datetimeObj.tm_min, second=0, microsecond=0)
    if nextRerollDatetime < currentDatetime:
        nextRerollDatetime += timedelta(days=freeRerollDaysDelta)
    else:
        nextRerollDatetime += timedelta(days=freeRerollDaysDelta - 1)
    return int(calendar.timegm(nextRerollDatetime.utctimetuple()))
