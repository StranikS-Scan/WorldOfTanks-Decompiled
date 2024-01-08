# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/utils/contexts.py
from typing import TYPE_CHECKING
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType
if TYPE_CHECKING:
    from gui.platform.products_fetcher.user_subscriptions.controller import PlatformGetUserSubscriptionsParams

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
