# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/wot_shop/controller.py
import logging
import typing
from BWUtil import AsyncReturn
from helpers import dependency
from skeletons.gui.platform.product_fetch_controller import IWotShopFetchController
from skeletons.gui.platform.product_purchase_controller import IWotShopPurchaseController
from wg_async import wg_async, wg_await
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from gui.platform.products_fetcher.wot_shop.fetch_result import WotShopFetchResult

class IShopController(object):

    def fetchProducts(self, storefront, forceFetch=False):
        raise NotImplementedError

    def buyProduct(self, storefront, code):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError


class IWotShopController(IShopController):
    pass


class WotShopController(IWotShopController):
    __wotShopFetchController = dependency.descriptor(IWotShopFetchController)
    __wotShopPurchaseController = dependency.descriptor(IWotShopPurchaseController)

    @wg_async
    def fetchProducts(self, storefront, forceFetch=False):
        if forceFetch:
            self.__wotShopFetchController.reset()
        fetchResult = yield wg_await(self.__wotShopFetchController.getProducts(storefront=storefront, showWaiting=False))
        raise AsyncReturn(fetchResult.getData())

    @wg_async
    def buyProduct(self, storefront, code, expectedPrice):
        result = yield wg_await(self.__wotShopPurchaseController.purchaseProduct(storefront, code, expectedPrice))
        raise AsyncReturn(result)

    def fini(self):
        self.__wotShopFetchController.fini()
