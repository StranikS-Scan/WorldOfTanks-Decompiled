# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/ranked/__init__.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared import g_eventBus
from web.client_web_api.api import C2WHandler, c2w
from web.web_client_api.ranked_battles import BROWSER_BRIDGE_EVENT
_ALLOWED_TOKENS = {'ranked_shop_no_log'}

class RankedEventHandler(C2WHandler):

    def init(self):
        super(RankedEventHandler, self).init()
        g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdate)

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self, True)
        super(RankedEventHandler, self).fini()

    def __onTokensUpdate(self, diff):
        tokens = list(_ALLOWED_TOKENS.intersection(diff.keys()))
        if tokens:
            self.__sendTokens(tokens)

    @c2w(name='tokens_update')
    def __sendTokens(self, tokens):
        return tokens


class BrowsersBridgeC2W(C2WHandler):

    def init(self):
        super(BrowsersBridgeC2W, self).init()
        g_eventBus.addListener(BROWSER_BRIDGE_EVENT, self.__handleProxyData)

    def fini(self):
        g_eventBus.removeListener(BROWSER_BRIDGE_EVENT, self.__handleProxyData)
        super(BrowsersBridgeC2W, self).fini()

    @c2w(name='browser_bridge_event')
    def __handleProxyData(self, event):
        return event.ctx
