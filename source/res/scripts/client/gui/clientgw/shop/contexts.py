# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clientgw/shop/contexts.py
import BigWorld
from constants import SPA_ATTRS
from gui.clientgw.base.contexts import CommonWebRequestCtx
from gui.clientgw.settings import WebRequestDataType

class ShopRequestCtx(CommonWebRequestCtx):
    __slots__ = ('__userCountry',)

    def __init__(self, waitingID='', userCountry=''):
        super(ShopRequestCtx, self).__init__(waitingID)
        self.__userCountry = userCountry

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getCountryCode(self):
        country = BigWorld.player().spaFlags.getFlag(SPA_ATTRS.USER_COUNTRY) or self.__userCountry
        return country.upper()

    @staticmethod
    def getDataObj(incomeData):
        return incomeData


class ShopInventoryEntitlementsCtx(ShopRequestCtx):
    __slots__ = ('__entitlementCodes',)

    def __init__(self, entitlementCodes=(), waitingID=''):
        super(ShopInventoryEntitlementsCtx, self).__init__(waitingID)
        self.__entitlementCodes = entitlementCodes

    def getRequestType(self):
        return WebRequestDataType.SHOP_INVENTORY_ENTITLEMENTS

    def getEntitlementCodes(self):
        return self.__entitlementCodes


class ShopStorefrontProductsCtx(ShopRequestCtx):
    __slots__ = ('__storefront',)

    def __init__(self, storefront='', waitingID='', userCountry=''):
        super(ShopStorefrontProductsCtx, self).__init__(waitingID, userCountry)
        self.__storefront = storefront
        self.__userCountry = userCountry

    def getRequestType(self):
        return WebRequestDataType.SHOP_GET_STOREFRONT_PRODUCTS

    def getStorefront(self):
        return self.__storefront


class ShopBuyStorefrontProductCtx(ShopStorefrontProductsCtx):
    __slots__ = ('__storefront', '__productCode', '__amount', '__prices')

    def __init__(self, storefront='', productCode='', amount=1, prices=None, waitingID='', userCountry=''):
        super(ShopBuyStorefrontProductCtx, self).__init__(storefront, waitingID, userCountry)
        self.__storefront = storefront
        self.__productCode = productCode
        self.__amount = amount
        self.__prices = prices

    def getRequestType(self):
        return WebRequestDataType.SHOP_BUY_STOREFRONT_PRODUCTS

    def getProductCode(self):
        return self.__productCode

    def getData(self):
        return {'prices': self.__prices,
         'amount': self.__amount}
