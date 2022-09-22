# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/shop/contexts.py
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType

class InventoryEntitlementsCtx(CommonWebRequestCtx):
    __slots__ = ('__entitlementCodes',)

    def __init__(self, entitlementCodes=(), waitingID=''):
        super(InventoryEntitlementsCtx, self).__init__(waitingID)
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
