# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/agate/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class AgateRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.AGATE_INVENTORY_ENTITLEMENTS: self.__getInventoryEntitlements,
         WebRequestDataType.AGATE_GET_INVENTORY_ENTITLEMENTS_V5: self.__getInventoryEntitlementsV5}
        return handlers

    def __getInventoryEntitlements(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('agate', 'get_inventory_entitlements'), entitlement_codes=ctx.getEntitlementCodes())

    def __getInventoryEntitlementsV5(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('agate', 'get_inventory_entitlements_v5'), entitlementsFilter=ctx.getEntitlementsFilter())
