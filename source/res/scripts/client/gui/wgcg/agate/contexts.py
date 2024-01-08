# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/agate/contexts.py
import typing
from enum import Enum
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType
if typing.TYPE_CHECKING:
    from typing import Dict, List

class InventoryEntitlementsCtx(CommonWebRequestCtx):
    __slots__ = ('__entitlementCodes',)

    def __init__(self, entitlementCodes=(), waitingID=''):
        super(InventoryEntitlementsCtx, self).__init__(waitingID)
        self.__entitlementCodes = entitlementCodes

    def getRequestType(self):
        return WebRequestDataType.AGATE_INVENTORY_ENTITLEMENTS

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getEntitlementCodes(self):
        return self.__entitlementCodes


class AgateGetInventoryEntitlementsCtx(CommonWebRequestCtx):

    class _FilterKeys(Enum):
        CODE = 'code'
        TAG = 'tag'

    class _FilterOperators(Enum):
        IN = 'in'
        NOT_IN = 'not_in'
        EQ = 'eq'
        NEQ = 'neq'

    __slots__ = ('__entitlementsFilter',)

    def __init__(self, entitlementsFilter, waitingID=''):
        self.__entitlementsFilter = entitlementsFilter
        super(AgateGetInventoryEntitlementsCtx, self).__init__(waitingID=waitingID)

    def getRequestType(self):
        return WebRequestDataType.AGATE_GET_INVENTORY_ENTITLEMENTS_V5

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getEntitlementsFilter(self):
        return self.__entitlementsFilter

    @classmethod
    def createFilterByTags(cls, tags):
        tagsFilter = {'key': cls._FilterKeys.TAG.value,
         'operator': cls._FilterOperators.IN.value,
         'value': tags}
        return {'filter': [tagsFilter]}

    @classmethod
    def createFilterByCodes(cls, codes):
        operator, value = cls.__makeRequestArgsForValues(codes)
        return {'filter': [{'key': cls._FilterKeys.CODE.value,
                     'operator': operator,
                     'value': value}]}

    @classmethod
    def __makeRequestArgsForValues(cls, valuesList):
        return (cls._FilterOperators.IN.value, valuesList) if len(valuesList) > 1 else (cls._FilterOperators.EQ.value, valuesList[0])
