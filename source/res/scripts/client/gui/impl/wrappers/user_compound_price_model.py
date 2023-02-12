# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/wrappers/user_compound_price_model.py
import logging
from typing import Tuple, Optional
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.compound_price_model import CompoundPriceModel
from gui.impl.gen.view_models.common.price_model import PriceModel
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel
from gui.shared.money import Money
from gui.shared.gui_items.gui_item_economics import ItemPrice
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class UserCompoundPriceModel(CompoundPriceModel):
    __slots__ = ()

    def clear(self):
        prices = self.getPrices()
        prices.clear()
        prices.invalidate()

    def assign(self, *itemPrices):
        self.clear()
        prices = self.getPrices()
        prices.reserve(len(itemPrices))
        for itemPrice in itemPrices:
            priceModel = PriceModel()
            PriceModelBuilder.fillPriceModelByItemPrice(priceModel, itemPrice)
            prices.addViewModel(priceModel)

        prices.invalidate()


class PriceModelBuilder(object):

    @classmethod
    def getPriceModel(cls, price, action=None, defPrice=None):
        model = PriceModel()
        cls.fillPriceModel(model, price, action, defPrice)
        return model

    @classmethod
    def clearPriceModel(cls, priceModel):
        priceModel.getPrice().clear()
        priceModel.getDiscount().clear()
        priceModel.getDefPrice().clear()

    @classmethod
    def fillPriceModelByItemPrice(cls, priceModel, itemPrice, checkBalanceAvailability=False):
        action = itemPrice.getActionPrcAsMoney()
        if action.isDefined():
            cls.fillPriceModel(priceModel, itemPrice.price, action, itemPrice.defPrice, checkBalanceAvailability=checkBalanceAvailability)
        else:
            cls.fillPriceModel(priceModel, itemPrice.price, checkBalanceAvailability=checkBalanceAvailability)

    @classmethod
    def fillPriceModel(cls, priceModel, price, action=None, defPrice=None, checkBalanceAvailability=False):
        cls.fillPriceItemModel(priceModel.getPrice(), price, checkBalanceAvailability=checkBalanceAvailability)
        if action is not None:
            cls.fillPriceItemModel(priceModel.getDiscount(), action, checkBalanceAvailability=checkBalanceAvailability)
            if defPrice is not None:
                cls.fillPriceItemModel(priceModel.getDefPrice(), defPrice, checkBalanceAvailability=checkBalanceAvailability)
            else:
                _logger.error('action and defPrice should be set both')
        return

    @classmethod
    def fillPriceItemModel(cls, array, price, checkBalanceAvailability=False):
        array.reserve(len(price))
        for name, value in price.iteritems():
            priceItemModel = cls._createPriceItemModel(name, value)
            array.addViewModel(priceItemModel)

        array.invalidate()

    @classmethod
    def _createPriceItemModel(cls, name, value, _=False):
        priceItemModel = PriceItemModel()
        priceItemModel.setName(name)
        priceItemModel.setValue(value)
        return priceItemModel


class BuyPriceModelBuilder(PriceModelBuilder):
    _itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def fillPriceModel(cls, priceModel, price, action=None, defPrice=None, balance=None, checkBalanceAvailability=False):
        cls.fillPriceItemModel(priceModel.getPrice(), price, balance, checkBalanceAvailability=checkBalanceAvailability)
        if action is not None:
            cls.fillPriceItemModel(priceModel.getDiscount(), action, balance, checkBalanceAvailability=checkBalanceAvailability)
            if defPrice is not None:
                cls.fillPriceItemModel(priceModel.getDefPrice(), defPrice, balance, checkBalanceAvailability=checkBalanceAvailability)
            else:
                _logger.error('action and defPrice should be set both')
        return

    @classmethod
    def fillPriceItemModel(cls, array, price, balance=None, checkBalanceAvailability=False):
        array.reserve(len(price))
        for name, value in price.iteritems():
            priceItemModel = cls._createPriceItemModel(name, value, balance, checkBalanceAvailability=checkBalanceAvailability)
            array.addViewModel(priceItemModel)

        array.invalidate()

    @classmethod
    def _createPriceItemModel(cls, name, value, balance=None, checkBalanceAvailability=False):
        priceItemModel = super(BuyPriceModelBuilder, cls)._createPriceItemModel(name, value)
        stats = cls._itemsCache.items.stats
        statsValue = stats.money.get(name) if balance is None else balance.get(name)
        if checkBalanceAvailability and not stats.mayConsumeWalletResources:
            priceItemModel.setIsEnough(False)
        elif statsValue is not None:
            priceItemModel.setIsEnough(statsValue >= value)
        return priceItemModel
