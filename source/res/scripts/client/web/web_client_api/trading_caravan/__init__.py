# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/trading_caravan/__init__.py
from helpers import dependency
from web.web_client_api import w2c, w2capi, W2CSchema
from skeletons.gui.shared import IItemsCache
_ENTITLEMENT_NAME = 'caravan_guaranteed_reward_points'

@w2capi(name='trading_caravan', key='action')
class TradingCaravanWebApi(W2CSchema):
    __itemsCache = dependency.descriptor(IItemsCache)

    @w2c(W2CSchema, name='get_trading_caravan_entitlements')
    def getTradingCaravanEntitlements(self, _):
        entitlements = self.__itemsCache.items.stats.entitlements
        caravanCoinsCount = entitlements.get(_ENTITLEMENT_NAME, 0)
        return {_ENTITLEMENT_NAME: caravanCoinsCount}
