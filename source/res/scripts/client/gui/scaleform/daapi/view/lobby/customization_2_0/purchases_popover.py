# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization_2_0/purchases_popover.py
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.daapi.view.meta.CustomizationPurchasesPopoverMeta import CustomizationPurchasesPopoverMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers.i18n import makeString as _ms
from gui.customization_2_0 import g_customizationController, shared

class PurchasesPopover(CustomizationPurchasesPopoverMeta):

    def __init__(self, ctx = None):
        super(PurchasesPopover, self).__init__()
        self.__items = g_customizationController.carousel.slots.cart.items

    def cleanAll(self):
        DialogsInterface.showDialog(I18nConfirmDialogMeta('customization/filter'), self.__confirmCloseWindow)

    def removePurchase(self, cType, slotIdx):
        g_customizationController.carousel.slots.dropAppliedItem(cType, slotIdx)

    def _dispose(self):
        g_customizationController.carousel.slots.cart.itemsUpdated -= self.__onCartItemsUpdated
        super(PurchasesPopover, self)._dispose()

    def _populate(self):
        super(PurchasesPopover, self)._populate()
        self.as_setPurchasesInitDataS({'closeButtonTooltip': makeTooltip(TOOLTIPS.CUSTOMIZATION_PURCHASESPOPOVERCLEARBTN_HEADER, TOOLTIPS.CUSTOMIZATION_PURCHASESPOPOVERCLEARBTN_BODY),
         'closeBtnLabel': VEHICLE_CUSTOMIZATION.CUSTOMIZATIONPURCHASESPOPOVER_CLOSEBTN})
        g_customizationController.carousel.slots.cart.itemsUpdated += self.__onCartItemsUpdated
        self.as_setPurchasesDataS(self.__getPurchaseItemVO(g_customizationController.carousel.slots.cart.items))

    def __onCartItemsUpdated(self, items):
        if not items:
            self.destroy()
        else:
            self.as_setPurchasesDataS(self.__getPurchaseItemVO(items))

    def __getPurchaseItemVO(self, items):
        purchaseItems = []
        for item in items:
            if item['currencyIcon'] == RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_2:
                price = text_styles.credits(item['price'])
            else:
                price = text_styles.gold(item['price'])
            data = {'name': text_styles.main(item['name']),
             'idx': item['idx'],
             'type': item['type'],
             'isTitle': False,
             'currencyIcon': item['currencyIcon'],
             'itemID': item['itemID'],
             'price': price,
             'removeItemIcon': RES_ICONS.MAPS_ICONS_LIBRARY_CROSS}
            if shared.isSale(item['type'], item['duration']):
                isGold = item['currencyIcon'] != RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_2
                data['salePrice'] = shared.getSalePriceString(isGold, item['price'])
            purchaseItems.append(data)

        return {'title': text_styles.highTitle(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATIONPURCHASESPOPOVER_TITLE, count=len(purchaseItems))),
         'popoverRenderers': purchaseItems}

    def __confirmCloseWindow(self, proceed):
        if proceed:
            for item in g_customizationController.carousel.slots.cart.items:
                self.removePurchase(item['type'], item['idx'])
