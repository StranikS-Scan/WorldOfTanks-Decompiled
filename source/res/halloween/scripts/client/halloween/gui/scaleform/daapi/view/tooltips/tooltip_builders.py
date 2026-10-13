# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/tooltips/tooltip_builders.py
from __future__ import absolute_import
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.shared.tooltips import contexts, advanced, ToolTipBaseData
from gui.shared.tooltips.builders import DataBuilder, AdvancedDataBuilder, TooltipWindowBuilder
from halloween.gui.halloween_gui_constants import HALLOWEEN_CAROUSEL_VEHICLE_TOOLTIP, HALLOWEEN_ABILITY_TOOLTIP, HALLOWEEN_MAIN_SHELL, HALLOWEEN_VEHICLE_FEATURE_TOOLTIP
from halloween.gui.impl.lobby.tooltips.vehicle_tooltip import VehicleTooltipView
from halloween.gui.scaleform.daapi.view.tooltips import event
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.tooltips.vehicle_items_builders import AdvancedShellBuilder
from halloween.gui.shared.contexts import EventVehicleContext
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(HALLOWEEN_CAROUSEL_VEHICLE_TOOLTIP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventVehicleInfoTooltipData(EventVehicleContext())),
     TooltipWindowBuilder(HALLOWEEN_VEHICLE_FEATURE_TOOLTIP, None, VehicleTooltipContentWindowData(contexts.ToolTipContext(None))),
     AdvancedDataBuilder(HALLOWEEN_ABILITY_TOOLTIP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventModuleBlockTooltipData(contexts.HangarContext()), advanced.HangarModuleAdvanced(contexts.HangarContext())),
     AdvancedShellBuilder(HALLOWEEN_MAIN_SHELL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventShellBlockToolTipData(contexts.TechMainContext()), advanced.HangarShellAdvanced(contexts.TechMainContext())))


class VehicleTooltipContentWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(VehicleTooltipContentWindowData, self).__init__(context, HALLOWEEN_VEHICLE_FEATURE_TOOLTIP)

    def getDisplayableData(self, vehicleCD, isQuestVisible=True, isStatusVisible=True, *_, **kwargs):
        return DecoratedTooltipWindow(VehicleTooltipView(vehicleCD, isQuestVisible=isQuestVisible, isStatusVisible=isStatusVisible, **kwargs), useDecorator=False)
