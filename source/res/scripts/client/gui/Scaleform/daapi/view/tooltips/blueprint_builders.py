# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/blueprint_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import blueprint
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.BLUEPRINT_INFO, TOOLTIPS_CONSTANTS.BLUEPRINT_UI, blueprint.VehicleBlueprintTooltipData(contexts.BlueprintContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BLUEPRINT_FRAGMENT_INFO, TOOLTIPS_CONSTANTS.BLUEPRINT_FRAGMENT_UI, blueprint.BlueprintFragmentTooltipData(contexts.BlueprintContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BLUEPRINT_EMPTY_SLOT_INFO, TOOLTIPS_CONSTANTS.BLUEPRINT_EMPTY_SLOT_UI, blueprint.BlueprintEmptySlotTooltipData(contexts.BlueprintContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BLUEPRINT_CONVERT_INFO, TOOLTIPS_CONSTANTS.BLUEPRINT_EMPTY_SLOT_UI, blueprint.ConvertInfoBlueprintTooltipData(contexts.BlueprintContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BLUEPRINT_RANDOM_INFO, TOOLTIPS_CONSTANTS.BLUEPRINT_FRAGMENT_UI, blueprint.BlueprintFragmentRandomTooltipData(contexts.BlueprintContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BLUEPRINT_RANDOM_NATIONAL_INFO, TOOLTIPS_CONSTANTS.BLUEPRINT_FRAGMENT_UI, blueprint.BlueprintFragmentRandomNationalTooltipData(contexts.BlueprintContext())))
