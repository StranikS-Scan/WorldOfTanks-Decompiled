# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/mapbox_lobby_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder
from gui.Scaleform.daapi.view.lobby.mapbox.tooltips.mapbox_selector_tooltip import MapboxSelectorTooltip
from gui.Scaleform.daapi.view.lobby.mapbox.tooltips.mapbox_progression_tooltip import MapboxProgressionTooltip
from gui.Scaleform.daapi.view.lobby.mapbox.tooltips.mapbox_calendar_tooltip import MapboxCalendarTooltip
from gui.Scaleform.daapi.view.lobby.mapbox.tooltips.mapbox_calendar_day_tooltip import MapboxCalendarDayTooltip
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.MAPBOX_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, MapboxSelectorTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.MAPBOX_PROGRESSION_PREVIEW, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, MapboxProgressionTooltip(contexts.QuestContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.MAPBOX_CALENDAR, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, MapboxCalendarTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.MAPBOX_CALENDAR_DAY, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, MapboxCalendarDayTooltip(contexts.ToolTipContext(None))))
