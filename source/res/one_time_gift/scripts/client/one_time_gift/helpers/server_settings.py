# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/helpers/server_settings.py
from collections import namedtuple

class OneTimeGiftConfig(namedtuple('OneTimeGiftConfig', ('isEnabled', 'startTime', 'endTime', 'remindTime', 'remindBattlesAmount', 'newbieDistinctionTime', 'additionalRewards', 'collectorsCompensation'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=True, startTime=0, endTime=0, remindTime=0, remindBattlesAmount=0, newbieDistinctionTime=0, additionalRewards={}, collectorsCompensation={})
        defaults.update(kwargs)
        return super(OneTimeGiftConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()
