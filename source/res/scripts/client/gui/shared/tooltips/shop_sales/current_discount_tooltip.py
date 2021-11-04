# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/shop_sales/current_discount_tooltip.py
import logging
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
_logger = logging.getLogger(__name__)
_TOOLTIP_WIDTH = 354
_TOOLTIP_HEIGHT = 400

class CurrentDiscountTooltip(BlocksTooltipData):

    def __init__(self, context):
        super(CurrentDiscountTooltip, self).__init__(context, None)
        self._setWidth(_TOOLTIP_WIDTH)
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(CurrentDiscountTooltip, self)._packBlocks()
        currentDiscount = args[0]
        items.append(formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.tooltips.shopSales.currentDiscount.header())), desc=text_styles.epicTitle('-' + str(currentDiscount) + '%'), img=backport.image(R.images.gui.maps.icons.shopSales.Percent_tooltip()), txtAlign=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, imgPadding=formatters.packPadding(left=35), descPadding=formatters.packPadding(left=87, top=20), padding=formatters.packPadding(bottom=-35)))
        items.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.shopSales.currentDiscount.howToBlock.header())), desc=text_styles.main(backport.text(R.strings.tooltips.shopSales.currentDiscount.howToBlock.body())), blocksLinkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        items.append(formatters.packAlignedTextBlockData(text=text_styles.neutral(backport.text(R.strings.tooltips.shopSales.currentDiscount.footer())), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        return items
