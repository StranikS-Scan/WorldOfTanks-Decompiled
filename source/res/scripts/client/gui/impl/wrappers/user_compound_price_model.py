# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/wrappers/user_compound_price_model.py
import logging
from typing import Tuple
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
    def fillPriceModelByItemPrice(cls, priceModel, itemPrice):
        action = itemPrice.getActionPrcAsMoney()
        if action.isDefined():
            cls.fillPriceModel(priceModel, itemPrice.price, action, itemPrice.defPrice)
        else:
            cls.fillPriceModel(priceModel, itemPrice.price)

    @classmethod
    def fillPriceModel(cls, priceModel, price, action=None, defPrice=None):
        cls.fillPriceItemModel(priceModel.getPrice(), price)
        if action is not None:
            cls.fillPriceItemModel(priceModel.getDiscount(), action)
            if defPrice is not None:
                cls.fillPriceItemModel(priceModel.getDefPrice(), defPrice)
            else:
                _logger.error('action and defPrice should be set both')
        return

    @classmethod
    def fillPriceItemModel(cls, array, price):
        array.reserve(len(price))
        for name, value in price.iteritems():
            priceItemModel = cls._createPriceItemModel(name, value)
            array.addViewModel(priceItemModel)

        array.invalidate()

    @classmethod
    def _createPriceItemModel(cls, name, value):
        priceItemModel = PriceItemModel()
        priceItemModel.setName(name)
        priceItemModel.setValue(value)
        return priceItemModel


class BuyPriceModelBuilder(PriceModelBuilder):
    _itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _createPriceItemModel(cls, name, value):
        priceItemModel = super(BuyPriceModelBuilder, cls)._createPriceItemModel(name, value)
        statsValue = cls._itemsCache.items.stats.money.get(name)
        if statsValue is not None:
            priceItemModel.setIsEnough(statsValue >= value)
        return priceItemModel
