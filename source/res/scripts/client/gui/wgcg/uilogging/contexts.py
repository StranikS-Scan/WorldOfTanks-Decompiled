# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/uilogging/contexts.py
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType

class UILoggingSessionCtx(CommonWebRequestCtx):

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getRequestType(self):
        return WebRequestDataType.UI_LOGGING_SESSION
