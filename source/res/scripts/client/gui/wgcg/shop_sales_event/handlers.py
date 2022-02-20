# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/shop_sales_event/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class ShopSalesEventRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.SHOP_SALES_EVENT_FETCH_FAVORITES: self.__fetchFavorites}
        return handlers

    def __fetchFavorites(self, ctx, callback):
        reqCtx = self._requester.doRequestEx(ctx, callback, ('shop_sales_event', 'shop_sales_event_fetch_favorites'))
        return reqCtx
