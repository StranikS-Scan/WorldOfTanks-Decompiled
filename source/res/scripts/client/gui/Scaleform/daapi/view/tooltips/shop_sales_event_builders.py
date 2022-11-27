# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/shop_sales_event_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder
from gui.shared.tooltips.shop_sales.current_discount_tooltip import CurrentDiscountTooltip
from gui.shared.tooltips.shop_sales.free_shuffle_tooltip import FreeShuffleTooltip
from gui.shared.tooltips.shop_sales.paid_shuffle_tooltip import PaidShuffleTooltip
from gui.shared.tooltips.shop_sales.vote_for_discount_tooltip import VoteForDiscountTooltip
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.CURRENT_DISCOUNT_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, CurrentDiscountTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.SHOP_SALES_FREE_SHUFFLE_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, FreeShuffleTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.SHOP_SALES_PAID_SHUFFLE_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, PaidShuffleTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.SHOP_SALES_VOTE_FOR_DISCOUNT, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, VoteForDiscountTooltip(contexts.ToolTipContext(None))))
