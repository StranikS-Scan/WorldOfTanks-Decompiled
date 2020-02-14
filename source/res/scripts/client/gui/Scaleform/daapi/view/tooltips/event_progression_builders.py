# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/event_progression_builders.py
from gui.Scaleform.daapi.view.lobby.event_progression.event_progression_widget_tooltip import EventProgressionWidgetTooltip
from gui.Scaleform.daapi.view.lobby.event_progression.event_progression_selector_tooltip import EventProgressionSelectorTooltip
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.EVENT_PROGRESSION_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EventProgressionSelectorTooltip(contexts.ToolTipContext(None))), DataBuilder(TOOLTIPS_CONSTANTS.EVENT_PROGRESSION_PROGRESS_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EventProgressionWidgetTooltip(contexts.ToolTipContext(None))))
