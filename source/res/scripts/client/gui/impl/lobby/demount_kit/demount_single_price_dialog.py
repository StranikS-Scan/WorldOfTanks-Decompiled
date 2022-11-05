# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/demount_kit/demount_single_price_dialog.py
import typing
from gui.goodies.demount_kit import getDemountKitForOptDevice
from gui.goodies.goodie_items import DemountKit
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import CancelButton, CheckMoneyButton
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.dialogs.sub_views.footer.single_price_footer import SinglePriceFooter
from gui.impl.dialogs.sub_views.icon.item_icon import ItemIcon
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencySize, CurrencyType
from gui.impl.gen.view_models.views.dialogs.template_settings.default_dialog_template_settings import DisplayFlags
from gui.impl.lobby.demount_kit.demount_kit_utils import getDemountDialogTitle
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.money import Currency
from gui.shop import showBuyGoldForEquipment
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.gui_item_economics import ItemPrice

class DemountOptionalDeviceSinglePriceDialog(DialogTemplateView):
    __slots__ = ('__forFitting', '__item', '__dkAppeared')
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, itemCD, forFitting=False, layoutID=None, uniqueID=None):
        super(DemountOptionalDeviceSinglePriceDialog, self).__init__(layoutID, uniqueID)
        self.__forFitting = forFitting
        self.__item = self._itemsCache.items.getItemByCD(itemCD)
        self.__dkAppeared = False

    @property
    def itemPrice(self):
        return self.__item.getRemovalPrice(self._itemsCache.items)

    def _onLoading(self, *args, **kwargs):
        rDK = R.strings.demount_kit
        self.setDisplayFlags(DisplayFlags.RESPONSIVEHEADER.value)
        currenciesList = [CurrencyType.EQUIPCOIN] if self.__item.isModernized else None
        self.setSubView(Placeholder.TOP_RIGHT, MoneyBalance(currenciesList=currenciesList))
        self.setSubView(Placeholder.ICON, ItemIcon(self.__item.intCD))
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(getDemountDialogTitle(self.__item, self.__forFitting)))
        self.setSubView(Placeholder.CONTENT, SimpleTextContent(rDK.equipmentDemount.confirmation.description))
        self.setSubView(Placeholder.FOOTER, SinglePriceFooter(rDK.equipmentDemountPrice, self.itemPrice, CurrencySize.BIG))
        self.addButton(CheckMoneyButton(self.itemPrice.price, rDK.demountConfirmation.submit()))
        self.addButton(CancelButton())
        super(DemountOptionalDeviceSinglePriceDialog, self)._onLoading(*args, **kwargs)
        self._itemsCache.onSyncCompleted += self._inventorySyncHandler
        return

    def _finalize(self):
        self._itemsCache.onSyncCompleted -= self._inventorySyncHandler
        super(DemountOptionalDeviceSinglePriceDialog, self)._finalize()

    def _inventorySyncHandler(self, *_):
        dk, _ = getDemountKitForOptDevice(self.__item)
        if dk is not None and dk.enabled:
            self.__dkAppeared = True
            self._closeClickHandler()
            return
        else:
            singlePriceFooter = self.getSubView(Placeholder.FOOTER)
            singlePriceFooter.updatePrice(self.itemPrice)
            checkMoneyButton = self.getButton(DialogButtons.SUBMIT)
            checkMoneyButton.money = self.itemPrice.price
            return

    def _getAdditionalData(self):
        return {'openDemountSelectorWindow': self.__dkAppeared}

    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            shortage = self._itemsCache.items.stats.money.getShortage(self.itemPrice.price)
            if shortage and shortage.getCurrency() == Currency.GOLD:
                showBuyGoldForEquipment(self.itemPrice.price.gold)
                result = DialogButtons.CANCEL
        super(DemountOptionalDeviceSinglePriceDialog, self)._setResult(result)
