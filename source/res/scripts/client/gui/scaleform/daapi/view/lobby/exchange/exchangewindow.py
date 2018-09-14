# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/exchange/ExchangeWindow.py
import BigWorld
from PlayerEvents import g_playerEvents
from gui import SystemMessages, game_control
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.ExchangeWindowMeta import ExchangeWindowMeta
from gui.shared import g_itemsCache
from gui.shared.gui_items.processors.common import GoldToCreditsExchanger
from gui.shared.utils import decorators

class ExchangeWindow(ExchangeWindowMeta):

    def _populate(self):
        super(ExchangeWindow, self)._populate()
        stats = g_itemsCache.items.stats
        self.as_setPrimaryCurrencyS(stats.actualGold)
        self.as_setSecondaryCurrencyS(stats.actualCredits)
        self.as_exchangeRateS(g_itemsCache.items.shop.defaults.exchangeRate, g_itemsCache.items.shop.exchangeRate)
        self.as_setWalletStatusS(game_control.g_instance.wallet.componentsStatuses)

    @decorators.process('transferMoney')
    def exchange(self, gold):
        result = yield GoldToCreditsExchanger(gold).request()
        if result and len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            self.onWindowClose()

    def _subscribe(self):
        g_clientUpdateManager.addCallbacks({'stats.credits': self.__setCreditsCallBack,
         'stats.gold': self._setGoldCallBack,
         'shop.exchangeRate': self.__setExchangeRateCallBack})
        game_control.g_instance.wallet.onWalletStatusChanged += self.__setWalletCallback
        g_itemsCache.onSyncCompleted += self.__setExchangeRateCallBack

    def __setExchangeRateCallBack(self, *args):
        self.as_exchangeRateS(g_itemsCache.items.shop.defaults.exchangeRate, g_itemsCache.items.shop.exchangeRate)

    def __setCreditsCallBack(self, credits):
        self.as_setSecondaryCurrencyS(credits)

    def __setWalletCallback(self, status):
        self.as_setPrimaryCurrencyS(g_itemsCache.items.stats.actualGold)
        self.as_setWalletStatusS(status)

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        g_itemsCache.onSyncCompleted -= self.__setExchangeRateCallBack
        game_control.g_instance.wallet.onWalletStatusChanged -= self.__setWalletCallback
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(ExchangeWindow, self)._dispose()
