# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/deprecated/mode_selector/loggers.py
from uilogging.deprecated.logging_constants import FEATURES
from uilogging.deprecated.base.loggers import BaseLogger
import BigWorld
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
        data = {'timeSpent': timeSpent,
         'tooltip': tooltip,
         'is_tooltip_advanced': isTooltipAdvanced,
         'previous_mode': previousMode,
         'current_mode': currentMode,
         'is_new_mode': isNewMode,
         'is_featured_mode': isFeaturedMode,
         '__intTime__': True}
        self.sendLogData(action, **data)
