# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/frontline/contexts.py
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType

class FrontlineAccountAttributeCtx(CommonWebRequestCtx):

    def __init__(self, ctx, waitingID=''):
        self.__attrPrefix = ctx.attr_prefix
        super(FrontlineAccountAttributeCtx, self).__init__(waitingID=waitingID)

    def getRequestType(self):
        return WebRequestDataType.FRONTLINE_GET_ACCOUNT_ATTRIBUTE

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


class FrontlineFetchProductListCtx(CommonWebRequestCtx):

    def __init__(self, ctx, waitingID=''):
        self.__params = {'header': {},
         'body': {'storefront': ctx.storefront,
                  'wgid': ctx.wgid,
                  'language': ctx.language,
                  'additional_data': ctx.additional_data,
                  'country': ctx.country,
                  'response_fields': ctx.response_fields}}
        super(FrontlineFetchProductListCtx, self).__init__(waitingID=waitingID)

    def getRequestType(self):
        return WebRequestDataType.FRONTLINE_FETCH_PRODUCT_LIST

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
