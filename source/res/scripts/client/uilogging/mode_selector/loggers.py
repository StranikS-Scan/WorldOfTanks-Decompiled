# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/mode_selector/loggers.py
from uilogging.logging_constants import FEATURES, KAFKA_TOPICS
from uilogging.base.loggers import BaseLogger
from uilogging import loggingSettings
import BigWorld
from helpers import time_utils
from wotdecorators import noexcept
__all__ = ('ModeSelectorUILogger',)

class ModeSelectorUILogger(BaseLogger):
    _feature = FEATURES.MODE_SELECTOR

    def __init__(self, *args, **kwargs):
        super(ModeSelectorUILogger, self).__init__(*args, **kwargs)
        self._uiTooltipOpened = None
        return

    def initLogger(self):
        super(ModeSelectorUILogger, self).initLogger()
        self._populateTime = int(BigWorld.time())

    @noexcept
    def logStatistic(self, action, timeSpent=0, resetTime=False, logOnce=False, restrictions=None, validate=False, tooltip=None, isTooltipAdvanced=None, previousMode=None, currentMode=None, isNewMode=None, isFeaturedMode=None, **kwargs):
        if not self.ready:
            return
        data = {'account_id': self._player,
         'key': self._logKey,
         'time_spent': timeSpent,
         'action': action,
         'realm': loggingSettings.realm,
         'feature': KAFKA_TOPICS[self._feature],
         'time': int(time_utils.getServerRegionalTime()),
         'tooltip': tooltip,
         'is_tooltip_advanced': isTooltipAdvanced,
         'previous_mode': previousMode,
         'current_mode': currentMode,
         'is_new_mode': isNewMode,
         'is_featured_mode': isFeaturedMode}
        self.sendLogData(data)
