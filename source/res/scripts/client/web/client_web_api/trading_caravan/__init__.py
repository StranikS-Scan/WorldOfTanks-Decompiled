# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/trading_caravan/__init__.py
from gui.ClientUpdateManager import g_clientUpdateManager
from web.client_web_api.api import C2WHandler, c2w
_TOKEN_PREFIX = 'trading_caravan:'

class TradingCaravanEventHandler(C2WHandler):

    def init(self):
        super(TradingCaravanEventHandler, self).init()
        g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdate)

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self, True)
        super(TradingCaravanEventHandler, self).fini()

    def __onTokensUpdate(self, diff):
        for token in diff.keys():
            if token.startswith(_TOKEN_PREFIX):
                self.__sendToken(token)

    @c2w(name='tokens_update')
    def __sendToken(self, token):
        return token
