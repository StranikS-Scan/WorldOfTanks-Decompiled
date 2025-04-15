# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/deprecated/ibc/loggers.py
import BigWorld
from uilogging.deprecated.logging_constants import FEATURES
from uilogging.deprecated.base.loggers import BaseLogger
from uilogging.deprecated.ibc.constants import IBC_LOG_KEYS
__all__ = ('IBCLogger',)
ACTIONS_COOLDOWN = {}
COOLDOWN = 5
RESET_CODE = 777L

class IBCLogger(BaseLogger):
    _feature = FEATURES.IN_BATTLE_COMMUNICATION

    def initLogger(self):
        self._populateTime = int(BigWorld.time())
        super(IBCLogger, self).initLogger()

    def logStatistic(self, resetTime=True, action=None, logOnce=False, restrictions=None, validate=True, **kwargs):
        if not self.ready:
            return
        if not self.arena:
            self._init()
        actionValue = kwargs.get('action_value')
        if actionValue == RESET_CODE:
            return
        currentTimestamp = int(BigWorld.time())
        if self._logKey == IBC_LOG_KEYS.IBC_CALLOUT_PANEL:
            if action not in ACTIONS_COOLDOWN:
                ACTIONS_COOLDOWN[action] = 0
            if BigWorld.time() - ACTIONS_COOLDOWN[action] <= COOLDOWN:
                return
            ACTIONS_COOLDOWN[action] = currentTimestamp
        timeDelta = int(currentTimestamp - self._populateTime)
        data = {'action_value': actionValue,
         'periphery_id': self.peripheryID,
         'arena_id': self.arenaID,
         'timeSpent': timeDelta,
         '__intTime__': True}
        self.sendLogData(action, **data)
        self._resetTime(resetTime)
