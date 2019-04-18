# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/frontline.py
import BigWorld
from gui import makeHtmlString
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, icons
from gui.shared.money import Currency
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import ITradeInController
_TOOLTIP_WIDTH = 350
_GIFTS_WIDTH = 265

class FrontlinePackPreviewTooltipData(BlocksTooltipData):
    __tradeIn = dependency.descriptor(ITradeInController)

    def __init__(self, context):
        super(FrontlinePackPreviewTooltipData, self).__init__(context, TOOLTIP_TYPE.FRONTLINE)
        self._setWidth(_TOOLTIP_WIDTH)
        self._setContentMargin(top=40, left=0, bottom=0, right=30)

    def _packBlocks(self, discount, bonuses):
        items = super(FrontlinePackPreviewTooltipData, self)._packBlocks()
        blocks = [self._getHeader()]
        if self.__tradeIn.isEnabled():
            blocks.append(formatters.packTextBlockData(padding=formatters.packPadding(left=50, bottom=15), text=_ms(text_styles.main(TOOLTIPS.FRONTLINEPACKPREVIEW_TRADEINBODY))))
        blocks.append(self._getDiscountSection(discount, bonuses))
        items.append(formatters.packBuildUpBlockData(blocks=blocks, gap=5, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL))
        return items

    def _getHeader(self):
        return formatters.packImageTextBlockData(title=text_styles.middleTitle(TOOLTIPS.FRONTLINEPACKPREVIEW_HEADER), img=backport.image(R.images.gui.maps.icons.epicBattles.modeIcon()), imgPadding=formatters.packPadding(left=10, top=-30), descPadding=formatters.packPadding(left=-7, right=30), txtPadding=formatters.packPadding(left=-7, right=30, top=-5), padding=formatters.packPadding(bottom=-17), txtGap=15, desc=text_styles.main(TOOLTIPS.FRONTLINEPACKPREVIEW_BODY))

    def _getGiftBlock(self):
        lineBlock = formatters.packImageBlockData(align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, img=backport.image(R.images.gui.maps.icons.tooltip.line()))
        textBlock = formatters.packTextWithBgBlockData(text=text_styles.concatStylesToSingleLine(icons.makeImageTag(source=backport.image(R.images.gui.maps.icons.library.icon_gift()), width=17, height=15, vSpace=0), text_styles.vehicleStatusCriticalTextSmall(TOOLTIPS.FRONTLINEPACKPREVIEW_GIFT)), bgColor=0, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)
        return formatters.packBuildUpBlockData(blocks=[lineBlock, textBlock], gap=-13, blockWidth=_TOOLTIP_WIDTH, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)

    def _getDiscountSection(self, discount, bonuses):
        discount = discount or 0
        formattedDiscount = makeHtmlString('html_templates:lobby/quests/actions', Currency.GOLD, {'value': BigWorld.wg_getGoldFormat(long(discount))})
        discountBlock = formatters.packTextBlockData(padding=formatters.packPadding(left=50), text=_ms(text_styles.main(TOOLTIPS.FRONTLINEPACKPREVIEW_DISCOUNT), value=formattedDiscount))
        return formatters.packBuildUpBlockData(blocks=[discountBlock, self._getGiftBlock(), self._getBonusSection(bonuses)], gap=25, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)

    def _getBonusSection(self, bonuses):
        hBlocks = []
        vBlocks = []
        for item in bonuses:
            if len(hBlocks) == 2:
                vBlocks.append(formatters.packBuildUpBlockData(blocks=hBlocks, blockWidth=_GIFTS_WIDTH, gap=5, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT))
                hBlocks = []
            hBlocks.append(formatters.packImageTextBlockData(desc=text_styles.main(item.text), img=item.img, blockWidth=130))

        vBlocks.append(formatters.packBuildUpBlockData(blocks=hBlocks, blockWidth=_GIFTS_WIDTH, gap=5, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT))
        return formatters.packBuildUpBlockData(blocks=vBlocks, blockWidth=_TOOLTIP_WIDTH, padding=formatters.packPadding(top=-25, left=42), layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)
