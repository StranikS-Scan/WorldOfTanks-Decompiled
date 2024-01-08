# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/wot_shop/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class WotShopRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.WOT_SHOP_GET_STOREFRONT_PRODUCTS: self.__getStorefrontProducts,
         WebRequestDataType.WOT_SHOP_BUY_STOREFRONT_PRODUCT: self.__buyStorefrontProduct}
        return handlers

    def __getStorefrontProducts(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('wot_shop', 'get_storefront_products'), ctx)

    def __buyStorefrontProduct(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('wot_shop', 'buy_storefront_product'), ctx)
