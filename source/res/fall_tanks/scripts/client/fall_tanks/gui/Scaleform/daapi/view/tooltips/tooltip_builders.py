# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/tooltips/tooltip_builders.py
from __future__ import absolute_import
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips.builders import DataBuilder
from fall_tanks.gui.fall_tanks_gui_constants import FallTanksTooltipConstants
from fall_tanks.gui.shared.tooltips import fall_tanks_contexts
from fall_tanks.gui.shared.tooltips.fall_tanks_tooltips import FallTanksShellBlockToolTipData, FallTanksAbilitiesBlockToolTipData
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(FallTanksTooltipConstants.FALL_TANKS_CUSTOM_SHELLS, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, FallTanksShellBlockToolTipData(fall_tanks_contexts.FallTanksHangarLoadoutContext())), DataBuilder(FallTanksTooltipConstants.FALL_TANKS_CUSTOM_ABILITIES, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, FallTanksAbilitiesBlockToolTipData(fall_tanks_contexts.FallTanksHangarLoadoutContext())))
