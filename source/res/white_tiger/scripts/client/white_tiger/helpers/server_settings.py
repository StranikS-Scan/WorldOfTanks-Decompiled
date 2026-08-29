# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/helpers/server_settings.py
from __future__ import absolute_import
from collections import namedtuple
from future.utils import viewitems

class WhiteTigerConfig(namedtuple('WhiteTigerConfig', ('isEnabled', 'peripheryIDs', 'primeTimes', 'seasons', 'cycleTimes', 'squadConfig'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, peripheryIDs={}, primeTimes={}, seasons={}, cycleTimes={}, squadConfig={})
        defaults.update(kwargs)
        return super(WhiteTigerConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = {k:v for k, v in viewitems(data) if k in allowedFields}
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()
