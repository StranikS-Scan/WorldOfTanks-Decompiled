# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/feature/tooltips/calendar_day_tooltip.py
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.shared.tooltips import TooltipType
from gui.impl.gen import R
from gui.shared.tooltips.periodic.calendar_day import PeriodicCalendarDayTooltip
from helpers.time_utils import ONE_DAY

class FunRandomCalendarDayTooltip(PeriodicCalendarDayTooltip, FunSubModesWatcher):
    _TOOLTIP_TYPE = TooltipType.FUN_RANDOM
    _RES_ROOT = R.strings.fun_random.calendarDay

    def _getController(self, *_):
        return self.getDesiredSubMode()


class FunRandomModeSelectorCalendarTooltip(FunRandomCalendarDayTooltip, FunSubModesWatcher):

    def _getController(self, subModeID=None, *_):
        return self._funRandomCtrl.subModesInfo if subModeID is None else self.getSubMode(subModeID)

    def _isValidPrimeTimes(self, serversPeriodsMapping):
        periods = [ periods for serverPeriods in serversPeriodsMapping.values() for periods in serverPeriods ]
        return any([ period[1] - period[0] != ONE_DAY for period in periods ])
