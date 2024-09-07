# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/Scaleform/daapi/view/tooltips/winback_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips.contexts import QuestsBoosterContext, ExtendedAwardContext
from gui.shared.tooltips.builders import DataBuilder
from winback.gui.shared.tooltips.contexts import WinbackDiscountContext
from winback.gui.shared.tooltips.quests import WinbackQuestsPreviewTooltipData
from winback.gui.shared.tooltips.vehicle import WinbackExtendedVehicleInfoTooltipData, WinbackDiscountExtendedVehicleInfoTooltipData
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.WINBACK_QUESTS_PREVIEW, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, WinbackQuestsPreviewTooltipData(QuestsBoosterContext())), DataBuilder(TOOLTIPS_CONSTANTS.WINBACK_EXTENDED_AWARD_VEHICLE, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, WinbackExtendedVehicleInfoTooltipData(ExtendedAwardContext())), DataBuilder(TOOLTIPS_CONSTANTS.WINBACK_DISCOUNT_AWARD_VEHICLE, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, WinbackDiscountExtendedVehicleInfoTooltipData(WinbackDiscountContext())))
