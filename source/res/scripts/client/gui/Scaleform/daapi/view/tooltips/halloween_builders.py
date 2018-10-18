# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/halloween_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import halloween
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.HALLOWEEN_HANGAR_TOOLTIP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, halloween.HangarTooltip(contexts.HalloweenContext())), DataBuilder(TOOLTIPS_CONSTANTS.HALLOWEEN_PROGRESS_TOOLTIP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, halloween.ProgressTooltip(contexts.HalloweenContext())))
