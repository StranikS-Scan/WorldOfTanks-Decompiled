# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/wrappers/user_compound_price_model.py
import logging
from typing import Optional, Tuple
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.compound_price_model import CompoundPriceModel
from gui.impl.gen.view_models.common.price_model import PriceModel
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel
from gui.shared.money import Money
from gui.shared.gui_items.gui_item_economics import ItemPrice
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
            action = itemPrice.getActionPrcAsMoney()
            if action.isDefined():
                priceModel = getPriceModel(itemPrice.price, action, itemPrice.defPrice)
            else:
                priceModel = getPriceModel(itemPrice.price)
            prices.addViewModel(priceModel)

        prices.invalidate()


def getPriceModel(price, action=None, defPrice=None):
    model = PriceModel()
    fillPriceItemModel(model.getPrice(), price)
    if action is not None:
        fillPriceItemModel(model.getDiscount(), action)
        if defPrice is not None:
            fillPriceItemModel(model.getDefPrice(), defPrice)
        else:
            _logger.error('action and defPrice should be set both')
    return model


def fillPriceItemModel(array, price):
    array.reserve(len(price))
    for name, value in price.iteritems():
        priceItemModel = PriceItemModel()
        priceItemModel.setName(name)
        priceItemModel.setValue(value)
        array.addViewModel(priceItemModel)

    array.invalidate()
