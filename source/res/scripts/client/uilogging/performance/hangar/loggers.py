# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/performance/hangar/loggers.py
import logging
import typing
from uilogging.base.logger import _BaseLogger as Logger, createPartnerID
from uilogging.constants import DEFAULT_LOGGER_NAME
from uilogging.performance.hangar.constants import Features, Groups, LogActions
from uilogging.helpers import getClientSessionID
import BigWorld
from wotdecorators import noexcept
if typing.TYPE_CHECKING:
    from uilogging.types import GroupType, PartnerIdType
_logger = logging.getLogger(DEFAULT_LOGGER_NAME)

class _BaseHangarMetricsLogger(Logger):
    __slots__ = ()

    def __init__(self, group):
        super(_BaseHangarMetricsLogger, self).__init__(Features.METRICS, group)

    @noexcept
    def log(self, data, partnerID=None, sessionID=''):
        if not isinstance(data, dict):
            _logger.error('Wrong metrics data type: [dict != %s].', type(data))
            return
        if data:
            super(_BaseHangarMetricsLogger, self)._log(LogActions.SPACE_DISPOSED, partnerID=partnerID, session_id=sessionID, **data)


class _HangarSpaceMetricsLogger(_BaseHangarMetricsLogger):
    __slots__ = ()

    def __init__(self):
        super(_HangarSpaceMetricsLogger, self).__init__(Groups.SPACE)

    def log(self, data, partnerID=None, sessionID=''):
        if not isinstance(data, dict):
            _logger.error('Wrong metrics data type: [dict != %s].', type(data))
            return
        if data:
            super(_HangarSpaceMetricsLogger, self).log(data, partnerID=partnerID, sessionID=sessionID)


class _HangarViewsMetricsLogger(_BaseHangarMetricsLogger):
    __slots__ = ()

    def __init__(self):
        super(_HangarViewsMetricsLogger, self).__init__(Groups.VIEWS)

    def log(self, data, partnerID=None, sessionID=''):
        if not isinstance(data, list):
            _logger.error('Wrong views metrics data type: [list != %s].', type(data))
            return
        for viewData in data:
            super(_HangarViewsMetricsLogger, self).log(viewData, partnerID=partnerID, sessionID=sessionID)


class HangarMetricsLogger(object):
    __slots__ = ('_loggers', '_defaultLogger')

    def __init__(self):
        self._loggers = {Groups.SPACE.value: _HangarSpaceMetricsLogger(),
         Groups.VIEWS.value: _HangarViewsMetricsLogger()}
        self._defaultLogger = self._loggers[Groups.SPACE.value]

    def initialize(self):
        self._defaultLogger.ensureSession()

    @noexcept
    def log(self):
        _logger.debug('Hangar performance metrics requested.')
        if self._defaultLogger.disabled:
            return
        data = BigWorld.wg_getHangarStatistics()
        if not data:
            _logger.debug('Hangar performance metrics are empty.')
            return
        diff = set(data) ^ set(self._loggers)
        if diff:
            _logger.error('Difference in loggers and received metrics groups: %s.', diff)
            return
        partnerID = createPartnerID()
        clientSessionID = getClientSessionID()
        for group, stats in data.iteritems():
            self._loggers[group].log(stats, partnerID=partnerID, sessionID=clientSessionID)
