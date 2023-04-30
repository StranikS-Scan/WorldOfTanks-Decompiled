# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/utils/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class UtilsRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.SPA_GET_ACCOUNT_ATTRIBUTE: self.__getAccountAttributeByPrefix,
         WebRequestDataType.PLATFORM_FETCH_PRODUCT_LIST: self.__fetchProductList,
         WebRequestDataType.PLATFORM_GET_USER_SUBSCRIPTIONS: self.__getUserSubscriptions}
        return handlers

    def __getAccountAttributeByPrefix(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('spa', 'get_account_attribute_by_prefix'), ctx.getRequestedAttr())

    def __fetchProductList(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('agate', 'agate_v4_fetch_product_list_state'), ctx.getParams())

    def __getUserSubscriptions(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('agate', 'agate_v5_get_user_subscriptions'), ctx.getParams())
