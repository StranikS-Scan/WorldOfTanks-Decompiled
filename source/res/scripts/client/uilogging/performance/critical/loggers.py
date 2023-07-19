# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/performance/critical/loggers.py
import BigWorld
import logging
from uilogging.base.logger import _BaseLogger as Logger
from uilogging.constants import DEFAULT_LOGGER_NAME
from uilogging.performance.critical.constants import Features, Groups, LogActions
from uilogging.helpers import getClientSessionID
from wotdecorators import noexcept
_logger = logging.getLogger(DEFAULT_LOGGER_NAME)

class MemoryCriticalLogger(Logger):
    __slots__ = ()

    def __init__(self):
        super(MemoryCriticalLogger, self).__init__(Features.MEMORY_CRITICAL, Groups.EVENT)

    def initialize(self):
        self.ensureSession()

    @noexcept
    def log(self, sessionStartedAt=0):
        _logger.debug('Critical memory metrics requested.')
        if self.disabled:
            return
        self.ensureSession()
        data = BigWorld.collectLastMemoryCriticalEvent()
        sessionID = getClientSessionID()
        if data:
            self._logImmediately(LogActions.MEMORY_CRITICAL_EVENT, session_id=sessionID, started_at=sessionStartedAt, **data)
        else:
            _logger.error('Memory critical metrics are empty')
