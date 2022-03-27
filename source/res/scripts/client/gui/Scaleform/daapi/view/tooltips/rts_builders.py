# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/rts_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts, module, advanced, tankman, vehicle, shell
from gui.shared.tooltips.builders import DataBuilder, AdvancedDataBuilder
from gui.Scaleform.daapi.view.tooltips.vehicle_items_builders import _shellAdvancedBlockCondition
from gui.shared.tooltips.rts.rts_selector_tooltip import RtsSelectorTooltip
from gui.shared.tooltips.rts.rts_calendar_day_tooltip import RtsCalendarDayTooltip
from gui.shared.tooltips.rts.rts_roster import RtsVehicleRestrictionsTooltip
from gui.shared.tooltips import common
__all__ = ('getTooltipBuilders',)

def _advancedBlockCondition(context):

    def advancedTooltipExist(*args):
        item = context.buildItem(*args)
        return item.getGUIEmblemID() in advanced.MODULE_MOVIES

    return advancedTooltipExist


def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.RTS_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RtsSelectorTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.RTS_CALENDAR_DAY_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RtsCalendarDayTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.RTS_VEHICLE_RESTRICTIONS, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RtsVehicleRestrictionsTooltip(contexts.ToolTipContext(None))),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.RTS_ROSTER_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, module.ModuleBlockTooltipData(contexts.RtsRosterContext()), advanced.HangarModuleAdvanced(contexts.RtsRosterContext()), condition=_advancedBlockCondition(contexts.RtsRosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.RTS_ROSTER_SHELL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, shell.ShellBlockToolTipData(contexts.RtsRosterContext(), basicDataAllowed=True), advanced.HangarShellAdvanced(contexts.RtsRosterContext()), condition=_shellAdvancedBlockCondition(contexts.RtsRosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.RTS_ROSTER_TANKMAN, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, tankman.RtsTankmanTooltipDataBlock(contexts.RtsRosterTankmanContext(fieldsToExclude=('count',))), advanced.TankmanTooltipAdvanced(contexts.RtsRosterTankmanContext(fieldsToExclude=('count',)))),
     DataBuilder(TOOLTIPS_CONSTANTS.RTS_VEHICLE_PARAMETERS, TOOLTIPS_CONSTANTS.VEHICLE_PARAMETERS_UI, vehicle.BaseVehicleAdvancedParametersTooltipData(contexts.RtsSelectedVehicleParametersContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.RTS_CAROUSEL_VEHICLE, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, vehicle.VehicleInfoTooltipData(contexts.RtsCarouselContext())),
     RtsCurrencyBuilder(TOOLTIPS_CONSTANTS.RTS_SPECIAL_CURRENCY, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI))


class RtsCurrencyBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(RtsCurrencyBuilder, self).__init__(tooltipType, linkage, common.RtsCurrencyTooltipData(contexts.ToolTipContext(None)))
        return

    def build(self, manager, formatType, advanced_, *args, **kwargs):
        return self._provider
