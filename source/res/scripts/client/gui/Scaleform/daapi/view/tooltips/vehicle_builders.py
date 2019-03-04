# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/vehicle_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import advanced
from gui.shared.tooltips import contexts
from gui.shared.tooltips import vehicle
from gui.shared.tooltips.builders import DataBuilder, DefaultFormatBuilder, AdvancedDataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.CAROUSEL_VEHICLE, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, vehicle.VehicleInfoTooltipData(contexts.CarouselContext())),
     InventoryVehicleBuilder(TOOLTIPS_CONSTANTS.INVENTORY_VEHICLE, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI),
     DataBuilder(TOOLTIPS_CONSTANTS.TECHTREE_VEHICLE, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, vehicle.VehicleInfoTooltipData(contexts.TechTreeContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.TECHTREE_VEHICLE_STATUS, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, vehicle.VehicleStatusTooltipData(contexts.TechTreeContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.SHOP_VEHICLE, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, vehicle.VehicleInfoTooltipData(contexts.ShopContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.AWARD_VEHICLE, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, vehicle.VehicleInfoTooltipData(contexts.AwardContext())),
     DefaultFormatBuilder(TOOLTIPS_CONSTANTS.TRADE_IN, TOOLTIPS_CONSTANTS.COMPLEX_UI, vehicle.VehicleTradeInTooltipData(contexts.HangarContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.TRADE_IN_PRICE, TOOLTIPS_CONSTANTS.TRADE_IN_PRICE, vehicle.VehicleTradeInPriceTooltipData(contexts.HangarContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.HISTORICAL_VEHICLE, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, vehicle.VehicleInfoTooltipData(contexts.HangarContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.VEHICLE_SIMPLE_PARAMETERS, TOOLTIPS_CONSTANTS.VEHICLE_PARAMETERS_UI, vehicle.VehicleSimpleParametersTooltipData(contexts.HangarParamContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BASE_VEHICLE_PARAMETERS, TOOLTIPS_CONSTANTS.VEHICLE_PARAMETERS_UI, vehicle.BaseVehicleAdvancedParametersTooltipData(contexts.BaseHangarParamContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.VEHICLE_CMP_PARAMETERS, TOOLTIPS_CONSTANTS.VEHICLE_PARAMETERS_UI, vehicle.BaseVehicleAdvancedParametersTooltipData(contexts.CmpParamContext()), advanced.VehicleParametersAdvanced(contexts.CmpParamContext()), condition=advanced.VehicleParametersAdvanced.readyForAdvanced),
     DataBuilder(TOOLTIPS_CONSTANTS.VEHICLE_AVG_PARAMETERS, TOOLTIPS_CONSTANTS.VEHICLE_PARAMETERS_UI, vehicle.VehicleAvgParameterTooltipData(contexts.HangarParamContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.VEHICLE_ADVANCED_PARAMETERS, TOOLTIPS_CONSTANTS.VEHICLE_PARAMETERS_UI, vehicle.VehicleAdvancedParametersTooltipData(contexts.HangarParamContext()), advanced.VehicleParametersAdvanced(contexts.HangarParamContext()), condition=advanced.VehicleParametersAdvanced.readyForAdvanced),
     DataBuilder(TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_SIMPLE_PARAMETERS, TOOLTIPS_CONSTANTS.VEHICLE_PARAMETERS_UI, vehicle.VehicleSimpleParametersTooltipData(contexts.PreviewParamContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_AVG_PARAMETERS, TOOLTIPS_CONSTANTS.VEHICLE_PARAMETERS_UI, vehicle.VehicleAvgParameterTooltipData(contexts.PreviewParamContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_ADVANCED_PARAMETERS, TOOLTIPS_CONSTANTS.VEHICLE_PARAMETERS_UI, vehicle.VehicleAdvancedParametersTooltipData(contexts.PreviewParamContext()), advanced.VehicleParametersAdvanced(contexts.PreviewParamContext()), condition=advanced.VehicleParametersAdvanced.readyForAdvanced),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_CREW_MEMBER, TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_CREW_MEMBER_UI, vehicle.VehiclePreviewCrewMemberTooltipData(contexts.PreviewContext()), advanced.TankmanPreviewTooltipAdvanced(contexts.PreviewContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_20_CREW_MEMBER, TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_CREW_MEMBER_UI, vehicle.VehiclePreview20CrewMemberTooltipData(contexts.PreviewContext()), advanced.TankmanPreviewTooltipAdvanced(contexts.PreviewContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.TECHTREE_VEHICLE_ANNOUNCEMENT, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, vehicle.VehicleAnnouncementParametersTooltipData(contexts.VehicleAnnouncementContext())))


class InventoryVehicleBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(InventoryVehicleBuilder, self).__init__(tooltipType, linkage, vehicle.VehicleInfoTooltipData(contexts.InventoryContext()))

    def _buildData(self, _advanced, intCD, *args, **kwargs):
        return super(InventoryVehicleBuilder, self)._buildData(_advanced, intCD)
