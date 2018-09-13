# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/exchange/ExchangeVcoinWindow.py
import BigWorld
from debug_utils import LOG_WARNING
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.exchange import VcoinGetBalanceRequester
from gui.Scaleform.daapi.view.lobby.exchange.BaseExchangeWindow import BaseExchangeWindow
from gui.Scaleform.daapi.view.lobby.exchange import VcoinUpdateBalanceRequester
from gui.Scaleform.daapi.view.meta.ExchangeVcoinWindowMeta import ExchangeVcoinWindowMeta
from gui.Scaleform.locale.WAITING import WAITING
from gui import SystemMessages
from gui.shared.events import OpenLinkEvent
from helpers import i18n

class ExchangeVcoinWindow(ExchangeVcoinWindowMeta, BaseExchangeWindow):
    VCOIN_COUNT_STEP = 1

    def _populate(self):
        super(ExchangeVcoinWindow, self)._populate()
        self.as_showWaitingS(i18n.makeString(WAITING.WAITING_EBANK_RESPONSE), {})
        VcoinUpdateBalanceRequester.g_instance.onEbankUpdateBalanceComplete += self.onUpdateBalanceCompleteHandler
        VcoinGetBalanceRequester.g_instance.onEbankGetBalanceComplete += self.eBankGetBalanceHandler
        VcoinGetBalanceRequester.g_instance.request()

    def eBankGetBalanceHandler(self, error):
        if len(error):
            self.onWindowClose()
            LOG_WARNING('Server error while getting EBank data: %s' % error)
            self.__showErrorSysMsg(error)
            return
        g_clientUpdateManager.addCallbacks({'stats.gold': self._setGoldCallBack})
        self.__sendData()

    def _setGoldCallBack(self, gold):
        self.as_setSecondaryCurrencyS(gold)

    def __sendData(self):
        self.as_hideWaitingS()
        vcoinRequester = VcoinGetBalanceRequester.g_instance
        self.as_setSecondaryCurrencyS(vcoinRequester.goldBalance)
        self.as_setPrimaryCurrencyS(vcoinRequester.balance)
        self.as_exchangeRateS(vcoinRequester.exchangeRate, vcoinRequester.exchangeRate)
        self.as_setTargetCurrencyDataS({'minTransactVal': vcoinRequester.minTransactVal,
         'maxTransactVal': vcoinRequester.maxTransactVal,
         'countStep': ExchangeVcoinWindow.VCOIN_COUNT_STEP})

    def buyVcoin(self):
        self.fireEvent(OpenLinkEvent(OpenLinkEvent.PAYMENT))

    def exchange(self, data):
        self.as_showWaitingS(WAITING.WAITING_EBANK_RESPONSE, {})
        VcoinUpdateBalanceRequester.g_instance.update(data)

    def onUpdateBalanceCompleteHandler(self, errStr, vcoin):
        if len(errStr) == 0:
            vcoinBalance = VcoinGetBalanceRequester.g_instance.balance
            self.__showSuccessSysMsg(vcoin * VcoinGetBalanceRequester.g_instance.exchangeRate, vcoin)
            self.onWindowClose()
            return
        LOG_WARNING('EBank buyGold request failed:', errStr)
        self.__showErrorSysMsg(errStr)
        self.as_hideWaitingS()

    def __showSuccessSysMsg(self, gold, vcoin):
        SystemMessages.g_instance.pushMessage(i18n.makeString('#system_messages:ebank/response/success') % {'gold': BigWorld.wg_getGoldFormat(gold),
         'vcoin': BigWorld.wg_getIntegralFormat(vcoin)}, type=SystemMessages.SM_TYPE.FinancialTransactionWithGold)

    def __showErrorSysMsg(self, msg):
        SystemMessages.g_instance.pushMessage(i18n.makeString('#system_messages:ebank/response/%s' % str(msg)), type=SystemMessages.SM_TYPE.Error)

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        VcoinUpdateBalanceRequester.g_instance.cancelBuyCallback()
        VcoinGetBalanceRequester.g_instance.cancelBalanceCallback()
        VcoinUpdateBalanceRequester.g_instance.onEbankUpdateBalanceComplete -= self.onUpdateBalanceCompleteHandler
        VcoinGetBalanceRequester.g_instance.onEbankGetBalanceComplete -= self.eBankGetBalanceHandler
        super(ExchangeVcoinWindow, self)._dispose()
