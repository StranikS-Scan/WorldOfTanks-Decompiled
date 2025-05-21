# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/tooltips/tooltip_builders.py
from gui.shared.tooltips import contexts, advanced
from gui.shared.tooltips.builders import DataBuilder, AdvancedDataBuilder
from last_stand.gui.ls_gui_constants import LS_RENT_VEHICLE_TOOLTIP, LS_ABILITY_TOOLTIP, LS_MAIN_SHELL, LS_CAROUSEL_VEHICLE_TOOLTIP
from last_stand.gui.scaleform.daapi.view.tooltips import event
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.tooltips.vehicle_items_builders import AdvancedShellBuilder
from last_stand.gui.shared.contexts import EventVehicleContext
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(LS_RENT_VEHICLE_TOOLTIP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventVehicleInfoTooltipData(EventVehicleContext())),
     DataBuilder(LS_CAROUSEL_VEHICLE_TOOLTIP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventVehicleInfoTooltipDataDef(EventVehicleContext())),
     AdvancedDataBuilder(LS_ABILITY_TOOLTIP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventModuleBlockTooltipData(contexts.HangarContext()), advanced.HangarModuleAdvanced(contexts.HangarContext())),
     AdvancedShellBuilder(LS_MAIN_SHELL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventShellBlockToolTipData(contexts.TechMainContext()), advanced.HangarShellAdvanced(contexts.TechMainContext())))
