# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/helpers/server_settings.py
from collections import namedtuple

class TechTreeTradeInConfig(namedtuple('TechTreeTradeInConfig', ('isEnabled', 'startTime', 'endTime'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, startTime=0, endTime=0)
        defaults.update(kwargs)
        return super(TechTreeTradeInConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()
