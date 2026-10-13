# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/shop/stats.py
from __future__ import absolute_import
import logging
from future.utils import viewitems
import adisp
import nations
from wg_async import wg_async, wg_await
from constants import PREM_TYPE_TO_ENTITLEMENT
from gui.shared.money import Currency
from gui.shared.utils.vehicle_collector_helper import hasCollectibleVehicles
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEntitlementsController, IWalletController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils.requesters import IStatsRequester
from web.common import formatBalance, formatWalletCurrencyStatuses
from web.web_client_api import Field, W2CSchema, w2c
_logger = logging.getLogger(__name__)

class _GetInventoryEntitlementsSchema(W2CSchema):
    force = Field(required=False, type=int, default=False)
    codes = Field(required=True, type=list)


class BalanceWebApiMixin(object):
    itemsCache = dependency.descriptor(IItemsCache)
    __entitlementsController = dependency.descriptor(IEntitlementsController)
    __wallet = dependency.descriptor(IWalletController)

    @w2c(W2CSchema, 'get_balance')
    def getBalance(self, cmd):
        stats = self.itemsCache.items.stats
        premiumExpireLocalTime = time_utils.makeLocalServerTime(stats.activePremiumExpiryTime)
        if premiumExpireLocalTime:
            premiumExpireISOTime = time_utils.timestampToISO(premiumExpireLocalTime)
        else:
            premiumExpireISOTime = None
        response = formatBalance(stats)
        response.update({'walletStatus': formatWalletCurrencyStatuses(wallet=self.__wallet, itemsCache=self.itemsCache),
         'premiumExpireDate': premiumExpireISOTime})
        return response

    @w2c(W2CSchema, 'get_stats')
    def getStats(self, cmd):

        def getTrainingCost(prices, currency):
            if isinstance(prices, dict):
                prices = [ pair[1] for pair in sorted(viewitems(prices), key=lambda i: i[0]) ]
            try:
                return [ price for price in prices if price.get(currency, None) ][0][currency]
            except IndexError:
                msg = 'unspecified price for currency {}'.format(currency)
                _logger.warning(msg)
                return 0.0

            return None

        getters = {'changeRoleCost': lambda stats: stats.changeRoleCost,
         'freeXPConversionDiscrecity': lambda stats: stats.freeXPConversion[0],
         'creditsSlotsPrices': lambda stats: stats.slotsPrices[1][0][1] if stats.slotsPrices[1][0][0] == Currency.CREDITS else 0,
         'goldSlotsPrices': lambda stats: stats.slotsPrices[1][0][1] if stats.slotsPrices[1][0][0] == Currency.GOLD else 0,
         'berthsPrices': lambda stats: stats.berthsPrices[2][0],
         'goldTankmanCost': lambda stats: getTrainingCost(stats.tankmanCost, Currency.GOLD),
         'creditsTankmanCost': lambda stats: getTrainingCost(stats.tankmanCost, Currency.CREDITS),
         'goldDropSkillsCost': lambda stats: getTrainingCost(stats.dropSkillsCost, Currency.GOLD),
         'creditsDropSkillsCost': lambda stats: getTrainingCost(stats.dropSkillsCost, Currency.CREDITS),
         'freeXPToTManXPRate': lambda stats: stats.freeXPToTManXPRate,
         'paidRemovalCostGold': lambda stats: stats.paidRemovalCost,
         'exchangeRate': lambda stats: stats.exchangeRate,
         'dailyXPFactor': lambda stats: stats.dailyXPFactor,
         'clanCreationCost': lambda stats: stats.clanCreationCost}
        currentStats = self.itemsCache.items.shop
        defaultStats = self.itemsCache.items.shop.defaults
        return {key:{'current': getter(currentStats),
         'default': getter(defaultStats)} for key, getter in viewitems(getters)}

    @w2c(W2CSchema, 'get_premium_info')
    def getPremiumInfo(self, cmd):
        return {PREM_TYPE_TO_ENTITLEMENT[k]:v for k, v in self.itemsCache.items.stats.premiumInfo.items()}

    @w2c(W2CSchema, 'get_collection_nations')
    def getCollectionNations(self, cmd):
        return {nations.MAP[nationID]:self.itemsCache.items.stats.getMaxResearchedLevel(nationID) for nationID in nations.MAP if hasCollectibleVehicles(nationID)}

    @w2c(_GetInventoryEntitlementsSchema, 'get_inventory_entitlements')
    def getInventoryEntitlements(self, cmd):
        result = True
        if cmd.force:
            result = yield self.__forceUpdateEntitlementsCache(cmd.codes)
        entitlements = {}
        for code in cmd.codes:
            entitlement = self.__entitlementsController.getBalanceEntitlementFromCache(code)
            granted = self.__entitlementsController.getGrantedEntitlementFromCache(code)
            grantedAmount = granted.getAmount() if granted is not None else 0
            if entitlement is not None:
                entitlements[code] = {'amount': entitlement.getAmount() + grantedAmount,
                 'expires_at': entitlement.getExpiresAtData()}

        yield {'success': result and self.__entitlementsController.isCacheInited() and not self.__entitlementsController.isCodesWasFailedInLastRequest(cmd.codes),
         'entitlements': entitlements}
        return

    @adisp.adisp_async
    @wg_async
    def __forceUpdateEntitlementsCache(self, codes, callback):
        result = yield wg_await(self.__entitlementsController.forceUpdateCache(codes))
        callback(result)
