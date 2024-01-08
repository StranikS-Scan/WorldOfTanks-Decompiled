# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/hof/contexts.py
from gui.clans import items
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType
from shared_utils import makeTupleByDict

class _BaseHofRequestCtx(CommonWebRequestCtx):

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return makeTupleByDict(items.HofAttrs, incomeData)

    def isCaching(self):
        return False


class HofUserInfoCtx(_BaseHofRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.HOF_USER_INFO


class HofUserExcludeCtx(_BaseHofRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.HOF_USER_EXCLUDE


class HofUserRestoreCtx(_BaseHofRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.HOF_USER_RESTORE
