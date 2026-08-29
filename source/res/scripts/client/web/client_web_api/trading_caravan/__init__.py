# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/trading_caravan/__init__.py
from helpers import dependency
from gui.ClientUpdateManager import g_clientUpdateManager
from web.client_web_api.api import C2WHandler, c2w
_TOKEN_PREFIX = 'trading_caravan:'
_PROGRESSION_TOKEN = 'trading_caravan_progression_update'
_ENTITLEMENT_NAME = 'caravan_guaranteed_reward_points'

class TradingCaravanEventHandler(C2WHandler):

    def init(self):
        super(TradingCaravanEventHandler, self).init()
        g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdate)
        g_clientUpdateManager.addCallback('cache.entitlements', self.__updateEntitlements)

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self, True)
        super(TradingCaravanEventHandler, self).fini()

    def __updateEntitlements(self, entitlements):
        caravanCoinsCount = entitlements.get(_ENTITLEMENT_NAME, 0)
        if caravanCoinsCount:
            self.__sendCaravanEntitlementsBalance(caravanCoinsCount)

    def __onTokensUpdate(self, diff):
        for token in diff.keys():
            if token.startswith(_TOKEN_PREFIX):
                self.__sendToken(token)
            if token == _PROGRESSION_TOKEN:
                self.__sendUpdate()

    @c2w(name='tokens_update')
    def __sendToken(self, token):
        return token

    @c2w(name='progression_update')
    def __sendUpdate(self):
        return True

    @c2w(name='entitlements_update')
    def __sendCaravanEntitlementsBalance(self, caravanCoinsCount):
        return caravanCoinsCount
