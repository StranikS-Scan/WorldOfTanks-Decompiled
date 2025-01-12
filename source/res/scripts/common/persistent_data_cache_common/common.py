# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/persistent_data_cache_common/common.py
import typing
import time
import logging
from contextlib import contextmanager
LOGGER_NAME = 'PersistentDataCache'
DEFAULT_SAVING_TIMEOUT = 120.0

def getLogger(*names):
    return logging.getLogger('{}'.format('.'.join((LOGGER_NAME,) + names)))


_logger = getLogger('Metrics')

class MeasureExecutionTime(object):
    __slots__ = ('_logger', '_metricName', '_totalTime')

    def __init__(self, metricName, logger=None):
        self._logger = logger or _logger
        self._metricName = metricName
        self._totalTime = 0.0

    def printTotalTime(self, reset=True):
        self._logger.debug('%s total time: %s', self._createMetricName(), self._totalTime)
        if reset:
            self._totalTime = 0.0

    @contextmanager
    def start(self, section=''):
        startTime = time.time()
        try:
            yield
        finally:
            endTime = time.time() - startTime
            self._totalTime += endTime
            self._logger.debug('%s executed in %s seconds.', self._createMetricName(section), endTime)

    def _createMetricName(self, section=''):
        return (self._metricName, section) if section else (self._metricName,)

    def __call__(self, func, section=''):

        def wrapper(*args, **kwargs):
            startTime = time.time()
            result = func(*args, **kwargs)
            endTime = time.time() - startTime
            self._totalTime += endTime
            self._logger.debug('%s executed in %s seconds.', self._createMetricName(section), endTime)
            return result

        return wrapper
