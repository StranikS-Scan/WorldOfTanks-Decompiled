# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/buy_vehicle.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, formatActionPrices
from gui.shared.tooltips import ToolTipBaseData, TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.gui_item_economics import ItemPrice

def _extendBlockListByDiscount(items, itemPrice):
    if not itemPrice.isActionPrice():
        return
    formattedOldPrice, formattedNewPrice = formatActionPrices(itemPrice.defPrice.toMoneyTuple(), itemPrice.price.toMoneyTuple(), True, True)
    items.append(formatters.packTitleDescAsComplexBlock(backport.text(R.strings.tooltips.actionPrice.header()), backport.text(R.strings.tooltips.actionPrice.body(), oldPrice=formattedOldPrice, newPrice=formattedNewPrice), headerStyle=text_styles.middleTitle, padding=formatters.packPadding(top=-3)))


class BaseItemTooltipData(BlocksTooltipData):

    def __init__(self, ctx):
        super(BaseItemTooltipData, self).__init__(ctx, TOOLTIP_TYPE.BUY_VEHICLE)
        self._setWidth(320)
        self._setContentMargin(bottom=8)


class AmmoTooltipData(BaseItemTooltipData):

    def _packBlocks(self, itemPrice):
        items = []
        rAmmo = R.strings.tooltips.buyVehicle.ammo
        items.append(formatters.packTitleDescAsComplexBlock(backport.text(rAmmo.header()), backport.text(rAmmo.body()), text_styles.middleTitle if not itemPrice.isActionPrice() else None, padding=formatters.packPadding(bottom=-3)))
        _extendBlockListByDiscount(items, itemPrice)
        return items


class SlotTooltipData(BaseItemTooltipData):

    def _packBlocks(self, itemPrice, hasEmptySlot):
        items = []
        if hasEmptySlot:
            rSlots = R.strings.tooltips.buyVehicle.slots
            items.append(formatters.packTitleDescAsComplexBlock(backport.text(rSlots.header()), backport.text(rSlots.body()), text_styles.middleTitle if not itemPrice.isActionPrice() else None, padding=formatters.packPadding(bottom=-3)))
        else:
            rNoSlots = R.strings.tooltips.buyVehicle.noSlots
            items.append(formatters.packTitleDescAsComplexBlock(backport.text(rNoSlots.header()), backport.text(rNoSlots.body()), text_styles.errorMedium if not itemPrice.isActionPrice() else text_styles.unavailable, padding=formatters.packPadding(bottom=-3)))
        _extendBlockListByDiscount(items, itemPrice)
        return items


class NoWalletTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(NoWalletTooltipData, self).__init__(context, TOOLTIP_TYPE.BUY_VEHICLE)

    def getDisplayableData(self):
        rNoWallet = R.strings.tooltips.buyVehicle.noWallet
        return {'header': backport.text(rNoWallet.header()),
         'body': backport.text(rNoWallet.body())}
