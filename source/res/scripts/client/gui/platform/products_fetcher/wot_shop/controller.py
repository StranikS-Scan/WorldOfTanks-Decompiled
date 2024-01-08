# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/products_fetcher/wot_shop/controller.py
import logging
from gui.platform.products_fetcher.controller import ProductsFetchController
from gui.platform.products_fetcher.wot_shop.descriptors.account_limits_descriptor import AccountLimitsDescriptor
from gui.platform.products_fetcher.wot_shop.descriptors.categories_descriptor import CategoriesDescriptor
from gui.platform.products_fetcher.wot_shop.descriptors.product_descriptor import ProductDescriptor
from gui.platform.products_fetcher.wot_shop.fetch_result import WotShopFetchResult
from gui.wgcg.wot_shop.contexts import WotShopGetStorefrontProductsCtx
from skeletons.gui.platform.product_fetch_controller import IWotShopFetchController
_logger = logging.getLogger(__name__)

class WotShopFetcherController(ProductsFetchController, IWotShopFetchController):
    platformFetchCtx = WotShopGetStorefrontProductsCtx
    productDescriptor = ProductDescriptor
    accountLimitsDescriptor = AccountLimitsDescriptor
    categoriesDescriptor = CategoriesDescriptor
    dataGetKey = 'data'
    downloadRequired = False

    @property
    def _fetchResultType(self):
        return WotShopFetchResult

    def _createDescriptors(self, data):
        self._fetchResult.setProducts(map(self.productDescriptor, data['items']))
        self._fetchResult.setAccountLimits(map(self.accountLimitsDescriptor, data['account_limits']))
        self._fetchResult.setCategories(map(self.categoriesDescriptor, data['categories']))

    def getProducts(self, showWaiting=True, **kwargs):
        self.platformParams.storefront = kwargs['storefront']
        return super(WotShopFetcherController, self).getProducts(showWaiting)
