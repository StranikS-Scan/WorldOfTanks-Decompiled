# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/helpers/server_settings.py
from __future__ import absolute_import
from collections import namedtuple

class AdventCalendarConfig(namedtuple('AdventCalendarConfig', ('isEnabled', 'startDate', 'postEventStartDate', 'NYEntryPointStartDate', 'postEventEndDate', 'doors', 'doorOpenTokenMask', 'downloadImgUrl'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, startDate=0, doors=[], postEventStartDate=0, postEventEndDate=0, NYEntryPointStartDate=0, doorOpenTokenMask='', downloadImgUrl='')
        defaults.update(kwargs)
        return super(AdventCalendarConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.items() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @property
    def doorsCount(self):
        return len(self.doors)

    def isSpecialDay(self, dayId):
        return self.doors[dayId - 1].get('isSpecialDay', False)
