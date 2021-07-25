# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/buy_vehicle_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts, buy_vehicle
from gui.shared.tooltips.builders import DefaultFormatBuilder, DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.BUY_VEHICLE_SLOT_TOOLTIP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, buy_vehicle.SlotTooltipData(contexts.ToolTipContext(None))), DataBuilder(TOOLTIPS_CONSTANTS.BUY_VEHICLE_AMMO_TOOLTIP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, buy_vehicle.AmmoTooltipData(contexts.ToolTipContext(None))), DefaultFormatBuilder(TOOLTIPS_CONSTANTS.BUY_VEHICLE_NO_WALLET, TOOLTIPS_CONSTANTS.COMPLEX_UI, buy_vehicle.NoWalletTooltipData(contexts.ToolTipContext(None))))
