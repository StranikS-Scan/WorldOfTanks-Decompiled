# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/dialogs/customization_confirm_dialog.py
from constants import EVENT
from gui.impl.gen import R
from gui.impl import backport
from helpers import dependency
from gui.shared.money import Currency
from gui.shop import showBuyGoldForBundle
from skeletons.gui.shared import IItemsCache
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.dialogs.dialog_template import DialogTemplateView
from skeletons.gui.game_event_controller import IGameEventController
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.dialogs.sub_views.footer.event_single_price_footer import EventSinglePrice
from gui.impl.dialogs.sub_views.top_right.event_money_balance import EventMoneyBalance
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType

class CustomizationConfirmDialog(DialogTemplateView):
    _itemsCache = dependency.descriptor(IItemsCache)
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, shopItem, count, layoutID=None, uniqueID=None, *args, **kwargs):
        super(CustomizationConfirmDialog, self).__init__(layoutID, uniqueID, *args, **kwargs)
        self.__shopItem = shopItem
        self.__count = count
        self.__shop = self._gameEventController.getShop()
        self.__bundle = self.__shop.getBundle(shopItem.bundleID)
        self.__totalPrice = self.__bundle.price.amount * self.__count

    def _onLoading(self, *args, **kwargs):
        c11Item = self.__shopItem.c11Item()
        title = ''
        if c11Item.itemTypeID == GUI_ITEM_TYPE.STYLE:
            title = backport.text(R.strings.event.tradeStyles.confirmBuy.style(), name=c11Item.userName)
            self.setSubView(Placeholder.TOP_RIGHT, MoneyBalance())
        else:
            title = backport.text(R.strings.event.tradeStyles.confirmBuy.decal(), name=c11Item.userName, count=self.__count)
            self.setSubView(Placeholder.TOP_RIGHT, EventMoneyBalance())
        self.setSubView(Placeholder.TITLE, SimpleTextContent(title))
        self.setSubView(Placeholder.FOOTER, EventSinglePrice(backport.text(R.strings.event.tradeStyles.confirmationCost()), self.__totalPrice, self.__bundle.price.currencyType))
        self.addButton(ConfirmButton(R.strings.event.tradeStyles.buy(), buttonType=ButtonType.MAIN))
        self.addButton(CancelButton())
        super(CustomizationConfirmDialog, self)._onLoading(*args, **kwargs)

    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            if self.__bundle.price.currencyType == EVENT.SHOP.REAL_CURRENCY:
                playerGold = self._itemsCache.items.stats.money.get(Currency.GOLD, 0)
                if playerGold < self.__totalPrice:
                    showBuyGoldForBundle(self.__bundle.price.amount, {})
                    result = DialogButtons.CANCEL
        super(CustomizationConfirmDialog, self)._setResult(result)
