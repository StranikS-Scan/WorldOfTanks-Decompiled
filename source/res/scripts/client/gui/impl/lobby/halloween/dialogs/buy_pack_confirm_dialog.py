# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/dialogs/buy_pack_confirm_dialog.py
from gui.impl.dialogs.sub_views.footer.single_price_footer import SinglePriceFooter
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencySize
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Money
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.impl.dialogs.dialog_template import DialogTemplateView
from skeletons.gui.game_event_controller import IGameEventController
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType

class BuyPackConfirmDialog(DialogTemplateView):
    _itemsCache = dependency.descriptor(IItemsCache)
    _gameEventController = dependency.descriptor(IGameEventController)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, bundle, layoutID=None, uniqueID=None, *args, **kwargs):
        super(BuyPackConfirmDialog, self).__init__(layoutID, uniqueID, *args, **kwargs)
        self.__bundle = bundle

    def _onLoading(self, *args, **kwargs):
        self.setSubView(Placeholder.TOP_RIGHT, MoneyBalance())
        self.setSubView(Placeholder.TITLE, SimpleTextContent(backport.text(R.strings.event.shop21.confirm_buy.dyn(self.__bundle.id)())))
        money = Money(gold=self.__bundle.price.amount)
        price = ItemPrice(money, money)
        self.setSubView(Placeholder.FOOTER, SinglePriceFooter(R.strings.event.shop21.confirmation.price(), price, CurrencySize.BIG))
        self.addButton(ConfirmButton(R.strings.event.shop21.confirm_buy.labelBuy(), buttonType=ButtonType.MAIN))
        self.addButton(CancelButton())
        self._gameEventController.onIngameEventsUpdated += self.__onEventUpdate
        super(BuyPackConfirmDialog, self)._onLoading(*args, **kwargs)

    def _finalize(self):
        self._gameEventController.onIngameEventsUpdated -= self.__onEventUpdate
        super(BuyPackConfirmDialog, self)._finalize()

    def __onEventUpdate(self):
        if not self._eventsCache.isEventEnabled():
            self._setResult(DialogButtons.CANCEL)
            self.destroyWindow()
