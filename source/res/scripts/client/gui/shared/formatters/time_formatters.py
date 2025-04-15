# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/time_formatters.py
import math
import time
from gui.Scaleform.locale.MENU import MENU
from gui.impl import backport
from helpers import i18n, time_utils
from rent_common import SeasonRentDuration
from constants import GameSeasonType
from season_common import getDateFromSeasonID
_SEASON_TYPE_KEY = {GameSeasonType.EPIC: 'epic',
 GameSeasonType.RANKED: 'ranked'}

class RentDurationKeys(object):
    SEASON = 'season'
    CYCLE = 'cycle'
    CYCLES = 'cycles'
    TIME = 'time'
    DAYS = 'days'
    HOURS = 'hours'
    MINUTES = 'minutes'
    BATTLES = 'battles'
    WINS = 'wins'


def defaultFormatter(key, countType, count, ctx=None):
    kwargs = ctx.copy() if ctx else {}
    kwargs[countType] = count
    return i18n.makeString((key % countType), **kwargs)


def formatDate(dateFormat, timestamp):
    return time.strftime(i18n.makeString(dateFormat), time_utils.getTimeStructInLocal(timestamp))


def formatTime(timeLeft, divisor, timeStyle=None):
    formattedTime = str(int(math.ceil(float(timeLeft) / divisor)))
    if timeStyle:
        formattedTime = timeStyle(formattedTime)
    return formattedTime


def getTimeLeftInfo(timeLeft, timeStyle=None):
    if timeLeft > 0 and timeLeft != float('inf'):
        if timeLeft > time_utils.ONE_DAY:
            return (RentDurationKeys.DAYS, formatTime(timeLeft, time_utils.ONE_DAY, timeStyle))
        return (RentDurationKeys.HOURS, formatTime(timeLeft, time_utils.ONE_HOUR, timeStyle))


def getTimeLeftInfoEx(timeLeft, timeStyle=None):
    if timeLeft > 0 and timeLeft != float('inf'):
        if timeLeft > time_utils.ONE_DAY:
            return (RentDurationKeys.DAYS, formatTime(timeLeft, time_utils.ONE_DAY, timeStyle))
        if timeLeft > time_utils.ONE_HOUR:
            return (RentDurationKeys.HOURS, formatTime(timeLeft, time_utils.ONE_HOUR, timeStyle))
    return (RentDurationKeys.MINUTES, formatTime(timeLeft, time_utils.ONE_MINUTE, timeStyle))


def getBattleTimerString(timeLeft):
    if timeLeft > 0 and timeLeft != float('inf'):
        minutes = int(timeLeft / time_utils.ONE_MINUTE)
        seconds = int(timeLeft % time_utils.ONE_MINUTE)
        return '{}:{}'.format('%02d' % minutes, '%02d' % seconds)


def getTimeLeftStr(localization, timeLeft, timeStyle=None, ctx=None, formatter=None):
    if ctx is None:
        ctx = {}
    if formatter is None:
        formatter = defaultFormatter
    result = ''
    timeKey, formattedTime = getTimeLeftInfo(timeLeft, timeStyle)
    if timeKey != 'inf':
        result = formatter(localization, timeKey, formattedTime, ctx)
    return result


def getDueDateOrTimeStr(finishTime, localization='', isShortDateFormat=False):
    if not finishTime or time_utils.isPast(finishTime):
        return ''
    if time_utils.isToday(finishTime):
        strTime = backport.getShortTimeFormat(finishTime)
    elif isShortDateFormat:
        strTime = backport.getShortDateFormat(finishTime)
    else:
        strTime = backport.getLongDateFormat(finishTime)
    return ' '.join([localization, strTime]) if localization else strTime


def getTimeDurationStr(seconds, useRoundUp=False):
    return time_utils.getTillTimeString(seconds, MENU.TIME_TIMEVALUE, useRoundUp)


def getTillTimeByResource(seconds, resource, useRoundUp=False, removeLeadingZeros=False):

    def stringGen(key, **kwargs):
        return backport.text(resource.dyn(key)(), **kwargs)

    return time_utils.getTillTimeString(seconds, isRoundUp=useRoundUp, sourceStrGenerator=stringGen, removeLeadingZeros=removeLeadingZeros)


class RentLeftFormatter(object):

    def __init__(self, rentInfo, isIGR=False):
        super(RentLeftFormatter, self).__init__()
        self.__rentInfo = rentInfo
        self.__isIGR = isIGR
        self.__localizationRootKey = '#menu:vehicle/rentLeft/%s'

    def getRentLeftStr(self, localization=None, timeStyle=None, ctx=None, formatter=None, strForSpecialTimeFormat=''):
        activeSeasonRent = self.__rentInfo.getActiveSeasonRent()
        if activeSeasonRent is not None:
            resultStr = self.getRentSeasonLeftStr(activeSeasonRent, localization, formatter, timeStyle, ctx)
        elif self.__rentInfo.getTimeLeft() > 0:
            if strForSpecialTimeFormat:
                finishTime = self.__rentInfo.getTimeLeft() + time_utils.getCurrentTimestamp()
                resultStr = self.getUntilTimeLeftStr(finishTime, strForSpecialTimeFormat)
            else:
                resultStr = self.getRentTimeLeftStr(localization, timeStyle, ctx, formatter)
        elif self.__rentInfo.battlesLeft:
            resultStr = self.getRentBattlesLeftStr(localization, formatter)
        elif self.__rentInfo.winsLeft > 0:
            resultStr = self.getRentWinsLeftStr(localization, formatter)
        else:
            resultStr = ''
        return resultStr

    def getRentTimeLeftStr(self, localization=None, timeStyle=None, ctx=None, formatter=None):
        if self.__isIGR:
            return ''
        else:
            if localization is None:
                localization = self.__localizationRootKey
            return getTimeLeftStr(localization, self.__rentInfo.getTimeLeft(), timeStyle, ctx, formatter)

    def getUntilTimeLeftStr(self, finishTime, localization=''):
        return '' if self.__isIGR else getDueDateOrTimeStr(finishTime, localization)

    def getRentBattlesLeftStr(self, localization=None, formatter=None):
        if localization is None:
            localization = self.__localizationRootKey
        if formatter is None:
            formatter = defaultFormatter
        battlesLeft = self.__rentInfo.battlesLeft
        return formatter(localization, RentDurationKeys.BATTLES, battlesLeft) if battlesLeft > 0 else ''

    def getRentWinsLeftStr(self, localization=None, formatter=None):
        if localization is None:
            localization = self.__localizationRootKey
        if formatter is None:
            formatter = defaultFormatter
        winsLeft = self.__rentInfo.winsLeft
        return formatter(localization, RentDurationKeys.WINS, winsLeft) if winsLeft > 0 else ''

    def getRentSeasonLeftStr(self, rentData, localization=None, formatter=None, timeStyle=None, ctx=None):
        ctx = ctx or {}
        if localization is None:
            localization = self.__localizationRootKey
        if formatter is None:
            formatter = defaultFormatter
        identifier = None
        timeLeftString = ''
        extraData = dict()
        if rentData.seasonType == GameSeasonType.RANKED:
            identifier, timeLeftString, extraData = self.getRentRankedSeasonLeftStr(rentData, timeStyle)
        if rentData.seasonType == GameSeasonType.EPIC:
            return i18n.makeString(localization % _SEASON_TYPE_KEY[rentData.seasonType] + '/base')
        else:
            ctx.update(extraData)
            return '' if not identifier else formatter(localization % _SEASON_TYPE_KEY[rentData.seasonType] + '/%s', identifier, timeLeftString, ctx)

    def getRentRankedSeasonLeftStr(self, rentData, timeStyle):
        ctx = {}
        timeLeft = self.__rentInfo.getTimeLeft()
        timeLeftString = formatTime(timeLeft, time_utils.ONE_DAY, timeStyle)
        identifier = RentDurationKeys.DAYS
        if rentData.duration == SeasonRentDuration.ENTIRE_SEASON and timeLeft > time_utils.ONE_WEEK:
            timeLeftString, _ = getDateFromSeasonID(rentData.seasonID)
            identifier = RentDurationKeys.SEASON
        return (identifier, timeLeftString, ctx)
