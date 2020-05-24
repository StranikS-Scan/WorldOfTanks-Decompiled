# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/statistic/loggers.py
from collections import defaultdict
import json
import BigWorld
import BattleReplay
from async import async, await, AsyncReturn
from debug_utils_bootcamp import LOG_STATISTIC
from gui.shared.utils import getPlayerDatabaseID
from bootcamp.Bootcamp import g_bootcamp
import constants
from .validators import TimeValidator
from .logging_constants import ACTIONS_HINTS_TO_LOG_ONCE, ACTION_SEQUENCES
from . import STATISTIC_SETTINGS
__all__ = ('BootcampUILogger',)

def isSPAAttributeExists():
    if not BigWorld.player():
        return False
    elif BattleReplay.isPlaying():
        return False
    elif STATISTIC_SETTINGS.TEST_MODE:
        return True
    else:
        bootcampSPAFlag = BigWorld.player().spaFlags.getFlag(constants.SPA_ATTRS.LOGGING_ENABLED)
        return bootcampSPAFlag and bootcampSPAFlag is not None


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


class BaseLogger(object):
    _logKey = None
    _validator = None

    def __init__(self, *args, **kwargs):
        self._player = None
        self._isNewbie = None
        self._ready = False
        self._enabled = isSPAAttributeExists()
        return

    @classmethod
    def setLogKey(cls, logKey):
        cls._logKey = logKey

    @property
    def ready(self):
        return self._ready if STATISTIC_SETTINGS.TEST_MODE else self._ready and self._enabled

    def initLogger(self):
        self._player = getPlayerDatabaseID()
        self._isNewbie = None
        return

    def logStatistic(self, **kwargs):
        raise NotImplementedError

    @async
    def _sendIntoKafka(self, data):
        BigWorld.fetchURL(url=STATISTIC_SETTINGS.HOST, callback=lambda x: x, headers=STATISTIC_SETTINGS.REQUEST_HEADERS, timeout=STATISTIC_SETTINGS.REQUEST_TIMEOUT, method=STATISTIC_SETTINGS.HTTP_METHOD, postdata=json.dumps(data))
        raise AsyncReturn(True)

    def _sendIntoClientLog(self, data):
        LOG_STATISTIC(str(data))

    @async
    def sendLogData(self, data):
        if STATISTIC_SETTINGS.CLIENT_LOG:
            self._sendIntoClientLog(data)
        yield await(self._sendIntoKafka(data))


class BootcampUILogger(BaseLogger):
    _validator = TimeValidator

    def __init__(self, *args, **kwargs):
        super(BootcampUILogger, self).__init__(*args, **kwargs)
        self._populateTime = None
        self._loggingCache = None
        return

    def _resetTime(self, resetTime):
        if resetTime:
            self._populateTime = BigWorld.time()

    def _updateFromContext(self, data):
        contextKeyMapping = {'is_newbie': 'isNewbie',
         'lesson_id': 'lessonNum'}
        context = g_bootcamp.getContext()
        for key, contextKey in contextKeyMapping.items():
            data[key] = context.get(contextKey, None)

        return

    def initLogger(self):
        if self.ready:
            return
        super(BootcampUILogger, self).initLogger()
        self._ready = True
        self._populateTime = BigWorld.time()
        self._loggingCache = LoggingCache()

    def getActionFromSequence(self, action):
        actionToLog, finalAction = ACTION_SEQUENCES[action]
        if actionToLog in self._loggingCache:
            actionToLog = finalAction
        return None if actionToLog in self._loggingCache else actionToLog

    def logStatistic(self, resetTime=True, action=None, logOnce=False):
        if not self.ready:
            return
        elif (logOnce or action in ACTIONS_HINTS_TO_LOG_ONCE) and action in self._loggingCache:
            return
        else:
            timeDelta = int(BigWorld.time() - self._populateTime)
            if self._validator and not self._validator.isValid(self._logKey, timeDelta):
                return
            if action in ACTION_SEQUENCES:
                action = self.getActionFromSequence(action)
                if not action:
                    return
            data = {'account_id': self._player,
             'key': self._logKey,
             'time_spent': timeDelta,
             'is_newbie': self._isNewbie,
             'action': action,
             'lesson_id': None,
             'realm': constants.CURRENT_REALM}
            self._updateFromContext(data)
            self.sendLogData(data)
            self._loggingCache.add(action)
            self._resetTime(resetTime)
            return
