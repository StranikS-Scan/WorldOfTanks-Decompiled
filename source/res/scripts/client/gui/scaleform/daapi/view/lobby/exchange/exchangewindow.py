# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/exchange/ExchangeWindow.py
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.ExchangeWindowMeta import ExchangeWindowMeta
from gui.shared.gui_items.processors.common import GoldToCreditsExchanger
from gui.shared.utils import decorators
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared import IItemsCache

class ExchangeWindow(ExchangeWindowMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    wallet = dependency.descriptor(IWalletController)

    def _populate(self):
        super(ExchangeWindow, self)._populate()
        stats = self.itemsCache.items.stats
        self.as_setPrimaryCurrencyS(stats.actualGold)
        self.as_setSecondaryCurrencyS(stats.actualCredits)
        self.as_exchangeRateS({'value': self.itemsCache.items.shop.defaults.exchangeRate,
         'actionValue': self.itemsCache.items.shop.exchangeRate,
         'actionMode': True})
        self.as_setWalletStatusS(self.wallet.componentsStatuses)

    @decorators.adisp_process('transferMoney')
    def exchange(self, gold):
        result = yield GoldToCreditsExchanger(gold).request()
        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            self.onWindowClose()

    def _subscribe(self):
        g_clientUpdateManager.addCurrencyCallback(Currency.CREDITS, self.__setCreditsCallBack)
        g_clientUpdateManager.addCurrencyCallback(Currency.GOLD, self._setGoldCallBack)
        g_clientUpdateManager.addCallbacks({'shop.exchangeRate': self.__setExchangeRateCallBack})
        self.wallet.onWalletStatusChanged += self.__setWalletCallback
        self.itemsCache.onSyncCompleted += self.__setExchangeRateCallBack

    def __setExchangeRateCallBack(self, *args):
        self.as_exchangeRateS({'value': self.itemsCache.items.shop.defaults.exchangeRate,
         'actionValue': self.itemsCache.items.shop.exchangeRate,
         'actionMode': True})

    def __setCreditsCallBack(self, credit):
        self.as_setSecondaryCurrencyS(credit)

    def __setWalletCallback(self, status):
        self.as_setPrimaryCurrencyS(self.itemsCache.items.stats.actualGold)
        self.as_setWalletStatusS(status)

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        self.itemsCache.onSyncCompleted -= self.__setExchangeRateCallBack
        self.wallet.onWalletStatusChanged -= self.__setWalletCallback
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(ExchangeWindow, self)._dispose()
