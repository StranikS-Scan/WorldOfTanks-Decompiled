# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/wrappers/user_compound_price_model.py
import logging
from typing import Iterable, Optional
from gui.impl.gen.view_models.common.compound_price_model import CompoundPriceModel
from gui.impl.gen.view_models.common.price_model import PriceModel
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel
from gui.shared.money import Money
from gui.shared.gui_items.gui_item_economics import ItemPrice
from user_list_model import UserListModel
_logger = logging.getLogger(__name__)

class UserCompoundPriceModel(CompoundPriceModel):
    __slots__ = ()

    def clear(self):
        self.prices.clearItems()
        self.prices.invalidate()

    def assign(self, *itemPrices):
        self.clear()
        for itemPrice in itemPrices:
            action = itemPrice.getActionPrcAsMoney()
            if action.isDefined():
                priceModel = getPriceModel(itemPrice.price, action, itemPrice.defPrice)
            else:
                priceModel = getPriceModel(itemPrice.price)
            self.prices.addViewModel(priceModel)

        self.prices.invalidate()


def getPriceModel(price, action=None, defPrice=None):
    model = PriceModel()
    fillPriceItemModel(model.price, price)
    if action is not None:
        fillPriceItemModel(model.discount, action)
        if defPrice is not None:
            fillPriceItemModel(model.defPrice, defPrice)
        else:
            _logger.error('action and defPrice should be set both')
    return model


def fillPriceItemModel(model, price):
    for name, value in price.iteritems():
        priceItemModel = PriceItemModel()
        priceItemModel.setName(name)
        priceItemModel.setValue(value)
        model.addViewModel(priceItemModel)

    model.invalidate()
    return model
