# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/shop_sales_event/events.py
from helpers import dependency
from gui.ClientUpdateManager import g_clientUpdateManager
from skeletons.gui.game_control import IShopSalesEventController
from web.client_web_api.api import C2WHandler, c2w
from web.common import formatShopSalesInfo
from shared_utils import findFirst
_ALLOWED_TOKENS = {'cn_11_11_free_reroll_bundle', 'cn_11_11_free_reroll_bundle_purchased'}

class ShopSalesEventHandler(C2WHandler):
    __shopSalesEvent = dependency.descriptor(IShopSalesEventController)
    __TOKEN_PREFIX = 'cn_11_11_bought'

    def init(self):
        super(ShopSalesEventHandler, self).init()
        self.__shopSalesEvent.onStateChanged += self.__onInfoChanged
        self.__shopSalesEvent.onBundlePurchased += self.__onBundlePurchased
        self.__shopSalesEvent.onCurrentBundleChanged += self.__onInfoChanged
        g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdate)

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self, True)
        self.__shopSalesEvent.onCurrentBundleChanged -= self.__onInfoChanged
        self.__shopSalesEvent.onBundlePurchased -= self.__onBundlePurchased
        self.__shopSalesEvent.onStateChanged -= self.__onInfoChanged
        super(ShopSalesEventHandler, self).fini()

    @c2w(name='shop_sales_info_updated')
    def __onInfoChanged(self):
        return formatShopSalesInfo()

    @c2w(name='shop_sales_bundle_purchased', preventIdentical=False)
    def __onBundlePurchased(self, messageData):
        tokens = (messageData or {}).get('data', {}).get('tokens', {})
        bToken = findFirst(lambda s: self.__TOKEN_PREFIX in s, tokens, '')
        return {'entitlement': bToken.split(':')[-1]} if bToken else None

    def __onTokensUpdate(self, diff):
        tokens = list(_ALLOWED_TOKENS.intersection(diff.keys()))
        if tokens:
            self.__sendTokens(tokens)

    @c2w(name='shop_sales_tokens_updated')
    def __sendTokens(self, tokens):
        return tokens
