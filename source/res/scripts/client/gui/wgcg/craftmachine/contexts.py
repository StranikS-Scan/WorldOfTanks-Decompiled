# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/craftmachine/contexts.py
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType

class CraftmachineModulesInfoCtx(CommonWebRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.CRAFTMACHINE_MODULES_INFO

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False
