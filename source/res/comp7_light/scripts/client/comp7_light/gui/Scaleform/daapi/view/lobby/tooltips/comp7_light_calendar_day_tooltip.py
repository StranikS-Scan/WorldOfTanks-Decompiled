# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/Scaleform/daapi/view/lobby/tooltips/comp7_light_calendar_day_tooltip.py
from comp7_light.gui.shared.tooltips import TOOLTIP_TYPE
from gui.impl.gen import R
from gui.shared.tooltips.periodic.calendar_day import PeriodicCalendarDayTooltip
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController

class Comp7LightCalendarDayTooltip(PeriodicCalendarDayTooltip):
    _controller = dependency.descriptor(IComp7LightController)
    _TOOLTIP_TYPE = TOOLTIP_TYPE.COMP7_LIGHT_CALENDAR_DAY_INFO
    _RES_ROOT = R.strings.comp7_light.calendarDay

    def _getController(self, *_):
        return self._controller
