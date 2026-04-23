# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/customization_bill_data_packer.py
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from gui.customization.constants import CustomizationModes
from gui.customization.shared import getPurchaseMoneyState, getTotalPurchaseInfo, isTransactionValid
from gui.impl.wrappers.user_compound_price_model import BuyPriceModelBuilder
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.money import Currency
from helpers import dependency
from items.components.c11n_constants import SeasonType
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from tutorial.hints_manager import HINT_SHOWN_STATUS

@dependency.replace_none_kwargs(service=ICustomizationService, settingsCore=ISettingsCore)
def packBottomPanelBillData(billModel, isBinSubViewActive=False, service=None, settingsCore=None):
    ctx = service.getCtx()
    if ctx is None:
        return
    else:
        purchaseItems = ctx.mode.getPurchaseItems()
        purchaseItems = processBillDataPurchaseItems(ctx, purchaseItems)
        isEmpty = isVehicleEmpty()
        fillBaseBillData(billModel, isEmpty, isBinSubViewActive, ctx, purchaseItems)
        showAutoRentHint = False
        if ctx.modeId in CustomizationModes.ALL_STYLES and purchaseItems:
            item = purchaseItems[0].item
            if item.isRentable:
                showAutoRentHint = settingsCore.serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.C11N_AUTOPROLONGATION_HINT) != HINT_SHOWN_STATUS
        isLockedItem = ctx.mode.isOutfitsHasLockedItems()
        isModified = ctx.isOutfitsModified()
        billModel.setShowAutoRentHint(showAutoRentHint)
        billModel.setIsAutoRentSelected(ctx.mode.isAutoRentEnabled())
        billModel.setCancelButtonEnabled(isModified)
        billModel.setIsLockedItem(isLockedItem)
        billModel.setClearButtonEnabled(not isVehicleEmpty())
        return


def fillBaseBillData(billModel, isEmpty=None, isBinSubViewActive=False, ctx=None, purchaseItems=None):
    if ctx is None:
        return
    else:
        if purchaseItems is None:
            purchaseItems = ctx.mode.getPurchaseItems()
            purchaseItems = processBillDataPurchaseItems(ctx, purchaseItems)
        cartInfo = getTotalPurchaseInfo(purchaseItems)
        isRentable = False
        rentCount = 0
        if ctx.modeId in CustomizationModes.ALL_STYLES and purchaseItems:
            item = purchaseItems[0].item
            if item.isRentable:
                isRentable = True
                rentCount = item.rentCount
        hasLockedItems = ctx.mode.isOutfitsHasLockedItems()
        isModified = ctx.isOutfitsModified()
        if isEmpty is None:
            isEmpty = isVehicleEmpty()
        totalPrice = cartInfo.totalPrice
        moneyState = getPurchaseMoneyState(totalPrice.price)
        isEnoughMoney = isTransactionValid(moneyState, totalPrice.price)
        isGoldPrice = Currency.GOLD in totalPrice.price
        isApplyButton = isModified and totalPrice == ITEM_PRICE_EMPTY and isEmpty or isBinSubViewActive
        fromStorageCount = 0
        lockedCount = 0
        if not isEmpty:
            for pItem in purchaseItems:
                if pItem.item.isHiddenInUI():
                    continue
                if not pItem.item.isUnlockedByToken():
                    lockedCount += 1
                if pItem.isFromInventory:
                    fromStorageCount += 1

        billModel.setInStorageCount(fromStorageCount)
        billModel.setLockedCount(lockedCount)
        billModel.setBuyButtonEnabled((not isEmpty or isModified) and not hasLockedItems and isCreditPriceEnough(isBinSubViewActive))
        billModel.setIsVehicleCustomized(isModified)
        billModel.setRentCount(rentCount)
        billModel.setIsRentable(isRentable)
        billModel.setIsEnoughMoney(isEnoughMoney)
        billModel.setIsGoldPrice(isGoldPrice)
        billModel.setIsApplyButton(isApplyButton and not hasLockedItems)
        BuyPriceModelBuilder.fillPriceModelByItemPrice(billModel.buyPrice, totalPrice)
        return


@dependency.replace_none_kwargs(service=ICustomizationService)
def isCreditPriceEnough(isBinSubViewActive=False, service=None):
    ctx = service.getCtx()
    if ctx is None:
        return
    else:
        purchaseItems = ctx.mode.getPurchaseItems()
        purchaseItems = processBillDataPurchaseItems(ctx, purchaseItems)
        cartInfo = getTotalPurchaseInfo(purchaseItems)
        totalPrice = cartInfo.totalPrice
        moneyState = getPurchaseMoneyState(totalPrice.price)
        isEnoughMoney = isTransactionValid(moneyState, totalPrice.price)
        return isEnoughMoney if Currency.CREDITS in totalPrice.price and isBinSubViewActive else True


@dependency.replace_none_kwargs(service=ICustomizationService)
def isVehicleEmpty(service=None):
    ctx = service.getCtx()
    if ctx.mode.modeId in CustomizationModes.ALL_STYLES and ctx.mode.isOutfitsEmpty():
        return True
    for season in SeasonType.COMMON_SEASONS:
        outfit = ctx.mode.getModifiedOutfit(season)
        for intCD, component, _, _, _ in outfit.itemsFull():
            if component.isFilled():
                item = service.getItemByCD(intCD)
                if ctx.mode.modeId not in CustomizationModes.ALL_STYLES and item.isHiddenInUI():
                    continue
                return False

    return True


def processBillDataPurchaseItems(ctx, purchaseItems):
    if ctx.modeId not in CustomizationModes.ALL_STYLES:
        return purchaseItems
    result = purchaseItems[:1]
    for pItem in purchaseItems[1:]:
        if pItem.isEdited:
            result.append(pItem)

    return result
