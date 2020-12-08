# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/ny/loggers.py
import time
import BigWorld
from uilogging.logging_constants import FEATURES, KAFKA_TOPICS
from uilogging.base.loggers import BaseLogger
from uilogging import loggingSettings
__all__ = ('NYLogger',)

class NYLogger(BaseLogger):
    _feature = FEATURES.NEW_YEAR

    def initLogger(self):
        self._populateTime = int(BigWorld.time())
        super(NYLogger, self).initLogger()

    def logStatistic(self, resetTime=True, action=None, logOnce=False, restrictions=None, validate=True, **kwargs):
        if not self.ready:
            return
        currentTimestamp = int(BigWorld.time())
        timeDelta = int(currentTimestamp - self._populateTime)
        data = {'account_id': self._player,
         'key': self._logKey,
         'action': action,
         'realm': loggingSettings.realm,
         'feature': KAFKA_TOPICS[self._feature],
         'time_spent': timeDelta,
         'time': int(time.time())}
        self.sendLogData(data)
        self._resetTime(resetTime)
