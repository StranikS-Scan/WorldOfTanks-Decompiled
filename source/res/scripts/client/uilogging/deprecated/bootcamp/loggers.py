# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/deprecated/bootcamp/loggers.py
from collections import defaultdict
import BigWorld
from bootcamp.Bootcamp import g_bootcamp
from uilogging.deprecated.bootcamp.validators import TimeValidator
from uilogging.deprecated.logging_constants import FEATURES
from uilogging.deprecated.base.loggers import BaseLogger
from uilogging.deprecated.bootcamp.constants import ACTIONS_HINTS_TO_LOG_ONCE, ACTION_SEQUENCES
__all__ = ('BootcampUILogger',)

class LoggingCacheMeta(type):
    _instance = None

    def __call__(cls):
        if cls._instance is None:
            cls._instance = super(LoggingCacheMeta, cls).__call__()
        return cls._instance


class LoggingCache(object):
    __metaclass__ = LoggingCacheMeta

    def __init__(self):
        self._data = defaultdict(set)

    def __contains__(self, key):
        return key in self.data

    def add(self, key):
        self.data.add(key)

    @property
    def data(self):
        return self._data[g_bootcamp.getLessonNum()]


class BootcampUILogger(BaseLogger):
    _validator = TimeValidator
    _feature = FEATURES.BOOTCAMP

    def __init__(self, *args, **kwargs):
        super(BootcampUILogger, self).__init__(*args, **kwargs)
        self._populateTime = None
        self._loggingCache = None
        return

    def _updateFromContext(self, data):
        contextKeyMapping = {'is_newbie': 'isNewbie',
         'lesson_id': 'lessonNum'}
        context = g_bootcamp.getContext()
        for key, contextKey in contextKeyMapping.items():
            data[key] = context.get(contextKey, None)

        return

    def initLogger(self):
        super(BootcampUILogger, self).initLogger()
        self._populateTime = int(BigWorld.time())
        self._loggingCache = LoggingCache()

    def getActionFromSequence(self, action):
        actionToLog, finalAction = ACTION_SEQUENCES[action]
        if actionToLog in self._loggingCache:
            actionToLog = finalAction
        return None if actionToLog in self._loggingCache else actionToLog

    def logStatistic(self, resetTime=True, action=None, logOnce=False, restrictions=None, validate=True, **kwargs):
        if not self.ready:
            return
        elif (logOnce or action in ACTIONS_HINTS_TO_LOG_ONCE) and action in self._loggingCache:
            return
        else:
            currentTimestamp = int(BigWorld.time())
            timeDelta = currentTimestamp - self._populateTime
            if self._validator and not self._validator.isValid(self._logKey, timeDelta, validate):
                return
            if action in ACTION_SEQUENCES:
                action = self.getActionFromSequence(action)
                if not action:
                    return
            data = {'timeSpent': timeDelta,
             'is_newbie': self._isNewbie,
             'lesson_id': None,
             '__intTime__': True}
            self._updateFromContext(data)
            if restrictions:
                for targetField, targetValue in restrictions.iteritems():
                    if callable(targetValue):
                        if not targetValue(data.get(targetField)):
                            return
                    if data.get(targetField) != targetValue:
                        return

            self.sendLogData(action, **data)
            self._loggingCache.add(action)
            self._resetTime(resetTime)
            return
