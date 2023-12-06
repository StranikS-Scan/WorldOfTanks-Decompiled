# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/shop/contexts.py
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType

class ShopInventoryEntitlementsCtx(CommonWebRequestCtx):
    __slots__ = ('__entitlementCodes',)

    def __init__(self, entitlementCodes=(), waitingID=''):
        super(ShopInventoryEntitlementsCtx, self).__init__(waitingID)
        self.__entitlementCodes = entitlementCodes

    def getRequestType(self):
        return WebRequestDataType.SHOP_INVENTORY_ENTITLEMENTS

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getEntitlementCodes(self):
        return self.__entitlementCodes

    @staticmethod
    def getDataObj(incomeData):
        return incomeData


class ShopStorefrontProductsCtx(CommonWebRequestCtx):
    __slots__ = ('__storefront',)

    def __init__(self, storefront='', waitingID=''):
        super(ShopStorefrontProductsCtx, self).__init__(waitingID)
        self.__storefront = storefront

    def getRequestType(self):
        return WebRequestDataType.SHOP_GET_STOREFRONT_PRODUCTS

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getStorefront(self):
        return self.__storefront

    @staticmethod
    def getDataObj(incomeData):
        return incomeData


class ShopBuyStorefrontProductCtx(CommonWebRequestCtx):
    __slots__ = ('__storefront', '__product_code', '__amount', '__prices')

    def __init__(self, storefront='', productCode='', amount=1, prices=None, waitingID=''):
        super(ShopBuyStorefrontProductCtx, self).__init__(waitingID)
        self.__storefront = storefront
        self.__productCode = productCode
        self.__amount = amount
        self.__prices = prices

    def getRequestType(self):
        return WebRequestDataType.SHOP_BUY_STOREFRONT_PRODUCTS

    def getStorefront(self):
        return self.__storefront

    def getProductCode(self):
        return self.__productCode

    def getData(self):
        return {'prices': self.__prices,
         'amount': self.__amount}

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    @staticmethod
    def getDataObj(incomeData):
        return incomeData
