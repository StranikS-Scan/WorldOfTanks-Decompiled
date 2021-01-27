# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/bob/contexts.py
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType

class BobGetTeamSkillsCtx(CommonWebRequestCtx):

    def __init__(self, timestamp=None, **kwargs):
        super(BobGetTeamSkillsCtx, self).__init__(**kwargs)
        self.__timestamp = timestamp

    def getTimestamp(self):
        return self.__timestamp

    def getRequestType(self):
        return WebRequestDataType.BOB_GET_TEAM_SKILLS

    @staticmethod
    def getDataObj(incomeData):
        data = incomeData or {}
        return data

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False


class BobGetTeamsCtx(CommonWebRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.BOB_GET_TEAMS

    def isClanSyncRequired(self):
        return False

    def isAuthorizationRequired(self):
        return True

    @staticmethod
    def getDataObj(incomeData):
        data = incomeData or {}
        return data
