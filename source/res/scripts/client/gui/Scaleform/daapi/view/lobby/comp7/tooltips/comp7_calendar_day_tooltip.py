# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/comp7/tooltips/comp7_calendar_day_tooltip.py
from gui.impl.gen import R
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips.periodic.calendar_day import PeriodicCalendarDayTooltip
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7CalendarDayTooltip(PeriodicCalendarDayTooltip):
    _controller = dependency.descriptor(IComp7Controller)
    _TOOLTIP_TYPE = TOOLTIP_TYPE.COMP7_CALENDAR_DAY_INFO
    _RES_ROOT = R.strings.comp7.calendarDay
