# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/shop/stats.py
import logging
import adisp
from async import async, await
from constants import PREM_TYPE_TO_ENTITLEMENT
from gui.game_control.wallet import WalletController
from gui.shared.money import Currency
from gui.shared.utils.vehicle_collector_helper import hasCollectibleVehicles
from helpers import dependency
from helpers import time_utils
import nations
from skeletons.gui.game_control import IEntitlementsController
from skeletons.gui.shared import IItemsCache
from web.web_client_api import W2CSchema, w2c, Field
_logger = logging.getLogger(__name__)

class _GetInventoryEntitlementsSchema(W2CSchema):
    force = Field(required=False, type=int, default=False)
    codes = Field(required=True, type=list)


class BalanceWebApiMixin(object):
    itemsCache = dependency.descriptor(IItemsCache)
    __entitlementsController = dependency.descriptor(IEntitlementsController)

    @w2c(W2CSchema, 'get_balance')
    def getBalance(self, cmd):
        stats = self.itemsCache.items.stats
        money = stats.actualMoney
        premiumExpireLocalTime = time_utils.makeLocalServerTime(stats.activePremiumExpiryTime)
        if premiumExpireLocalTime:
            premiumExpireISOTime = time_utils.timestampToISO(premiumExpireLocalTime)
        else:
            premiumExpireISOTime = None
        balanceData = {Currency.currencyExternalName(currency):money.get(currency, 0) for currency in Currency.ALL}
        balanceData.update({'walletStatus': {Currency.currencyExternalName(key):WalletController.STATUS.getKeyByValue(code).lower() for key, code in stats.currencyStatuses.items() if key in Currency.ALL},
         'premiumExpireDate': premiumExpireISOTime})
        return balanceData

    @w2c(W2CSchema, 'get_stats')
    def getStats(self, cmd):

        def getTrainingCost(prices, currency):
            if isinstance(prices, dict):
                prices = [ pair[1] for pair in sorted(prices.iteritems(), key=lambda i: i[0]) ]
            try:
                return [ price for price in prices if price.get(currency, None) ][0][currency]
            except IndexError:
                msg = 'unspecified price for currency {}'.format(currency)
                _logger.warning(msg)
                return 0.0

            return None

        getters = {'changeRoleCost': lambda stats: stats.changeRoleCost,
         'freeXPConversionDiscrecity': lambda stats: stats.freeXPConversion[0],
         'slotsPrices': lambda stats: stats.slotsPrices[1][0],
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
         'default': getter(defaultStats)} for key, getter in getters.iteritems()}

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

    @adisp.async
    @async
    def __forceUpdateEntitlementsCache(self, codes, callback):
        result = yield await(self.__entitlementsController.forceUpdateCache(codes))
        callback(result)
