# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_cm_handlers.py
from Event import Event
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.Scaleform.locale.MENU import MENU
from gui.shared.formatters import getItemPricesVO
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from helpers import dependency
from items.components.c11n_constants import SeasonType
from shared_utils import first
from skeletons.gui.shared import IItemsCache
from skeletons.gui.customization import ICustomizationService
from gui.Scaleform.framework import ViewTypes

class CustomizationOptions(object):
    BUY = 'buy'
    SELL = 'sell'
    REMOVE_FROM_TANK = 'removeFromTank'


class CustomizationItemCMHandler(AbstractContextMenuHandler):
    itemsCache = dependency.descriptor(IItemsCache)
    service = dependency.descriptor(ICustomizationService)

    def __init__(self, cmProxy, ctx=None):
        self._intCD = 0
        super(CustomizationItemCMHandler, self).__init__(cmProxy, ctx, {CustomizationOptions.BUY: 'buyItem',
         CustomizationOptions.SELL: 'sellItem',
         CustomizationOptions.REMOVE_FROM_TANK: 'removeItemFromTank'})
        self.onSelected = Event(self._eManager)
        self._item = self.itemsCache.items.getItemByCD(self._intCD)
        self._c11nView = self.app.containerManager.getContainer(ViewTypes.LOBBY_SUB).getView()

    def fini(self):
        self.onSelected.clear()
        self.onSelected = None
        super(CustomizationItemCMHandler, self).fini()
        return

    def buyItem(self):
        self.onSelected(CustomizationOptions.BUY, self._intCD)

    def sellItem(self):
        self.onSelected(CustomizationOptions.SELL, self._intCD)

    def removeItemFromTank(self):
        self.onSelected(CustomizationOptions.REMOVE_FROM_TANK, self._intCD)

    def _generateOptions(self, ctx=None):
        item = self.itemsCache.items.getItemByCD(self._intCD)
        buyPriceVO = getItemPricesVO(item.getBuyPrice())
        sellPriceVO = getItemPricesVO(item.getSellPrice())
        inventoryCount = self._c11nView.getItemInventoryCount(item)
        availableForSale = inventoryCount > 0 and item.getSellPrice() != ITEM_PRICE_EMPTY and not item.isRentable and not item.isHidden
        style = self._c11nView.getModifiedStyle()
        removeFromTankEnabled = style.intCD == item.intCD if style is not None else False
        for outfit in (self._c11nView.getModifiedOutfit(season) for season in SeasonType.COMMON_SEASONS):
            if outfit.has(item):
                removeFromTankEnabled = True
                break

        availableForPurchase = not item.isHidden and not item.getBuyPrice() == ITEM_PRICE_EMPTY
        return [self._makeItem(CustomizationOptions.BUY, MENU.cst_item_ctx_menu(CustomizationOptions.BUY), {'data': {'price': first(buyPriceVO)} if availableForPurchase else None,
          'enabled': availableForPurchase}, None, 'CurrencyContextMenuItem'),
         self._makeSeparator(),
         self._makeItem(CustomizationOptions.SELL, MENU.cst_item_ctx_menu(CustomizationOptions.SELL), {'data': {'price': first(sellPriceVO)} if availableForSale else None,
          'enabled': availableForSale}, None, 'CurrencyContextMenuItem'),
         self._makeSeparator(),
         self._makeItem(CustomizationOptions.REMOVE_FROM_TANK, MENU.cst_item_ctx_menu(CustomizationOptions.REMOVE_FROM_TANK), {'enabled': removeFromTankEnabled})]

    def _initFlashValues(self, ctx):
        self._intCD = ctx.itemID
