# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/hero_tank/contexts.py
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType

class GetHeroTankRequestCtx(CommonWebRequestCtx):

    def __init__(self, waitingID=''):
        super(GetHeroTankRequestCtx, self).__init__(waitingID=waitingID)

    def isAuthorizationRequired(self):
        return False

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getRequestType(self):
        return WebRequestDataType.HERO_TANK_GET_LIST
