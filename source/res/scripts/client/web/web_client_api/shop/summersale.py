# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/shop/summersale.py
import logging
from gui.shared.gui_items.processors.stall import PurchaseStallProductProcessor
from helpers import dependency
from skeletons.gui.game_control import ISummerSaleController
from skeletons.gui.shared import IItemsCache
from web.web_client_api import Field, W2CSchema, WebCommandException, w2c, w2capi
_logger = logging.getLogger(__name__)

def _amountValidator(amount, _=None):
    if amount and amount <= 0:
        raise WebCommandException('amount must be greater than 0')
    return True


class _ProductCodeSchema(W2CSchema):
    productCode = Field(required=True, type=basestring)


class _BuyProductSchema(W2CSchema):
    productCode = Field(required=True, type=basestring)
    amount = Field(required=False, type=int, validator=_amountValidator)


@w2capi(name='summersale', key='action')
class SummerSaleWebApi(W2CSchema):
    __summerSaleController = dependency.descriptor(ISummerSaleController)
    __itemsCache = dependency.descriptor(IItemsCache)

    @w2c(_BuyProductSchema, 'buy_product')
    def buyServerProductByCode(self, cmd):
        success, error = False, ''
        if self.__summerSaleController.isEnabled():
            response = yield PurchaseStallProductProcessor(cmd.productCode, cmd.amount).request()
            if response:
                success, error = response.success, response.userMsg
            else:
                error = 'Undefined server error'
        else:
            error = 'SummerSale event is not active'
        yield {'success': success,
         'error': error}

    @w2c(_ProductCodeSchema, 'get_product_lqo')
    def getLimitQuantity(self, cmd):
        yield {'count': self.__itemsCache.items.tokens.getTokenCount('{}_no_log'.format(cmd.productCode)) or 0,
         'success': True}
