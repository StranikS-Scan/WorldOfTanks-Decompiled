# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/shop/stats.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared import IItemsCache
from web.client_web_api.api import C2WHandler, c2w
from web.common import getWalletCurrencyStatuses, getBalance

class BalanceEventHandler(C2WHandler):
    __walletController = dependency.descriptor(IWalletController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def init(self):
        super(BalanceEventHandler, self).init()
        self.__walletController.onWalletStatusChanged += self.__onWalletUpdate
        g_clientUpdateManager.addCallbacks({'stats.{}'.format(c):self.__onBalanceUpdate for c in Currency.EXTENDED})
        g_clientUpdateManager.addCallbacks({'cache.dynamicCurrencies': self.__onBalanceUpdate})

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)
        self.__walletController.onWalletStatusChanged -= self.__onWalletUpdate
        super(BalanceEventHandler, self).fini()

    @c2w(name='balance_update')
    def __onBalanceUpdate(self, *_):
        return getBalance(self.__itemsCache.items.stats)

    @c2w(name='wallet_update')
    def __onWalletUpdate(self, *_):
        return getWalletCurrencyStatuses(self.__itemsCache.items.stats)
