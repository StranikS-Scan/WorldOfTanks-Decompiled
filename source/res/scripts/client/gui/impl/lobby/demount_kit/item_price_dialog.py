# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/demount_kit/item_price_dialog.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.lobby.demount_kit.item_base_dialog import BaseItemDialog
from gui.shared.economics import getActionPrc
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Currency
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shop import showBuyGoldForEquipment

class ItemPriceDialog(BaseItemDialog):
    __slots__ = ()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            specialArgs = None
            if tooltipId == TOOLTIPS_CONSTANTS.ACTION_PRICE:
                specialArgs = (ACTION_TOOLTIPS_TYPE.ITEM,
                 self._item.intCD,
                 self.__convertMoneyToTuple(self._price.price),
                 self.__convertMoneyToTuple(self._price.defPrice),
                 bool(self.viewModel.getDiscount()))
            elif tooltipId == TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY:
                specialArgs = (self._shortage, self._currency)
            if specialArgs is not None:
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=specialArgs)
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(ItemPriceDialog, self).createToolTip(event)

    def isPriceInGold(self):
        return self._currency == Currency.GOLD

    @property
    def _price(self):
        raise NotImplementedError

    @property
    def _currency(self):
        return self._price.getCurrency()

    @property
    def _shortage(self):
        shortage = self._stats.money.getShortage(self._price.price)
        return shortage.get(self._currency)

    def _setItemPrice(self, model):
        if not self._price:
            return
        model.setCurrencyType(self._currency)
        model.setItemPrice(self._price.price.get(self._currency))
        discount = getActionPrc(self._price.price, self._price.defPrice)
        model.setDiscount(discount)
        model.setIsAcceptDisabled(not self.isPriceInGold() and bool(self._shortage))

    def _setBaseParams(self, model):
        super(ItemPriceDialog, self)._setBaseParams(model)
        self._setItemPrice(model)

    def _onInventoryResync(self, *args, **kwargs):
        super(ItemPriceDialog, self)._onInventoryResync(args, kwargs)
        with self.viewModel.transaction() as model:
            self._setItemPrice(model)

    def _onAcceptClicked(self):
        if self.isPriceInGold() and self._shortage:
            showBuyGoldForEquipment(self._price.price.get(self._currency))
        else:
            super(ItemPriceDialog, self)._onAcceptClicked()

    @staticmethod
    def __convertMoneyToTuple(price):
        return (price.credits, price.gold, price.crystal)
