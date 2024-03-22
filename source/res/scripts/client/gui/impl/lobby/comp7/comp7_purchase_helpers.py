# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_purchase_helpers.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel
from gui.impl.gen.view_models.views.lobby.comp7.base_product_model import ProductState, ProductTypes
from gui.impl.gen.view_models.views.lobby.comp7.reward_product_model import RewardProductModel
from gui.impl.gen.view_models.views.lobby.comp7.style3d_product_model import Style3dProductModel
from gui.impl.gen.view_models.views.lobby.comp7.vehicle_product_model import VehicleProductModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.comp7.comp7_c11n_helpers import getStylePreviewVehicle
from gui.shared.economics import getGUIPrice
from gui.shared.money import Currency
from helpers import dependency
from items import ITEM_TYPES, parseIntCompactDescr
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Union, Type
    from gui.shared.gui_items.fitting_item import FittingItem
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.shared.gui_items.customization.c11n_items import Style
    T_PRODUCT_MODEL = Union[VehicleProductModel, Style3dProductModel, RewardProductModel]
    T_PRODUCT_MODEL_TYPE = Union[Type[VehicleProductModel], Type[Style3dProductModel], Type[RewardProductModel]]

class _BaseProductPacker(object):
    __slots__ = ('__itemCD',)
    _itemsCache = dependency.descriptor(IItemsCache)
    __tradeInController = dependency.descriptor(ITradeInController)

    def __init__(self, itemCD):
        super(_BaseProductPacker, self).__init__()
        self.__itemCD = itemCD

    @property
    def _productModel(self):
        raise NotImplementedError

    @property
    def _productType(self):
        raise NotImplementedError

    def pack(self, price):
        item = self._itemsCache.items.getItemByCD(self.__itemCD)
        productModel = self._productModel()
        productModel.setId(self.__itemCD)
        productModel.setType(self._productType)
        productModel.setState(self.__getState(item))
        self._setProductSpecificData(item, productModel)
        self.__setPriceModelData(item, price, productModel.price)
        return productModel

    def _setProductSpecificData(self, item, productModel):
        pass

    def __getState(self, item):
        if item.isInInventory:
            return ProductState.PURCHASED
        return ProductState.READYTORESTORE if item.isRestoreAvailable() else ProductState.READYTOPURCHASE

    def __setPriceModelData(self, item, price, priceModel):
        if item.isRestorePossible():
            self.__setRestorePrice(item, priceModel)
        else:
            self.__setProductPrice(price, priceModel)

    def __setRestorePrice(self, item, priceModel):
        price = getGUIPrice(item, self._itemsCache.items.stats.money, self._itemsCache.items.shop.exchangeRate)
        currency = price.getCurrency()
        money = self._itemsCache.items.stats.money
        priceModel.setName(currency)
        priceModel.setValue(price.get(currency, 0))
        priceModel.setIsEnough(item.mayRestoreWithExchange(money, self._itemsCache.items.shop.exchangeRate))

    def __setProductPrice(self, price, priceModel):
        currency = price.get('currency')
        value = price.get('value')
        priceModel.setName(currency)
        priceModel.setValue(value)
        money = self._itemsCache.items.stats.money
        priceModel.setIsEnough(money.get(currency, 0) >= value)


class _VehiclePacker(_BaseProductPacker):

    @property
    def _productModel(self):
        return VehicleProductModel

    @property
    def _productType(self):
        return ProductTypes.VEHICLE

    def _setProductSpecificData(self, item, productModel):
        fillVehicleModel(productModel.vehicleInfo, item)
        productModel.setDescription(item.shortDescriptionSpecial or backport.text(R.strings.paragons.progressionPage.showroom.vehicle.defaultShortDescriptionSpecial()))


class _StylePacker(_BaseProductPacker):

    @property
    def _productModel(self):
        return Style3dProductModel

    @property
    def _productType(self):
        return ProductTypes.STYLE3D

    def _setProductSpecificData(self, item, productModel):
        productModel.setDescription(item.getDescription())
        productModel.setName(item.userName)
        vehicleCD = getStylePreviewVehicle(item)
        vehicleItem = self._itemsCache.items.getItemByCD(vehicleCD)
        fillVehicleModel(productModel.vehicleInfo, vehicleItem)


class _OptionalDevicePacker(_BaseProductPacker):

    @property
    def _productModel(self):
        return RewardProductModel

    @property
    def _productType(self):
        return ProductTypes.REWARD


def getComp7ProductModel(itemCD, price):
    itemTypeID = getItemType(itemCD)
    packer = None
    if itemTypeID == ITEM_TYPES.vehicle:
        packer = _VehiclePacker(itemCD)
    elif itemTypeID == ITEM_TYPES.customizationItem:
        packer = _StylePacker(itemCD)
    elif itemTypeID == ITEM_TYPES.optionalDevice:
        packer = _OptionalDevicePacker(itemCD)
    if packer is None:
        raise SoftException('Could not find packer for {}'.format(itemCD))
    return packer.pack(price)


def getItemType(itemCD):
    return parseIntCompactDescr(itemCD)[0]


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getComp7BalanceModel(itemsCache=None):
    balance = []
    for currency in (Currency.CRYSTAL,
     Currency.GOLD,
     Currency.CREDITS,
     Currency.FREE_XP):
        currencyModel = PriceItemModel()
        currencyModel.setName(currency)
        if currency == Currency.FREE_XP:
            currencyModel.setValue(itemsCache.items.stats.actualFreeXP)
        else:
            currencyModel.setValue(itemsCache.items.stats.actualMoney.get(currency, 0))
        balance.append(currencyModel)

    return balance


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def updateComp7BalanceModel(balanceModel, itemsCache=None):
    for currencyModel in balanceModel:
        currency = currencyModel.getName()
        if currency == Currency.FREE_XP:
            currencyModel.setValue(itemsCache.items.stats.actualFreeXP)
        currencyModel.setValue(itemsCache.items.stats.actualMoney.get(currency, 0))
