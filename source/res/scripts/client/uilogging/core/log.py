# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/core/log.py
import logging
import typing
import constants
from helpers import time_utils
from uilogging.core.common import getClientBuildVersion, convertEnum
from uilogging.constants import LogLevels, DEFAULT_LOGGER_NAME
if typing.TYPE_CHECKING:
    from uilogging.types import FeatureType, GroupType, ActionType, LogLevelType
_logger = logging.getLogger(DEFAULT_LOGGER_NAME)

class LogRecord(object):
    __slots__ = ('_properties',)

    def __init__(self, feature, group, action, level, params):
        params = {k:convertEnum(v) for k, v in dict(params).iteritems()}
        _time = time_utils.getServerUTCTime()
        properties = {'client_version': getClientBuildVersion(),
         'key': convertEnum(group),
         'loglevel': convertEnum(level),
         'time_spent': params.pop('timeSpent', 0),
         'action': convertEnum(action),
         'realm': constants.CURRENT_REALM,
         'feature': convertEnum(feature),
         'time': int(_time) if params.pop('__intTime__', False) else _time,
         'partner_id': params.pop('partnerID', None)}
        duplicates = set(properties) & set(params)
        if duplicates:
            _logger.error('Reserved keys: %s in additional log params.', duplicates)
            self._properties = {}
        else:
            properties.update(params)
            self._properties = properties
        return

    @property
    def feature(self):
        return self._properties.get('feature', '')

    @property
    def group(self):
        return self._properties.get('key', '')

    @property
    def action(self):
        return self._properties.get('action', '')

    @property
    def level(self):
        return self._properties.get('loglevel', LogLevels.NOTSET)

    @property
    def time(self):
        return self._properties.get('time', 0)

    @property
    def partnerID(self):
        return self._properties.get('partner_id', None)

    @property
    def broken(self):
        return False if self.feature and self.group and self.action else True

    def toDict(self):
        return dict(self._properties)

    def __str__(self):
        return '<Log: {}, {}, {}, {}, {}>'.format(self.feature, self.group, self.action, self.level, self.time)

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self._properties)
