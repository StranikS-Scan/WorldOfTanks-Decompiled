# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/Scaleform/daapi/view/tooltips/lobby_builders.py
from advent_calendar.gui.Scaleform.daapi.view.tooltips.feature_tooltips import AdventCalendarNotRecruitedTooltipData, AdventCalendarCustomizationTooltipData
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.ADVENT_CALENDAR_TANKMAN_NOT_RECRUITED, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, AdventCalendarNotRecruitedTooltipData(contexts.NotRecruitedTankmanContext())), DataBuilder(TOOLTIPS_CONSTANTS.ADVENT_CALENDAR_CUSTOMIZATION_ITEM, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_UI, AdventCalendarCustomizationTooltipData(contexts.TechCustomizationContext())))
