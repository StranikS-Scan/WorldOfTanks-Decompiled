# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/shop/stats.py
import logging
from constants import PREM_TYPE_TO_ENTITLEMENT
from gui.shared.money import Currency
from gui.shared.utils.vehicle_collector_helper import hasCollectibleVehicles
from helpers import dependency, time_utils
import nations
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils.requesters import IStatsRequester
from web.common import getWalletCurrencyStatuses, getBalance
from web.web_client_api import W2CSchema, w2c
_logger = logging.getLogger(__name__)

class BalanceWebApiMixin(object):
    itemsCache = dependency.descriptor(IItemsCache)

    @w2c(W2CSchema, 'get_balance')
    def getBalance(self, cmd):
        stats = self.itemsCache.items.stats
        premiumExpireLocalTime = time_utils.makeLocalServerTime(stats.activePremiumExpiryTime)
        if premiumExpireLocalTime:
            premiumExpireISOTime = time_utils.timestampToISO(premiumExpireLocalTime)
        else:
            premiumExpireISOTime = None
        response = getBalance(stats)
        response.update({'walletStatus': getWalletCurrencyStatuses(stats),
         'premiumExpireDate': premiumExpireISOTime})
        return response

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
