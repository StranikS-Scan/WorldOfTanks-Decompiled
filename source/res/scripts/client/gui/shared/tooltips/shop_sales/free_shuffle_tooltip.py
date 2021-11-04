# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/shop_sales/free_shuffle_tooltip.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import formatPrice, text_styles
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
BLOCK_WIDTH = 278

class FreeShuffleTooltip(BlocksTooltipData):

    def __init__(self, context):
        super(FreeShuffleTooltip, self).__init__(context, None)
        self._setWidth(BLOCK_WIDTH)
        self._setContentMargin(left=20, bottom=12, right=-12)
        return

    def _packBlocks(self, *args, **kwargs):
        maxNumber, paidShuffleCost = args
        titleBlock = formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(R.strings.tooltips.shopSales.freeShuffle.header())), desc=text_styles.main(backport.text(R.strings.tooltips.shopSales.freeShuffle.body())), padding=formatters.packPadding(bottom=-6))
        maximumFreeBlock = formatters.packImageTextBlockData(title=text_styles.neutral(backport.text(R.strings.tooltips.shopSales.freeShuffle.maximumFree(), max_number=maxNumber)), img=backport.image(R.images.gui.maps.icons.library.attentionIconFilled()), txtPadding=formatters.packPadding(top=-2, left=3), imgPadding=formatters.packPadding(left=2), ignoreImageSize=True)
        paidBlock = formatters.packTextBlockData(text=text_styles.concatStylesWithSpace(formatPrice(paidShuffleCost, reverse=True, useIcon=True, useStyle=True), text_styles.main(backport.text(R.strings.tooltips.shopSales.freeShuffle.paidShuffleCost()))))
        return [formatters.packBuildUpBlockData(blocks=[titleBlock]), formatters.packBuildUpBlockData(blocks=[maximumFreeBlock], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE), formatters.packBuildUpBlockData(blocks=[paidBlock])]
