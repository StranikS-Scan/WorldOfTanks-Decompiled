# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/util/token.py
from gui.ClientUpdateManager import g_clientUpdateManager
from web.client_web_api.api import C2WHandler, c2w

class TokenEventHandler(C2WHandler):

    def init(self):
        super(TokenEventHandler, self).init()
        g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdate)

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(TokenEventHandler, self).fini()

    @c2w(name='tokens_update')
    def __onTokensUpdate(self, diff):
        result = {}
        for tokenID in diff:
            expireTimestamp, amount = diff[tokenID] if diff[tokenID] else (0, 0)
            result[tokenID] = {'expireTimestamp': expireTimestamp,
             'amount': amount}

        return result
