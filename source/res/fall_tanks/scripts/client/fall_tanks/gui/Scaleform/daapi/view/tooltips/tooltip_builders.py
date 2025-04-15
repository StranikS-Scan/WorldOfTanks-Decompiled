# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/tooltips/tooltip_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips.builders import DataBuilder
from fall_tanks.gui.fall_tanks_gui_constants import FallTanksTankSetupConstants
from fall_tanks.gui.shared.tooltips import contexts
from fall_tanks.gui.shared.tooltips.fall_tanks_tooltips import FallTanksShellBlockToolTipData, FallTanksAbilitiesBlockToolTipData
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(FallTanksTankSetupConstants.FALL_TANK_SHELLS, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, FallTanksShellBlockToolTipData(contexts.FallTanksHangarAmmoContext(), TOOLTIP_TYPE.SHELL)), DataBuilder(FallTanksTankSetupConstants.FALL_TANK_CONSUMABLES, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, FallTanksAbilitiesBlockToolTipData(contexts.FallTanksHangarAmmoContext(), TOOLTIP_TYPE.EQUIPMENT)))
