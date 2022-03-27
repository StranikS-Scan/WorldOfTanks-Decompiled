# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/rts/rts_battle_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
_TOOLTIP_MIN_WIDTH = 460

class RTSOrderTooltipData(BlocksTooltipData):

    def __init__(self, ctx):
        super(RTSOrderTooltipData, self).__init__(ctx, None)
        self._setContentMargin(top=14, left=3, bottom=14, right=14)
        self._setWidth(_TOOLTIP_MIN_WIDTH)
        return

    def _packBlocks(self, order):
        items = super(RTSOrderTooltipData, self)._packBlocks()
        items.append(formatters.packImageTextBlockData(title=text_styles.middleTitle(backport.text(R.strings.rts_battles.tooltip.order.dyn(order).title())), desc=text_styles.main(backport.text(R.strings.rts_battles.tooltip.order.dyn(order).desc())), txtPadding=formatters.packPadding(top=3, left=27)))
        return items
