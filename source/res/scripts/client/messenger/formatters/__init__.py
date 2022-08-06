# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/__init__.py
import logging
from time import gmtime, time as getTime
from collections import namedtuple
from constants import NC_CONTEXT_ITEM_TYPE
from gui.impl import backport
from helpers import time_utils
from messenger import g_settings
_logger = logging.getLogger(__name__)

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
        return '{0:>s}'.format(backport.getShortDateFormat(time))

    @classmethod
    def getLongTimeFormat(cls, time):
        return '{0:>s}'.format(backport.getLongTimeFormat(time))

    @classmethod
    def getShortTimeFormat(cls, time):
        return '{0:>s}'.format(backport.getShortTimeFormat(time))

    @classmethod
    def getLongDatetimeFormat(cls, time):
        return '{0:>s} {1:>s}'.format(backport.getShortDateFormat(time), backport.getLongTimeFormat(time))

    @classmethod
    def getShortTimeDateFormat(cls, time):
        return '{0:>s} {1:>s}'.format(backport.getShortTimeFormat(time), backport.getShortDateFormat(time))

    @classmethod
    def getShortDatetimeFormat(cls, time):
        return '{0:>s} {1:>s}'.format(backport.getShortDateFormat(time), backport.getShortTimeFormat(time))

    @classmethod
    def getActualMsgTimeStr(cls, timestamp):
        try:
            DAY_SECONDS = 86400
            currentTime = getTime()
            if currentTime - timestamp > DAY_SECONDS or gmtime().tm_mday != gmtime(timestamp).tm_mday:
                return TimeFormatter.getShortTimeDateFormat(timestamp)
            return TimeFormatter.getShortTimeFormat(timestamp)
        except Exception:
            _logger.exception('There is error while formatting message time: %r', timestamp)

    @classmethod
    def getMessageEmptyFormatU(cls, _):
        pass

    @classmethod
    def getMessageShortDateFormat(cls, time):
        return '({0:>s}) '.format(backport.getShortDateFormat(time)).decode('utf-8', 'ignore')

    @classmethod
    def getMessageLongTimeFormat(cls, time):
        return '({0:>s}) '.format(backport.getLongTimeFormat(time)).decode('utf-8', 'ignore')

    @classmethod
    def getMessageLongDatetimeFormat(cls, time):
        return '({0:>s} {1:>s}) '.format(backport.getShortDateFormat(time), backport.getLongTimeFormat(time)).decode('utf-8', 'ignore')


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
            _logger.warning('Type of item is not found: %r, %r', itemType, itemValue)
            return str(itemValue)
        method = cls._formats[itemType]
        return getattr(cls, method)(itemValue)

    @classmethod
    def getGoldFormat(cls, value):
        return backport.getGoldFormat(value)

    @classmethod
    def getIntegralFormat(cls, value):
        return backport.getIntegralFormat(value)

    @classmethod
    def getFractionalFormat(cls, value):
        return backport.getFractionalFormat(value)

    @classmethod
    def getNiceNumberFormat(cls, value):
        return backport.getNiceNumberFormat(value)

    @classmethod
    def getShortTimeFormat(cls, value):
        return cls._makeLocalTimeString(value, backport.getShortTimeFormat)

    @classmethod
    def getLongTimeFormat(cls, value):
        return cls._makeLocalTimeString(value, backport.getLongTimeFormat)

    @classmethod
    def getShortDateFormat(cls, value):
        return cls._makeLocalTimeString(value, backport.getShortDateFormat)

    @classmethod
    def getLongDateFormat(cls, value):
        return cls._makeLocalTimeString(value, backport.getLongDateFormat)

    @classmethod
    def getDateTimeFormat(cls, value):
        return cls._makeLocalTimeString(value, lambda localTime: '{0:>s} {1:>s}'.format(backport.getShortDateFormat(value), backport.getLongTimeFormat(value)))

    @classmethod
    def getStringFormat(cls, value):
        return unicode(value)

    @classmethod
    def _makeLocalTimeString(cls, value, formatter):
        result = time_utils.makeLocalServerTime(value)
        if result:
            result = formatter(value)
        else:
            _logger.warning('Timestamp is not defined: %r', value)
            result = ''
        return result


SysMsgExtraData = namedtuple('SysMsgExtraData', 'type data')
