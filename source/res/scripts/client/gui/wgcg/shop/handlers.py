# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/shop/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class ShopRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.SHOP_INVENTORY_ENTITLEMENTS: self.__getInventoryEntitlements}
        return handlers

    def __getInventoryEntitlements(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('shop', 'get_inventory_entitlements'), entitlement_codes=ctx.getEntitlementCodes())
