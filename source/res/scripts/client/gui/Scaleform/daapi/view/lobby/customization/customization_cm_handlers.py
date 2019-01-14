# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_cm_handlers.py
from Event import Event
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.Scaleform.locale.MENU import MENU
from gui.shared.formatters import getItemPricesVO
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from helpers import dependency
from shared_utils import first
from skeletons.gui.shared import IItemsCache
from skeletons.gui.customization import ICustomizationService
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.Scaleform.daapi.view.lobby.customization.shared import SEASON_TYPE_TO_NAME, C11nMode

class CustomizationOptions(object):
    BUY = 'buy'
    BUY_MORE = 'buyMore'
    SELL = 'sell'
    REMOVE_FROM_TANK = 'removeFromTank'
    PROLONGATION_ON = 'autoprolongationOn'
    PROLONGATION_OFF = 'autoprolongationOff'


class CustomizationItemCMHandler(AbstractContextMenuHandler):
    itemsCache = dependency.descriptor(IItemsCache)
    service = dependency.descriptor(ICustomizationService)

    def __init__(self, cmProxy, ctx=None):
        self._intCD = 0
        super(CustomizationItemCMHandler, self).__init__(cmProxy, ctx, {CustomizationOptions.BUY: 'buyItem',
         CustomizationOptions.SELL: 'sellItem',
         CustomizationOptions.REMOVE_FROM_TANK: 'removeItemFromTank',
         CustomizationOptions.PROLONGATION_ON: 'changeAutoRent',
         CustomizationOptions.PROLONGATION_OFF: 'changeAutoRent'})
        self.onSelected = Event(self._eManager)
        self._item = self.itemsCache.items.getItemByCD(self._intCD)
        self.__ctx = self.service.getCtx()

    def changeAutoRent(self):
        self.__ctx.changeAutoRent()

    def fini(self):
        self.__ctx = None
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
        inventoryCount = self.__ctx.getItemInventoryCount(item)
        availableForSale = inventoryCount > 0 and item.getSellPrice() != ITEM_PRICE_EMPTY and not item.isRentable and not item.isHidden
        style = self.__ctx.modifiedStyle
        if self.__ctx.mode == C11nMode.STYLE:
            removeFromTankEnabled = style is not None and style.intCD == item.intCD
            removeFromTankText = CustomizationOptions.REMOVE_FROM_TANK
        else:
            outfit = self.__ctx.getModifiedOutfit(self.__ctx.currentSeason)
            removeFromTankEnabled = outfit.has(item)
            removeFromTankText = '/'.join((CustomizationOptions.REMOVE_FROM_TANK, SEASON_TYPE_TO_NAME.get(self.__ctx.currentSeason)))
        accountMoney = self.itemsCache.items.stats.money
        availableForPurchase = item.buyCount > 0 and not item.getBuyPrice() == ITEM_PRICE_EMPTY and item.getBuyPrice().price <= accountMoney
        showAlert = len(sellPriceVO[0]) > 1
        tooltipVO = None
        if showAlert:
            tooltipVO = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ITEM, str(item.intCD), False, item.sellPrices.getSum().price, item.sellPrices.getSum().defPrice)
            price = sellPriceVO[0]['price']
            sellPriceVO[0] = {}
            sellPriceVO[0]['price'] = price
        menuItems = []
        buyText = CustomizationOptions.BUY
        if self.__ctx.getItemInventoryCount(item) > 0 and item.isRentable:
            buyText = CustomizationOptions.BUY_MORE
        menuItems.append(self._makeItem(CustomizationOptions.BUY, MENU.cst_item_ctx_menu(buyText), {'data': {'price': first(buyPriceVO)} if availableForPurchase else None,
         'enabled': availableForPurchase}, None, 'CurrencyContextMenuItem'))
        menuItems.append(self._makeSeparator())
        if item.isRentable:
            if item.itemTypeID == GUI_ITEM_TYPE.STYLE:
                prolongationEnabled = self.__ctx.modifiedStyle == item
            else:
                outfit = self.__ctx.getModifiedOutfit(self.__ctx.currentSeason)
                appliedCount = outfit.itemsCounter[item.intCD]
                prolongationEnabled = appliedCount > 0
            optId = CustomizationOptions.PROLONGATION_ON
            if self.__ctx.autoRentEnabled():
                optId = CustomizationOptions.PROLONGATION_OFF
            menuItems.append(self._makeItem(optId, MENU.cst_item_ctx_menu(optId), {'enabled': prolongationEnabled,
             'iconType': optId}))
            menuItems.append(self._makeSeparator())
        menuItems.append(self._makeItem(CustomizationOptions.SELL, MENU.cst_item_ctx_menu(CustomizationOptions.SELL), {'data': {'price': first(sellPriceVO)} if availableForSale else None,
         'enabled': availableForSale,
         'showAlert': showAlert,
         'tooltipVO': tooltipVO}, None, 'CurrencyContextMenuItem'))
        menuItems.append(self._makeSeparator())
        menuItems.append(self._makeItem(CustomizationOptions.REMOVE_FROM_TANK, MENU.cst_item_ctx_menu(removeFromTankText), {'enabled': removeFromTankEnabled}))
        return menuItems

    def _initFlashValues(self, ctx):
        self._intCD = ctx.itemID
