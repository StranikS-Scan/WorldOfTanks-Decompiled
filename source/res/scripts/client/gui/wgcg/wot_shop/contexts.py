# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/wot_shop/contexts.py
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType

class WotShopGetStorefrontProductsCtx(CommonWebRequestCtx):
    __slots__ = ('__storefront',)

    def __init__(self, ctx, waitingID=''):
        self.__storefront = ctx.storefront
        super(WotShopGetStorefrontProductsCtx, self).__init__(waitingID)

    def getRequestType(self):
        return WebRequestDataType.WOT_SHOP_GET_STOREFRONT_PRODUCTS

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getStorefront(self):
        return self.__storefront


class WotShopPurchaseStorefrontProductCtx(CommonWebRequestCtx):
    __slots__ = ('__storefront', '__productCode', '__expectedPrice')

    def __init__(self, storefront, productCode, expectedPrice, waitingID=''):
        self.__storefront = storefront
        self.__productCode = productCode
        self.__expectedPrice = expectedPrice
        super(WotShopPurchaseStorefrontProductCtx, self).__init__(waitingID)

    def getRequestType(self):
        return WebRequestDataType.WOT_SHOP_BUY_STOREFRONT_PRODUCT

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getStorefront(self):
        return self.__storefront

    def getProductCode(self):
        return self.__productCode

    def getExpectedPrice(self):
        return self.__expectedPrice
