# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/birthday_calendar/__init__.py
from gui.game_control import CalendarInvokeOrigin
from helpers import dependency
from skeletons.gui.game_control import IBirthdayCalendarController
from skeletons.gui.shared import IItemsCache
from web.web_client_api import w2c, w2capi, W2CSchema, Field

def _invokedFromValidator(value, _):
    return not value or value in CalendarInvokeOrigin.ALL()


class _OpenBirthdayCalendarSchema(W2CSchema):
    url = Field(required=False, type=basestring)
    invoked_from = Field(required=False, type=basestring, validator=_invokedFromValidator)


class OpenBirthdayCalendarWebApiMixin(object):
    __birthdayCalendarController = dependency.descriptor(IBirthdayCalendarController)

    @w2c(_OpenBirthdayCalendarSchema, 'birthday_calendar')
    def openBirthdayCalendar(self, cmd):
        self.__birthdayCalendarController.showWindow(cmd.url, cmd.invoked_from)


@w2capi(name='birthday_calendar', key='action')
class BirthdayCalendarWebApi(object):
    __birthdayCalendarController = dependency.descriptor(IBirthdayCalendarController)
    __itemsCache = dependency.descriptor(IItemsCache)

    @w2c(W2CSchema, name='event_daterange')
    def eventDates(self, cmd):
        start, end = self.__birthdayCalendarController.eventDates or (0, 0)
        return {'start_timestamp': start,
         'end_timestamp': end}

    @w2c(W2CSchema, name='birthday_stage')
    def birthdayStage(self, cmd):
        return {'birthday_stage': self.__birthdayCalendarController.tokenCount}
