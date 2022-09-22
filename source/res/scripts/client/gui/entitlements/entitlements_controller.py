# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/entitlements/entitlements_controller.py
import logging
from adisp import process
from async import async, await_callback
from BWUtil import AsyncReturn
from gui.entitlements.entitlement_cache import ShopEntitlementsCache
from gui.wgcg.shop.contexts import InventoryEntitlementsCtx
from gui.wgcg.states import WebControllerStates
from helpers import dependency
from skeletons.gui.game_control import IEntitlementsController
from skeletons.gui.web import IWebController
_logger = logging.getLogger(__name__)

class EntitlementsController(IEntitlementsController):
    __slots__ = ('__cache', '__cacheSyncInProgress', '__lastFailedEntitlements')
    __webController = dependency.descriptor(IWebController)

    def __init__(self):
        super(EntitlementsController, self).__init__()
        self.__cache = None
        self.__cacheSyncInProgress = False
        self.__lastFailedEntitlements = set()
        return

    @property
    def isCacheInited(self):
        return self.__cache is not None

    def onDisconnected(self):
        self.__cache = None
        self.__cacheSyncInProgress = False
        self.__lastFailedEntitlements.clear()
        return

    def onLobbyInited(self, event):
        self.__lastFailedEntitlements.clear()
        if self.__webController.getStateID() == WebControllerStates.STATE_NOT_DEFINED:
            self.__webController.invalidate()

    def getEntitlementFromCache(self, code):
        return self.__cache.getEntitlementBalance(code) if self.isCacheInited else None

    def getConsumedEntitlementFromCache(self, code):
        return self.__cache.getHoldConsumedEntitlement(code) if self.isCacheInited else None

    def getGrantedEntitlementFromCache(self, code):
        return self.__cache.getHoldGrantedEntitlement(code) if self.isCacheInited else None

    def isCodesWasFailedInLastRequest(self, codes):
        return not self.__lastFailedEntitlements.isdisjoint(codes)

    def updateCache(self, codes):
        self.__sendRequest(codes, lambda *args: True)

    @async
    def forceUpdateCache(self, codes):
        result = yield await_callback(self.__sendRequest)(codes)
        raise AsyncReturn(result)

    @process
    def __sendRequest(self, codes, callback):
        if self.__cacheSyncInProgress:
            callback(False)
            return
        else:
            if self.__webController.isAvailable():
                try:
                    self.__cacheSyncInProgress = True
                    response = yield self.__webController.sendRequest(ctx=InventoryEntitlementsCtx(entitlementCodes=codes))
                finally:
                    self.__cacheSyncInProgress = False

                if response.isSuccess():
                    result = InventoryEntitlementsCtx.getDataObj(response.data)
                    if self.__cache is not None:
                        self.__cache.update(codes, result.get('data', {}))
                        self.__lastFailedEntitlements.difference_update(codes)
                    else:
                        self.__cache = ShopEntitlementsCache(result.get('data', {}))
                else:
                    if self.__cache is not None:
                        self.__lastFailedEntitlements.update(codes)
                    _logger.warning('Failed to get entitlements data. Code: %s.', response.getCode())
                callback(response.isSuccess())
            else:
                _logger.warning("Failed to get entitlements data. Web controller isn't available")
                callback(False)
            return
