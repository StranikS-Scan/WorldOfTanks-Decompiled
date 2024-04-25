# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/shop_views/shop_buy_dialog_view.py
import typing
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import ConfirmButton, CancelButton
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType
from historical_battles.gui.impl.dialogs.sub_views.content.hb_multi_price import HBMultiPriceContent
from historical_battles.gui.impl.dialogs.sub_views.footer.hb_multi_price import HBMultiPriceFooter
from historical_battles.gui.impl.dialogs.sub_views.footer.hb_multi_price_quantity import HBMultiPriceQuantityFooter
from historical_battles.gui.impl.dialogs.sub_views.icon.icon_with_blinking import IconWithBlinking
from historical_battles.gui.impl.dialogs.sub_views.top_right.hb_money_balance import HBMoneyBalance
from historical_battles.gui.impl.lobby.shop_views.utils import hasEnoughMoney, getSortedPriceList
from historical_battles_common.helpers_common import Discount
if typing.TYPE_CHECKING:
    from typing import Iterable
    from historical_battles.gui.impl.dialogs.sub_views.common.hb_multi_price import HBMultiPrice
    from historical_battles_common.helpers_common import EventShopBundlePrice

class ShopBuyDialogView(DialogTemplateView):

    def __init__(self, data, layoutID=None, uniqueID=None, *args, **kwargs):
        super(ShopBuyDialogView, self).__init__(layoutID, uniqueID, *args, **kwargs)
        self._data = data
        bundle = self._data['bundle']
        self._prices = getSortedPriceList(bundle.prices)
        self._discounts = Discount.getDiscountPercent(bundle.price, bundle.oldPrice)

    @property
    def pickCount(self):
        return self._data.get('pickCount', False)

    @property
    def prices(self):
        return self._prices

    @property
    def discounts(self):
        return self._discounts

    @property
    def footer(self):
        return self.getSubView(Placeholder.FOOTER)

    def _onLoading(self, *args, **kwargs):
        self.setBackgroundImagePath(R.images.historical_battles.gui.maps.icons.backgrounds.shopConfirmBackground())
        self.setSubView(Placeholder.TOP_RIGHT, HBMoneyBalance(isGoldVisible=True, isCreditsVisible=True))
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(self._data.get('titleText')))
        isPrize = self._data.get('isPrize', False)
        if isPrize:
            self.setSubView(Placeholder.ICON, IconWithBlinking(iconResID=self._data.get('icon'), isBottomPushingDown=True, overlayResIDList=self._data.get('overlays'), blinkingResIDList=self._data.get('blinkingIcons')))
        else:
            self.setSubView(Placeholder.ICON, IconSet(self._data.get('icon'), isBottomPushingDown=False, overlayResIDList=self._data.get('overlays'), backgroundResIDList=self._data.get('backgrounds')))
        if self.pickCount:
            self.setSubView(Placeholder.CONTENT, HBMultiPriceContent(self.prices))
        footerClass = HBMultiPriceQuantityFooter if self.pickCount else HBMultiPriceFooter
        self.setSubView(Placeholder.FOOTER, footerClass(prices=self.prices, discounts=self.discounts))
        self.addButton(ConfirmButton(R.strings.hb_shop.common.button.get(), buttonType=ButtonType.PRIMARY, isDisabled=not hasEnoughMoney(self.prices)))
        self.addButton(CancelButton())
        super(ShopBuyDialogView, self)._onLoading(*args, **kwargs)

    def _getAdditionalData(self):
        return {'count': self.footer.count}
