# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/shop_views/booster_buy_dialog_view.py
from gui.impl import backport
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import ConfirmButton, CancelButton
from gui.impl.dialogs.dialog_template_tooltip import DialogTemplateTooltip
from gui.impl.dialogs.sub_views.footer.single_price_footer import SinglePriceFooter
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencySize
from gui.shared.gui_items.gui_item_economics import ItemPrice
from historical_battles.gui.impl.dialogs.sub_views.content.order_with_bonuses import OrderWithBonuses
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.bundle_view_model import BundleLayout
from historical_battles.gui.impl.lobby.tooltips.order_tooltip import OrderTooltip
rIcons = R.images.historical_battles.gui.maps.icons
rBoosterBuyDialog = R.strings.hb_shop.booster_buy_dialog

class BoosterBuyDialogView(DialogTemplateView):
    LAYOUT_ID = R.views.lobby.historical_battles.dialogs.BoosterBuyDialogView()

    def __init__(self, data, layoutID=None, uniqueID=None, *args, **kwargs):
        super(BoosterBuyDialogView, self).__init__(layoutID, uniqueID, *args, **kwargs)
        self._data = data

    def _onLoading(self, *args, **kwargs):
        layout = self._data['layout']
        self.setBackgroundImagePath(R.images.historical_battles.gui.maps.icons.backgrounds.buyBundle())
        self.setSubView(Placeholder.TOP_RIGHT, MoneyBalance())
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(self._getTitle()))
        if layout == BundleLayout.NEWBIE:
            self.setSubView(Placeholder.ICON, IconSet(rIcons.order.c_220x220.x10(), backgroundResIDList=[rIcons.bundlesWindow.lightRed_huge()], isBottomPushingDown=False, tooltip=DialogTemplateTooltip(self._orderTooltipFactory)))
        self.setSubView(Placeholder.FOOTER, SinglePriceFooter(rBoosterBuyDialog.cost, ItemPrice(self._data['price'], self._data['oldPrice'] or self._data['price']), CurrencySize.BIG))
        if layout != BundleLayout.NEWBIE:
            self.setSubView(Placeholder.CONTENT, OrderWithBonuses(self._data['order'], self._data['bonuses']))
        buttonType = ButtonType.PRIMARY if layout == BundleLayout.NEWBIE else ButtonType.MAIN
        self.addButton(ConfirmButton(R.strings.hb_shop.common.button.buy(), buttonType=buttonType))
        self.addButton(CancelButton())
        super(BoosterBuyDialogView, self)._onLoading(*args, **kwargs)

    def _getTitle(self):
        layout = self._data['layout']
        rTitle = rBoosterBuyDialog.title
        if layout == BundleLayout.NEWBIE:
            count = int(self._data['count'])
            return backport.text(rTitle.newbie(), number=count)
        return backport.text(rTitle.specialist()) if layout == BundleLayout.SPECIALIST else backport.text(rTitle.master())

    def _orderTooltipFactory(self):
        return OrderTooltip(self._data['order'].type.value, True, False)

    def _getAdditionalData(self):
        return {'count': self._data.get('count', 1)}
