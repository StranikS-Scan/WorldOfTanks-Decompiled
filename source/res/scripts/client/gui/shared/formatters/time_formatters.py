# Embedded file name: scripts/client/gui/shared/formatters/time_formatters.py
import math
from gui.Scaleform.locale.MENU import MENU
from helpers import i18n, time_utils

def defaultFormatter(key, countType, count, ctx = None):
    kwargs = ctx.copy() if ctx else {}
    kwargs[countType] = count
    return i18n.makeString((key % countType), **kwargs)


def getTimeLeftStr(localization, timeLeft, timeStyle = None, ctx = None, formatter = None):
    if ctx is None:
        ctx = {}
    if formatter is None:
        formatter = defaultFormatter
    result = ''

    def formatTime(divisor):
        formattedTime = str(int(math.ceil(float(timeLeft) / divisor)))
        if timeStyle:
            formattedTime = timeStyle(formattedTime)
        return formattedTime

    if timeLeft > 0:
        if timeLeft > time_utils.ONE_DAY:
            result = formatter(localization, 'days', formatTime(time_utils.ONE_DAY), ctx)
        else:
            result = formatter(localization, 'hours', formatTime(time_utils.ONE_HOUR), ctx)
    return result


def getTimeDurationStr(seconds, useRoundUp = False):
    return time_utils.getTillTimeString(seconds, MENU.TIME_TIMEVALUE, useRoundUp)


class RentLeftFormatter(object):

    def __init__(self, rentInfo, isIGR = False):
        super(RentLeftFormatter, self).__init__()
        self.__rentInfo = rentInfo
        self.__isIGR = isIGR
        self.__localizationRootKey = '#menu:vehicle/rentLeft/%s'

    def getRentLeftStr(self, localization = None, timeStyle = None, ctx = None, formatter = None):
        if self.__rentInfo.timeLeft > 0:
            resultStr = self.getRentTimeLeftStr(localization, timeStyle, ctx, formatter)
        else:
            resultStr = self.getRentBattlesLeftStr(localization, formatter)
        return resultStr

    def getRentTimeLeftStr(self, localization = None, timeStyle = None, ctx = None, formatter = None):
        if self.__isIGR:
            return ''
        else:
            if localization is None:
                localization = self.__localizationRootKey
            return getTimeLeftStr(localization, self.__rentInfo.timeLeft, timeStyle, ctx, formatter)

    def getRentBattlesLeftStr(self, localization = None, formatter = None):
        if localization is None:
            localization = self.__localizationRootKey
        if formatter is None:
            formatter = defaultFormatter
        battlesLeft = self.__rentInfo.battlesLeft
        if battlesLeft > 0:
            return formatter(localization, 'battles', battlesLeft)
        else:
            return ''
