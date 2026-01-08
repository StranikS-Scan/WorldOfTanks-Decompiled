# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/stronghold/__init__.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.lobby.stronghold.stronghold_helpers import getClanSeasonProgressLevel
from web.client_web_api.api import C2WHandler, c2w
_ALLOWED_TOKEN = 'clan_season_progress'

class StrongholdEventHandler(C2WHandler):

    def init(self):
        super(StrongholdEventHandler, self).init()
        g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdate)

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self, True)
        super(StrongholdEventHandler, self).fini()

    def __onTokensUpdate(self, diff):
        if _ALLOWED_TOKEN in diff:
            self.__sendToken({_ALLOWED_TOKEN: getClanSeasonProgressLevel()})

    @c2w(name='stronghold_token_update')
    def __sendToken(self, tokenInfo):
        return tokenInfo
