# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/Scaleform/daapi/view/tooltips/lobby_builders.py
from gui_lootboxes.gui.bonuses.bonus_tooltips import LootBoxVehicleBlueprintFragmentTooltipData
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.LOOT_BOXES_VEHICLE_BLUEPRINT_FRAGMENT, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, LootBoxVehicleBlueprintFragmentTooltipData(contexts.ToolTipContext(None))),)
