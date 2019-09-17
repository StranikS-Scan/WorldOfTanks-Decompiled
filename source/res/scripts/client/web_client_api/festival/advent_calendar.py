# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/festival/advent_calendar.py
import sys
from helpers import dependency
from skeletons.gui.game_control import ICalendarController
from web_client_api import w2c, W2CSchema, Field, WebCommandException

def _itemsCountValidator(value, _):
    return _isValid('items_count', value)


def _endTimestampValidator(value, _):
    return _isValid('end_timestamp', value)


def _isValid(key, value):
    if 0 <= value <= sys.maxint:
        return True
    raise WebCommandException('{} must be in range from 0 to {} inclusive'.format(key, sys.maxint))


class _SetCounterSchema(W2CSchema):
    items_count = Field(required=True, type=int, validator=_itemsCountValidator)
    end_timestamp = Field(required=True, type=(int, float), validator=_endTimestampValidator)


class AdventCalendarWebApiMixin(object):
    __calendarController = dependency.descriptor(ICalendarController)

    @w2c(W2CSchema, 'get_advc_counters_info')
    def getCounter(self, _):
        info = self.__calendarController.getDeferredItemsActionInfo()
        return {'isEnabled': info.isEnabled,
         'itemsCount': info.itemsCount,
         'endTimestamp': info.endTimestamp}

    @w2c(_SetCounterSchema, 'set_advc_counters_info')
    def setCounter(self, cmd):
        self.__calendarController.setDeferredItemsActionInfo(cmd.items_count, cmd.end_timestamp)

    @w2c(W2CSchema, 'upd_advc_counters_info')
    def updateCounter(self, _):
        self.__calendarController.updDeferredItemsActionInfo()
