# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/frontline_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts, frontline
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.FRONTLINE_COUPON, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, frontline.FrontlinePackPreviewTooltipData(contexts.HangarContext())), DataBuilder(TOOLTIPS_CONSTANTS.FRONTLINE_RANK, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, frontline.FrontlineRankTooltipData(contexts.HangarContext())))
