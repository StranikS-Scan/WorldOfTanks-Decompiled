# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/mapbox/tooltips/mapbox_calendar_day_tooltip.py
from gui.impl.gen import R
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips.periodic.calendar_day import PeriodicCalendarDayTooltip
from helpers import dependency
from skeletons.gui.game_control import IMapboxController

class MapboxCalendarDayTooltip(PeriodicCalendarDayTooltip):
    _controller = dependency.descriptor(IMapboxController)
    _TOOLTIP_TYPE = TOOLTIP_TYPE.MAPBOX_CALENDAR_DAY
    _RES_ROOT = R.strings.mapbox.calendarDay

    def _getController(self, *_):
        return self._controller

    def _isValidPrimeTimes(self, serversPeriodsMapping):
        periods = [ periods for serverPeriods in serversPeriodsMapping.values() for periods in serverPeriods ]
        return len(periods) > 0
