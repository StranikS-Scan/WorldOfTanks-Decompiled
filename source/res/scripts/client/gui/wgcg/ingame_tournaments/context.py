# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/ingame_tournaments/context.py
from gui.wgcg.settings import WebRequestDataType
from gui.shared.utils.requesters import RequestCtx

class IngameTournamentGetDataCtx(RequestCtx):

    def getRequestType(self):
        return WebRequestDataType.INGAME_TOURNAMENT_GET_DATA

    def isAuthorizationRequired(self):
        return False

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False
