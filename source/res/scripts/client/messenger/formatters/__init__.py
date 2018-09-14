# Embedded file name: scripts/client/messenger/formatters/__init__.py
from collections import namedtuple
import BigWorld
import time
from time import gmtime
from constants import NC_CONTEXT_ITEM_TYPE
from debug_utils import LOG_WARNING, LOG_CURRENT_EXCEPTION, LOG_ERROR
from helpers import time_utils, i18n
from messenger import g_settings

class TimeFormatter(object):
    _messageDateTimeFormat = {0: 'getMessageEmptyFormatU',
     1: 'getMessageShortDateFormat',
     2: 'getMessageLongTimeFormat',
     3: 'getMessageLongDatetimeFormat'}

    @classmethod
    def getMessageTimeFormat(cls, time):
        method = cls._messageDateTimeFormat[g_settings.userPrefs.datetimeIdx]
        return getattr(cls, method)(time)

    @classmethod
    def getShortDateFormat(cls, time):
        return '{0:>s}'.format(BigWorld.wg_getShortDateFormat(time))

    @classmethod
    def getLongTimeFormat(cls, time):
        return '{0:>s}'.format(BigWorld.wg_getLongTimeFormat(time))

    @classmethod
    def getShortTimeFormat(cls, time):
        return '{0:>s}'.format(BigWorld.wg_getShortTimeFormat(time))

    @classmethod
    def getLongDatetimeFormat(cls, time):
        return '{0:>s} {1:>s}'.format(BigWorld.wg_getShortDateFormat(time), BigWorld.wg_getLongTimeFormat(time))

    @classmethod
    def getShortTimeDateFormat(cls, time):
        return '{0:>s} {1:>s}'.format(BigWorld.wg_getShortTimeFormat(time), BigWorld.wg_getShortDateFormat(time))

    @classmethod
    def getShortDatetimeFormat(cls, time):
        return '{0:>s} {1:>s}'.format(BigWorld.wg_getShortDateFormat(time), BigWorld.wg_getShortTimeFormat(time))

    @classmethod
    def getActualMsgTimeStr(cls, timestamp):
        try:
            DAY_SECONDS = 86400
            currentTime = time.time()
            if currentTime - timestamp > DAY_SECONDS or gmtime().tm_mday != gmtime(timestamp).tm_mday:
                return TimeFormatter.getShortTimeDateFormat(timestamp)
            return TimeFormatter.getShortTimeFormat(timestamp)
        except:
            LOG_ERROR('There is error while formatting message time', timestamp)
            LOG_CURRENT_EXCEPTION()

    @classmethod
    def getMessageEmptyFormatU(cls, _):
        return u''

    @classmethod
    def getMessageShortDateFormat(cls, time):
        return '({0:>s}) '.format(BigWorld.wg_getShortDateFormat(time)).decode('utf-8', 'ignore')

    @classmethod
    def getMessageLongTimeFormat(cls, time):
        return '({0:>s}) '.format(BigWorld.wg_getLongTimeFormat(time)).decode('utf-8', 'ignore')

    @classmethod
    def getMessageLongDatetimeFormat(cls, time):
        return '({0:>s} {1:>s}) '.format(BigWorld.wg_getShortDateFormat(time), BigWorld.wg_getLongTimeFormat(time)).decode('utf-8', 'ignore')


class NCContextItemFormatter(object):
    _formats = {NC_CONTEXT_ITEM_TYPE.GOLD: 'getGoldFormat',
     NC_CONTEXT_ITEM_TYPE.INTEGRAL: 'getIntegralFormat',
     NC_CONTEXT_ITEM_TYPE.FRACTIONAL: 'getFractionalFormat',
     NC_CONTEXT_ITEM_TYPE.NICE_NUMBER: 'getNiceNumberFormat',
     NC_CONTEXT_ITEM_TYPE.SHORT_TIME: 'getShortTimeFormat',
     NC_CONTEXT_ITEM_TYPE.LONG_TIME: 'getLongTimeFormat',
     NC_CONTEXT_ITEM_TYPE.SHORT_DATE: 'getShortDateFormat',
     NC_CONTEXT_ITEM_TYPE.LONG_DATE: 'getLongDateFormat',
     NC_CONTEXT_ITEM_TYPE.DATETIME: 'getDateTimeFormat',
     NC_CONTEXT_ITEM_TYPE.STRING: 'getStringFormat'}

    @classmethod
    def getItemFormat(cls, itemType, itemValue):
        if itemType not in cls._formats:
            LOG_WARNING('Type of item is not found', itemType, itemValue)
            return str(itemValue)
        method = cls._formats[itemType]
        return getattr(cls, method)(itemValue)

    @classmethod
    def getGoldFormat(cls, value):
        return BigWorld.wg_getGoldFormat(value)

    @classmethod
    def getIntegralFormat(cls, value):
        return BigWorld.wg_getIntegralFormat(value)

    @classmethod
    def getFractionalFormat(cls, value):
        return BigWorld.wg_getFractionalFormat(value)

    @classmethod
    def getNiceNumberFormat(cls, value):
        return BigWorld.wg_getNiceNumberFormat(value)

    @classmethod
    def getShortTimeFormat(cls, value):
        return cls._makeLocalTimeString(value, BigWorld.wg_getShortTimeFormat)

    @classmethod
    def getLongTimeFormat(cls, value):
        return cls._makeLocalTimeString(value, BigWorld.wg_getLongTimeFormat)

    @classmethod
    def getShortDateFormat(cls, value):
        return cls._makeLocalTimeString(value, BigWorld.wg_getShortDateFormat)

    @classmethod
    def getLongDateFormat(cls, value):
        return cls._makeLocalTimeString(value, BigWorld.wg_getLongDateFormat)

    @classmethod
    def getDateTimeFormat(cls, value):
        return cls._makeLocalTimeString(value, lambda localTime: '{0:>s} {1:>s}'.format(BigWorld.wg_getShortDateFormat(value), BigWorld.wg_getLongTimeFormat(value)))

    @classmethod
    def getStringFormat(cls, value):
        return i18n.encodeUtf8(value)

    @classmethod
    def _makeLocalTimeString(cls, value, formatter):
        result = time_utils.makeLocalServerTime(value)
        if result:
            result = formatter(value)
        else:
            LOG_WARNING('Timestamp is not defined', value)
            result = ''
        return result


SysMsgExtraData = namedtuple('SysMsgExtraData', 'type data')
