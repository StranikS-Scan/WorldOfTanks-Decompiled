# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_cycle_helpers.py
import datetime
from collections import namedtuple
from helpers import i18n
from gui.Scaleform.locale.MENU import MENU
_CYCLE_ID = 20180705
ActiveCycleTimeFrameStrings = namedtuple('ActiveCycleTimeFrameStrings', ('startDay', 'endDay', 'startMonth', 'endMonth'))

def getCurrentWelcomeScreenVersion():
    return generateVersionFromCycleID(_CYCLE_ID)


def generateVersionFromCycleID(cycleID):
    year, month, day = getDateFromCycleID(cycleID)
    year = year - 2000
    return (year << 9) + (month << 5) + day


def getActiveCycleTimeFrameStrings(nextSeason):
    if not nextSeason:
        return ActiveCycleTimeFrameStrings(None, None, None, None)
    else:
        startTimestamp = nextSeason.getCycleStartDate()
        endTimestamp = nextSeason.getCycleEndDate()
        startDay, startMonth = _getDayMonthAsStrFromUTCTimestamp(startTimestamp)
        endDay, endMonth = _getDayMonthAsStrFromUTCTimestamp(endTimestamp)
        return ActiveCycleTimeFrameStrings(startDay, endDay, startMonth, endMonth)


def getDateFromCycleID(cycleID):
    cycleIDStr = str(cycleID)
    year = int(cycleIDStr[:4])
    month = int(cycleIDStr[4:6])
    day = int(cycleIDStr[6:8])
    return (year, month, day)


def _getDayMonthAsStrFromUTCTimestamp(utcTimestamp):
    date = datetime.datetime.fromtimestamp(utcTimestamp)
    dayString = date.strftime('%d')
    if dayString.startswith('0'):
        dayString = dayString[1:]
    monthNr = date.strftime('%m')
    if monthNr.startswith('0'):
        monthNr = monthNr[1:]
    monthString = i18n.makeString(MENU.datetime_months_full(monthNr))
    return (dayString, monthString)
