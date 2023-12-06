# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/utils/contexts.py
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType

class SPAAccountAttributeCtx(CommonWebRequestCtx):

    def __init__(self, ctx, waitingID=''):
        self.__attrPrefix = ctx.attr_prefix
        super(SPAAccountAttributeCtx, self).__init__(waitingID=waitingID)

    def getRequestType(self):
        return WebRequestDataType.SPA_GET_ACCOUNT_ATTRIBUTE

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getRequestedAttr(self):
        return self.__attrPrefix

    @staticmethod
    def getDataObj(incomeData):
        return incomeData

    @staticmethod
    def getDefDataObj():
        return None


class PlatformFetchProductListCtx(CommonWebRequestCtx):

    def __init__(self, ctx, waitingID=''):
        self.__params = {'storefront': ctx.storefront,
         'wgid': ctx.wgid,
         'language': ctx.language,
         'additional_data': ctx.additional_data,
         'country': ctx.country,
         'response_fields': ctx.response_fields,
         'response_fields_profile': ctx.response_fields_profile,
         'category': ctx.category}
        if ctx.product_codes:
            self.__params.update(product_codes=ctx.product_codes)
        super(PlatformFetchProductListCtx, self).__init__(waitingID=waitingID)

    def getRequestType(self):
        return WebRequestDataType.PLATFORM_FETCH_PRODUCT_LIST

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getParams(self):
        return self.__params

    @staticmethod
    def getDataObj(incomeData):
        return incomeData

    @staticmethod
    def getDefDataObj():
        return None


class PlatformFetchProductListPersonalCtx(CommonWebRequestCtx):

    def __init__(self, ctx, waitingID=''):
        self.__params = {'storefront': ctx.storefront,
         'language': ctx.language,
         'country': ctx.country}
        if ctx.product_codes:
            self.__params.update(product_codes=ctx.product_codes)
        super(PlatformFetchProductListPersonalCtx, self).__init__(waitingID=waitingID)

    def getRequestType(self):
        return WebRequestDataType.PLATFORM_FETCH_PRODUCT_LIST_PERSONAL

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getParams(self):
        return self.__params

    @staticmethod
    def getDataObj(incomeData):
        return incomeData

    @staticmethod
    def getDefDataObj():
        return None


class PlatformGetUserSubscriptionsCtx(CommonWebRequestCtx):

    def __init__(self, ctx, waitingID=''):
        self.__params = {'status': ctx.status,
         'product_code': ctx.productCode}
        super(PlatformGetUserSubscriptionsCtx, self).__init__(waitingID=waitingID)

    def getRequestType(self):
        return WebRequestDataType.PLATFORM_GET_USER_SUBSCRIPTIONS

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getParams(self):
        return self.__params

    @staticmethod
    def getDataObj(incomeData):
        return incomeData

    @staticmethod
    def getDefDataObj():
        return None
