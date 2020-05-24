# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_cm_handlers.py
import logging
from adisp import process as adisp_process
from Event import Event
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs.confirm_customization_item_dialog_meta import ConfirmC11nBuyMeta, ConfirmC11nSellMeta
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.Scaleform.locale.MENU import MENU
from gui.customization.constants import CustomizationModes, CustomizationModeSource
from gui.customization.shared import SEASON_TYPE_TO_NAME, EDITABLE_STYLE_IRREMOVABLE_TYPES
from gui.shared.formatters import getItemPricesVO
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from helpers import dependency
from shared_utils import first
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from CurrentVehicle import g_currentVehicle
_logger = logging.getLogger(__name__)

class CustomizationOptions(object):
    BUY = 'buy'
    BUY_MORE = 'buyMore'
    SELL = 'sell'
    REMOVE_FROM_TANK = 'removeFromTank'
    PROLONGATION_ON = 'autoprolongationOn'
    PROLONGATION_OFF = 'autoprolongationOff'
    STYLE_INFO = 'styleInfo'
    EDIT_STYLE = 'editStyle'
    BASE_STYLE = 'baseStyle'


class CustomizationItemCMHandler(AbstractContextMenuHandler):
    itemsCache = dependency.descriptor(IItemsCache)
    service = dependency.descriptor(ICustomizationService)

    def __init__(self, cmProxy, ctx=None):
        self._intCD = 0
        super(CustomizationItemCMHandler, self).__init__(cmProxy, ctx, {CustomizationOptions.BUY: 'buyItem',
         CustomizationOptions.SELL: 'sellItem',
         CustomizationOptions.REMOVE_FROM_TANK: 'removeItemFromTank',
         CustomizationOptions.PROLONGATION_ON: 'changeAutoRent',
         CustomizationOptions.PROLONGATION_OFF: 'changeAutoRent',
         CustomizationOptions.STYLE_INFO: 'showStyleInfo',
         CustomizationOptions.EDIT_STYLE: 'enterEditMode',
         CustomizationOptions.BASE_STYLE: 'clearStyle'})
        self.onSelected = Event(self._eManager)
        self._item = self.itemsCache.items.getItemByCD(self._intCD)
        self.__ctx = self.service.getCtx()

    def changeAutoRent(self):
        self.__ctx.mode.changeAutoRent()

    def fini(self):
        self.__ctx = None
        self.onSelected.clear()
        self.onSelected = None
        super(CustomizationItemCMHandler, self).fini()
        return

    @adisp_process
    def buyItem(self):
        yield DialogsInterface.showDialog(ConfirmC11nBuyMeta(self._intCD, vehicle=g_currentVehicle.item))

    @adisp_process
    def sellItem(self):
        inventoryCount = self.__ctx.mode.getItemInventoryCount(self._item, excludeBase=True)
        if self._item.isProgressive:
            installed = self._item.installedCount(g_currentVehicle.item.intCD)
            fullInventoryCount = self._item.fullInventoryCount(g_currentVehicle.item.intCD)
            availToSell = installed + fullInventoryCount - self._item.descriptor.progression.autoGrantCount
            availToSell = max(0, availToSell)
            inventoryCount = min(inventoryCount, availToSell)
        yield DialogsInterface.showDialog(ConfirmC11nSellMeta(self._intCD, inventoryCount, self.__ctx.mode.sellItem, vehicle=g_currentVehicle.item))

    def removeItemFromTank(self):
        if self.__ctx.modeId == CustomizationModes.STYLED:
            self.__ctx.mode.removeStyle(self._intCD)
        else:
            self.__ctx.mode.removeItems(True, self._intCD)

    def showStyleInfo(self):
        self.__ctx.events.onShowStyleInfo(self._item)

    def enterEditMode(self):
        self.__ctx.editStyle(self._intCD, source=CustomizationModeSource.CONTEXT_MENU)

    def clearStyle(self):
        if self.__ctx.modeId in (CustomizationModes.STYLED, CustomizationModes.EDITABLE_STYLE):
            self.__ctx.mode.clearStyle()
        else:
            _logger.error('Failed to install EditableStyle base outfit. Style/EditableStyle mode must be selected.')

    def _generateOptions(self, ctx=None):
        item = self.itemsCache.items.getItemByCD(self._intCD)
        menuItems = []
        if item.itemTypeID == GUI_ITEM_TYPE.STYLE:
            menuItems += self.__separateItem(self.__getStyleInfoBtn(item))
            if item.isEditable:
                menuItems += self.__separateItem(self.__getEditStyleBtn(item))
                menuItems += self.__separateItem(self.__getClearStyleBtn(item))
        menuItems += self.__separateItem(self.__getBuyBtn(item))
        if item.isRentable:
            menuItems += self.__separateItem(self.__getRentBtn(item))
        menuItems += self.__separateItem(self.__getSellBtn(item))
        menuItems.append(self.__getRemoveBtn(item))
        return menuItems

    def _initFlashValues(self, ctx):
        self._intCD = ctx.itemID

    def __separateItem(self, item):
        return [item, self._makeSeparator()]

    def __getStyleInfoBtn(self, item):
        enabled = bool(item.longDescriptionSpecial)
        btn = self._makeItem(optId=CustomizationOptions.STYLE_INFO, optLabel=MENU.cst_item_ctx_menu(CustomizationOptions.STYLE_INFO), optInitData={'enabled': enabled})
        return btn

    def __getEditStyleBtn(self, item):
        enabled = item.canBeEditedForVehicle(g_currentVehicle.item.intCD)
        btn = self._makeItem(optId=CustomizationOptions.EDIT_STYLE, optLabel=MENU.cst_item_ctx_menu(CustomizationOptions.EDIT_STYLE), optInitData={'enabled': enabled})
        return btn

    def __getClearStyleBtn(self, item):
        from gui.Scaleform.daapi.view.lobby.customization.shared import isStyleEditedForCurrentVehicle
        style = self.__ctx.mode.modifiedStyle
        isStyleInstalled = style is not None and style.intCD == item.intCD
        if isStyleInstalled and style.isEditable:
            modifiedOutfits = self.__ctx.mode.getModifiedOutfits()
            enabled = isStyleEditedForCurrentVehicle(modifiedOutfits, style)
        else:
            enabled = False
        btn = self._makeItem(optId=CustomizationOptions.BASE_STYLE, optLabel=MENU.cst_item_ctx_menu(CustomizationOptions.BASE_STYLE), optInitData={'enabled': enabled})
        return btn

    def __getBuyBtn(self, item):
        isInInventory = self.__ctx.mode.getItemInventoryCount(item) > 0
        textKey = CustomizationOptions.BUY_MORE if item.isRentable and isInInventory else CustomizationOptions.BUY
        buyPrice = item.getBuyPrice()
        buyPriceVO = getItemPricesVO(buyPrice)
        availableForPurchase = item.buyCount > 0
        if availableForPurchase and not buyPrice == ITEM_PRICE_EMPTY:
            accountMoney = self.itemsCache.items.stats.money
            availableForPurchase &= buyPrice.price <= accountMoney
        if availableForPurchase and item.isProgressionAutoBound:
            availableForPurchase &= item.availableForPurchaseProgressive(g_currentVehicle.item) > 0
        btn = self._makeItem(optId=CustomizationOptions.BUY, optLabel=MENU.cst_item_ctx_menu(textKey), optInitData={'data': {'price': first(buyPriceVO)} if availableForPurchase else None,
         'enabled': availableForPurchase}, optSubMenu=None, linkage='CurrencyContextMenuItem')
        return btn

    def __getRentBtn(self, item):
        style = self.__ctx.mode.modifiedStyle
        enabled = style is not None and style.intCD == item.intCD
        isAutoRentEnabled = self.__ctx.mode.isAutoRentEnabled()
        optId = CustomizationOptions.PROLONGATION_OFF if isAutoRentEnabled else CustomizationOptions.PROLONGATION_ON
        btn = self._makeItem(optId=optId, optLabel=MENU.cst_item_ctx_menu(optId), optInitData={'enabled': enabled,
         'iconType': optId})
        return btn

    def __getSellBtn(self, item):
        sellPrice = item.getSellPrice()
        sellPriceVO = getItemPricesVO(sellPrice)
        showAlert = len(sellPriceVO[0]) > 1
        if showAlert:
            tooltipVO = packActionTooltipData(actionType=ACTION_TOOLTIPS_TYPE.ITEM, key=str(item.intCD), isBuying=False, price=item.sellPrices.getSum().price, oldPrice=item.sellPrices.getSum().defPrice)
            price = sellPriceVO[0]['price']
            sellPriceVO[0] = {'price': price}
        else:
            tooltipVO = None
        inventoryCount = self.__ctx.mode.getItemInventoryCount(item, excludeBase=True)
        if item.isProgressive:
            installedCount = item.installedCount(g_currentVehicle.item.intCD)
            fullCount = installedCount + inventoryCount
            availableToSellCount = fullCount - item.descriptor.progression.autoGrantCount
            availableToSellCount = max(0, availableToSellCount)
            availableToSellCount = min(inventoryCount, availableToSellCount)
        else:
            availableToSellCount = inventoryCount
        availableForSale = availableToSellCount > 0 and sellPrice != ITEM_PRICE_EMPTY and not item.isRentable and not item.isHidden
        btn = self._makeItem(optId=CustomizationOptions.SELL, optLabel=MENU.cst_item_ctx_menu(CustomizationOptions.SELL), optInitData={'data': {'price': first(sellPriceVO)} if availableForSale else None,
         'enabled': availableForSale,
         'showAlert': showAlert,
         'tooltipVO': tooltipVO}, optSubMenu=None, linkage='CurrencyContextMenuItem')
        return btn

    def __getRemoveBtn(self, item):
        itemType = item.itemTypeID
        if itemType == GUI_ITEM_TYPE.STYLE:
            style = self.__ctx.mode.modifiedStyle
            isInstalled = style is not None and style.intCD == item.intCD
            textKey = CustomizationOptions.REMOVE_FROM_TANK
        else:
            outfit = self.__ctx.mode.getModifiedOutfit()
            isInstalled = outfit.has(item)
            seasonName = SEASON_TYPE_TO_NAME.get(self.__ctx.season)
            textKey = '/'.join((CustomizationOptions.REMOVE_FROM_TANK, seasonName))
        if self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE and itemType in EDITABLE_STYLE_IRREMOVABLE_TYPES:
            baseOutfit = self.__ctx.mode.baseOutfits[self.__ctx.season]
            isBase = baseOutfit.has(item)
            enabled = isInstalled and not isBase
        else:
            enabled = isInstalled
        btn = self._makeItem(optId=CustomizationOptions.REMOVE_FROM_TANK, optLabel=MENU.cst_item_ctx_menu(textKey), optInitData={'enabled': enabled})
        return btn
