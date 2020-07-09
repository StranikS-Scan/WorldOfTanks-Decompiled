# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/rank/contexts.py
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType

class RankedPositionCtx(CommonWebRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.RANKED_LEAGUE_POSITION

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    @staticmethod
    def getDataObj(incomeData):
        return incomeData

    @staticmethod
    def getDefDataObj():
        return None


class RankedYearPositionCtx(CommonWebRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.RANKED_YEAR_POSITION

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    @staticmethod
    def getDataObj(incomeData):
        return incomeData

    @staticmethod
    def getDefDataObj():
        return None
