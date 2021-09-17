# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ranked/ranked_calendar_day_tooltip.py
from gui.impl.gen import R
from helpers import dependency
from gui.shared.tooltips import TOOLTIP_TYPE
from skeletons.gui.game_control import IRankedBattlesController
from gui.shared.tooltips.periodic.calendar_day import PeriodicCalendarDayTooltip

class RankedCalendarDayTooltip(PeriodicCalendarDayTooltip):
    _RES_ROOT = R.strings.ranked_battles.calendarDay
    _TOOLTIP_TYPE = TOOLTIP_TYPE.RANKED_CALENDAR_DAY
    _controller = dependency.descriptor(IRankedBattlesController)
