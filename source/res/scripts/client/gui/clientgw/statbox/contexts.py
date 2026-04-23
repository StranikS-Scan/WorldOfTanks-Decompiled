# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clientgw/statbox/contexts.py
from gui.clientgw.base.contexts import CommonWebRequestCtx
from gui.clientgw.settings import WebRequestDataType

class StatBoxGetInfoCtx(CommonWebRequestCtx):

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getRequestType(self):
        return WebRequestDataType.STATBOX_STATISTICS_INFO
