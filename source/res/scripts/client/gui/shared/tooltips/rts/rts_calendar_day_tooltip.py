# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/rts/rts_calendar_day_tooltip.py
from gui.impl.gen import R
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips.periodic.calendar_day import PeriodicCalendarDayTooltip
from helpers import dependency
from skeletons.gui.game_control import IRTSBattlesController

class RtsCalendarDayTooltip(PeriodicCalendarDayTooltip):
    _RES_ROOT = R.strings.rts_battles.calendarDay
    _TOOLTIP_TYPE = TOOLTIP_TYPE.RTS_CALENDAR_DAY
    _controller = dependency.descriptor(IRTSBattlesController)
