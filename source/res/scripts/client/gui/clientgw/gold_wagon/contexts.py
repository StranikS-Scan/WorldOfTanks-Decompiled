# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clientgw/gold_wagon/contexts.py
from gui.clientgw.base.contexts import CommonWebRequestCtx
from gui.clientgw.settings import WebRequestDataType

class GoldWagonFetchInfoCtx(CommonWebRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.GOLD_WAGON_INFO

    def isAuthorizationRequired(self):
        return False

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False
