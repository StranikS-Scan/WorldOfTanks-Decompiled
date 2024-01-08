# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/product_purchase/wot_shop_purchase_controller.py
import logging
from functools import partial
from BWUtil import AsyncReturn
from adisp import adisp_process
from gui.wgcg.wot_shop.contexts import WotShopPurchaseStorefrontProductCtx
from helpers import dependency
from skeletons.gui.platform.product_purchase_controller import IWotShopPurchaseController, WotShopPrice
from skeletons.gui.web import IWebController
from wg_async import wg_async, await_callback
_logger = logging.getLogger(__name__)

class WotShopPurchaseController(IWotShopPurchaseController):
    __webCtrl = dependency.descriptor(IWebController)

    @wg_async
    def purchaseProduct(self, storefront, productCode, expectedPrice):
        ctx = WotShopPurchaseStorefrontProductCtx(storefront=storefront, productCode=productCode, expectedPrice=expectedPrice)
        _logger.debug('Trying to purchase product: %s', ctx)
        success = yield await_callback(partial(self.__purchaseProduct, ctx))()
        _logger.debug('Purchase product response: %s', success)
        raise AsyncReturn(success)

    @adisp_process
    def __purchaseProduct(self, ctx, callback):
        response = yield self.__webCtrl.sendRequest(ctx=ctx)
        callback(response.isSuccess())
