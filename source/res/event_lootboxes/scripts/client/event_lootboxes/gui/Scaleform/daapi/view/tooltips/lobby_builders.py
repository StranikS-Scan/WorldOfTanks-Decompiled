# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_lootboxes/scripts/client/event_lootboxes/gui/Scaleform/daapi/view/tooltips/lobby_builders.py
from event_lootboxes.gui.event_lootboxes.bonus_tooltips import EventLootBoxVehicleBlueprintFragmentTooltipData
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.EVENT_LOOT_BOXES_VEHICLE_BLUEPRINT_FRAGMENT, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EventLootBoxVehicleBlueprintFragmentTooltipData(contexts.ToolTipContext(None))),)
