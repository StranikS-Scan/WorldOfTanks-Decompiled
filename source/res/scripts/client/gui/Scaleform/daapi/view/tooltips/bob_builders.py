# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/bob_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder, DefaultFormatBuilder
from gui.shared.tooltips.bob_tooltips import BobSelectorTooltip, BobServerPrimeTime
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.BOB_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, BobSelectorTooltip(contexts.ToolTipContext(None))), DefaultFormatBuilder(TOOLTIPS_CONSTANTS.BOB_SERVER_PRIMETIME, TOOLTIPS_CONSTANTS.COMPLEX_UI, BobServerPrimeTime(contexts.ToolTipContext(None))))
