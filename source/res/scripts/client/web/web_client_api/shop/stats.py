# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/shop/stats.py
import logging
from constants import PREM_TYPE_TO_ENTITLEMENT
from gui.game_control.wallet import WalletController
from gui.shared.money import Currency
from helpers import dependency
from helpers import time_utils
from web.web_client_api import W2CSchema, w2c
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class BalanceWebApiMixin(object):
    itemsCache = dependency.descriptor(IItemsCache)

    @w2c(W2CSchema, 'get_balance')
    def getBalance(self, cmd):
        stats = self.itemsCache.items.stats
        money = stats.actualMoney
        premiumExpireLocalTime = time_utils.makeLocalServerTime(stats.activePremiumExpiryTime)
        if premiumExpireLocalTime:
            premiumExpireISOTime = time_utils.timestampToISO(premiumExpireLocalTime)
        else:
            premiumExpireISOTime = None
        balanceData = {currency:money.get(currency, 0) for currency in Currency.ALL}
        balanceData.update({'walletStatus': {key:WalletController.STATUS.getKeyByValue(code).lower() for key, code in stats.currencyStatuses.items() if key in Currency.ALL},
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
