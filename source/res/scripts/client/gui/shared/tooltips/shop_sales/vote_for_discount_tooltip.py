# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/shop_sales/vote_for_discount_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
BLOCK_WIDTH = 250

class VoteForDiscountTooltip(BlocksTooltipData):

    def __init__(self, context):
        super(VoteForDiscountTooltip, self).__init__(context, None)
        self._setWidth(BLOCK_WIDTH)
        self._setContentMargin(right=2, bottom=40)
        return

    def _packBlocks(self, *args, **kwargs):
        maxNumber = args[0]
        available = args[1]
        if available:
            titleBlock = formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(R.strings.tooltips.shopSales.voteForDiscount.available.header())), desc=text_styles.main(backport.text(R.strings.tooltips.shopSales.voteForDiscount.available.body())), descPadding=formatters.packPadding(top=2, right=-5))
            maximumFreeBlock = formatters.packImageTextBlockData(title=text_styles.neutral(backport.text(R.strings.tooltips.shopSales.voteForDiscount.available.maximumVotes(), max_number=maxNumber)), img=backport.image(R.images.gui.maps.icons.library.attentionIconFilled()), imgPadding=formatters.packPadding(top=2), txtPadding=formatters.packPadding(left=3))
            return [formatters.packBuildUpBlockData(blocks=[titleBlock], blockWidth=BLOCK_WIDTH, padding=formatters.packPadding(bottom=-10)), formatters.packBuildUpBlockData(blocks=[maximumFreeBlock], blockWidth=BLOCK_WIDTH - 20, padding=formatters.packPadding(bottom=-28))]
        availabilityBlock = formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.tooltips.shopSales.voteForDiscount.unavailable.header())), desc=text_styles.main(backport.text(R.strings.tooltips.shopSales.voteForDiscount.unavailable.availabilityBlock(), start_time=text_styles.neutral(backport.text(R.strings.tooltips.shopSales.paidShuffle.startTime())))), txtPadding=formatters.packPadding(left=-30), descPadding=formatters.packPadding(left=-4), img=backport.image(R.images.gui.maps.icons.shopSales.clock()), imgPadding=formatters.packPadding(left=-8, top=18), blockWidth=BLOCK_WIDTH)
        footerBlock = formatters.packTitleDescBlock(title=text_styles.main(backport.text(R.strings.tooltips.shopSales.voteForDiscount.unavailable.footer(), max_number=maxNumber)), padding=formatters.packPadding(top=45))
        return [formatters.packBuildUpBlockData(blocks=[availabilityBlock], blockWidth=BLOCK_WIDTH + 20, padding=formatters.packPadding(bottom=-11)), formatters.packBuildUpBlockData(blocks=[footerBlock], blockWidth=BLOCK_WIDTH, padding=formatters.packPadding(bottom=-35, top=-50))]
