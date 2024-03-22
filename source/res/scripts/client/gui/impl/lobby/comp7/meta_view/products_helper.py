# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/meta_view/products_helper.py
import typing
from account_helpers.AccountSettings import AccountSettings, COMP7_UI_SECTION, COMP7_SHOP_SEEN_PRODUCTS
from debug_utils import LOG_WARNING
from gui.Scaleform.daapi.view.lobby.vehicle_preview.items_kit_helper import getCDFromId
from gui.impl.gen.view_models.views.lobby.comp7.base_product_model import BaseProductModel, ProductTypes, ProductState
from gui.impl.gen.view_models.views.lobby.comp7.reward_product_model import RewardProductModel
from gui.impl.gen.view_models.views.lobby.comp7.style3d_product_model import Style3dProductModel
from gui.impl.gen.view_models.views.lobby.comp7.vehicle_product_model import VehicleProductModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.comp7.comp7_bonus_packer import getComp7BonusPacker
from gui.impl.lobby.comp7.comp7_c11n_helpers import getStylePreviewVehicle
from gui.server_events.bonuses import ItemsBonus
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.tooltips import TOOLTIP_TYPE
from helpers import dependency
from items.vehicles import g_cache
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
_PRODUCT_TYPE_TO_MODEL = {ProductTypes.VEHICLE: VehicleProductModel,
 ProductTypes.STYLE3D: Style3dProductModel,
 ProductTypes.REWARD: RewardProductModel}
_PRODUCT_TYPE_ORDER = [ProductTypes.VEHICLE, ProductTypes.STYLE3D, ProductTypes.REWARD]
if typing.TYPE_CHECKING:
    from gui.game_control.comp7_shop_controller import ShopPageProductInfo

def packProduct(productData):
    productCD, productType = _getProductTypeData(productData)
    if not productCD:
        LOG_WARNING('Unknown product with data: {}'.format(productData))
        return None
    else:
        productModel = _PRODUCT_TYPE_TO_MODEL[productType]()
        setProductModelData(productData, productModel)
        return productModel


def setProductModelData(productData, productModel):
    productCD, productType = _getProductTypeData(productData)
    if not productCD:
        LOG_WARNING('Unknown product with data: {}'.format(productData))
        return None
    else:
        _setGenericData(productModel, productCD, productType, productData)
        _setSpecificData(productModel, productCD, productType)
        return None


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getItemType(intCD, itemsCache=None):
    try:
        item = itemsCache.items.getItemByCD(intCD)
        if item:
            return item.itemTypeID
        return None
    except KeyError:
        return None

    return None


@dependency.replace_none_kwargs(c11nService=ICustomizationService)
def getVehicleCDAndStyle(cd, c11nService=None):
    style = c11nService.getItemByCD(cd)
    return (getStylePreviewVehicle(style), style)


def getSeenProducts():
    settings = AccountSettings.getUIFlag(COMP7_UI_SECTION)
    return settings.get(COMP7_SHOP_SEEN_PRODUCTS, [])


def addSeenProduct(product):
    settings = AccountSettings.getUIFlag(COMP7_UI_SECTION)
    settings.setdefault(COMP7_SHOP_SEEN_PRODUCTS, []).append(product)
    AccountSettings.setUIFlag(COMP7_UI_SECTION, settings)


def hasUnseenProduct(products):
    seenProducts = getSeenProducts()
    for product in products.itervalues():
        cd, _ = _getProductTypeData(product)
        if cd not in seenProducts:
            return True

    return False


def _getProductTypeData(product):
    for cd, entitlementType in product.entitlements.iteritems():
        itemType = getItemType(getCDFromId(entitlementType, cd))
        if itemType == GUI_ITEM_TYPE.VEHICLE:
            return (cd, ProductTypes.VEHICLE)
        if itemType == GUI_ITEM_TYPE.OPTIONALDEVICE:
            return (cd, ProductTypes.REWARD)
        style = g_cache.customization20().styles.get(cd)
        if style:
            return (style.compactDescr, ProductTypes.STYLE3D)
        return (0, ProductTypes.BASE)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _setGenericData(model, productCD, productType, product, itemsCache=None):
    stats = itemsCache.items.stats
    playerMoney = stats.money.get(product.currencyName)
    productPrice = product.discountPrice if product.discountPrice else product.originalPrice
    isEnoughMoney = playerMoney >= productPrice
    purchaseAllowed = product.purchasable and product.limitsPurchaseAllowed
    model.setId(productCD)
    model.setIsNew(productCD not in getSeenProducts())
    model.setType(productType)
    model.setRank(product.rank)
    model.setLimitedQuantity(product.limitedQuantity)
    model.setState(_getProductState(productCD, purchaseAllowed, not product.limitsPurchaseAllowed))
    model.setDescription(product.description)
    model.price.setName(product.currencyName)
    model.price.setValue(product.originalPrice)
    model.price.setIsEnough(isEnoughMoney)
    if product.discountPrice:
        model.price.setDiscountValue(product.discountPrice)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getProductState(productCD, purchaseAllowed, isPersonalLimitsReached, itemsCache=None):
    product = itemsCache.items.getItemByCD(productCD)
    isSinglePurchasableItemType = product.itemTypeID in (GUI_ITEM_TYPE.VEHICLE, GUI_ITEM_TYPE.STYLE)
    if product.itemTypeID == GUI_ITEM_TYPE.STYLE:
        isInInventory = product.fullCount() > 0
    else:
        isInInventory = product.isInInventory
    if isInInventory and isSinglePurchasableItemType:
        return ProductState.PURCHASED
    if product.isRestorePossible():
        return ProductState.READYTORESTORE
    if isPersonalLimitsReached:
        if isSinglePurchasableItemType and not isInInventory:
            return ProductState.INPROGRESS
        return ProductState.PURCHASED
    return ProductState.LOCKED if not purchaseAllowed else ProductState.READYTOPURCHASE


def _setSpecificData(model, productCD, productType):
    productSetters = {ProductTypes.VEHICLE: _setVehicleSpecificData,
     ProductTypes.STYLE3D: _setStyleSpecificData,
     ProductTypes.REWARD: _setRewardSpecificData}
    productSetters[productType](model, productCD)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _setVehicleSpecificData(model, productCD, itemsCache=None):
    vehicle = itemsCache.items.getItemByCD(productCD)
    model.setCanGoToHangar(vehicle.isInInventory)
    model.setTooltipId(TOOLTIP_TYPE.VEHICLE)
    fillVehicleModel(model.vehicleInfo, vehicle)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _setStyleSpecificData(model, productCD, itemsCache=None):
    vCompDescr, style = getVehicleCDAndStyle(productCD)
    if not vCompDescr:
        return
    vehicle = itemsCache.items.getItemByCD(vCompDescr)
    fillVehicleModel(model.vehicleInfo, vehicle)
    model.setName(style.userName)
    model.setCanGoToCustomization(vehicle.isCustomizationEnabled())


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _setRewardSpecificData(model, productCD, itemsCache=None):
    reward = itemsCache.items.getItemByCD(productCD)
    bonus = ItemsBonus('items', {reward.intCD: 1})
    packedBonus = getComp7BonusPacker().pack(bonus)[0]
    model.reward.setName(packedBonus.getName())
    model.reward.setOverlayType(packedBonus.getOverlayType())
    model.reward.setItem(packedBonus.getItem())
    model.reward.setLabel(packedBonus.getLabel())
    model.reward.setValue(packedBonus.getValue())
