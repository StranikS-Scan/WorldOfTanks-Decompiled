# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/Scaleform/__init__.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as _TOOLTIPS
from gui.shared.system_factory import registerLobbyTooltipsBuilders

def registerAdventCalendarScaleform():
    registerLobbyTooltipsBuilders([('advent_calendar.gui.Scaleform.daapi.view.tooltips.lobby_builders', _TOOLTIPS.ADVENT_CALENDAR_SET)])
