# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/football_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import football
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.FOOTBALL_BUFFON, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, football.FootballBuffonTooltipData(contexts.ToolTipContext(None))), DataBuilder(TOOLTIPS_CONSTANTS.FOOTBALL_GREEN_FLAG, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, football.GreenFlagTooltipData(contexts.ToolTipContext(None))))
