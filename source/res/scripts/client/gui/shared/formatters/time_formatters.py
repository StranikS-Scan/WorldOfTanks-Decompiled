# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/time_formatters.py
import math
import time
from gui.Scaleform.locale.MENU import MENU
from helpers import i18n, time_utils

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
            return ('days', formatTime(timeLeft, time_utils.ONE_DAY, timeStyle))
        return ('hours', formatTime(timeLeft, time_utils.ONE_HOUR, timeStyle))


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


def getTimeDurationStr(seconds, useRoundUp=False):
    return time_utils.getTillTimeString(seconds, MENU.TIME_TIMEVALUE, useRoundUp)


class RentLeftFormatter(object):

    def __init__(self, rentInfo, isIGR=False):
        super(RentLeftFormatter, self).__init__()
        self.__rentInfo = rentInfo
        self.__isIGR = isIGR
        self.__localizationRootKey = '#menu:vehicle/rentLeft/%s'

    def getRentLeftStr(self, localization=None, timeStyle=None, ctx=None, formatter=None):
        if self.__rentInfo.getTimeLeft() > 0:
            resultStr = self.getRentTimeLeftStr(localization, timeStyle, ctx, formatter)
        elif self.__rentInfo.battlesLeft:
            resultStr = self.getRentBattlesLeftStr(localization, formatter)
        else:
            resultStr = self.getRentWinsLeftStr(localization, formatter)
        return resultStr

    def getRentTimeLeftStr(self, localization=None, timeStyle=None, ctx=None, formatter=None):
        if self.__isIGR:
            return ''
        else:
            if localization is None:
                localization = self.__localizationRootKey
            return getTimeLeftStr(localization, self.__rentInfo.getTimeLeft(), timeStyle, ctx, formatter)

    def getRentBattlesLeftStr(self, localization=None, formatter=None):
        if localization is None:
            localization = self.__localizationRootKey
        if formatter is None:
            formatter = defaultFormatter
        battlesLeft = self.__rentInfo.battlesLeft
        return formatter(localization, 'battles', battlesLeft) if battlesLeft > 0 else ''

    def getRentWinsLeftStr(self, localization=None, formatter=None):
        if localization is None:
            localization = self.__localizationRootKey
        if formatter is None:
            formatter = defaultFormatter
        winsLeft = self.__rentInfo.winsLeft
        return formatter(localization, 'wins', winsLeft) if winsLeft > 0 else ''
