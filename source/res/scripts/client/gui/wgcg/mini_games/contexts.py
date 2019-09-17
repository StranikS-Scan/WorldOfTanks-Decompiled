# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/mini_games/contexts.py
from gui.wgcg.settings import WebRequestDataType
from gui.shared.utils.requesters import RequestCtx

class FestivalMiniGamesDataCtx(RequestCtx):

    def getRequestType(self):
        return WebRequestDataType.FESTIVAL_MINI_GAMES_DATA

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False
