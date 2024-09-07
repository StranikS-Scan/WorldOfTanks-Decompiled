# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/Scaleform/daapi/view/tooltips/lobby_builders.py
from armory_yard.gui.impl.lobby.feature.tooltips.entry_point_active_tooltip_view import EntryPointActiveTooltipView
from armory_yard.gui.impl.lobby.feature.tooltips.entry_point_before_progression_tooltip_view import EntryPointBeforeProgressionTooltipView
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.shared.tooltips.builders import DataBuilder, TooltipWindowBuilder
from gui.shared.tooltips import contexts, vehicle, ToolTipBaseData
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.ARMORY_YARD_AWARD_VEHICLE, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, vehicle.VehicleInfoTooltipData(contexts.AwardContext(simplifiedOnly=False))), TooltipWindowBuilder(TOOLTIPS_CONSTANTS.ARMORY_YARD_ENTRY_POINT_ACTIVE, None, EntryPointActiveTooltipData(contexts.ToolTipContext(None))), TooltipWindowBuilder(TOOLTIPS_CONSTANTS.ARMORY_YARD_ENTRY_POINT_BEFORE_PROGRESSION, None, EntryPointBeforeProgressionTooltipData(contexts.ToolTipContext(None))))


class EntryPointActiveTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(EntryPointActiveTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.ARMORY_YARD_ENTRY_POINT_ACTIVE)

    def getDisplayableData(self, vehicleCD, *args, **kwargs):
        return DecoratedTooltipWindow(EntryPointActiveTooltipView(), useDecorator=False)


class EntryPointBeforeProgressionTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(EntryPointBeforeProgressionTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.ARMORY_YARD_ENTRY_POINT_BEFORE_PROGRESSION)

    def getDisplayableData(self, vehicleCD, *args, **kwargs):
        return DecoratedTooltipWindow(EntryPointBeforeProgressionTooltipView(), useDecorator=False)
