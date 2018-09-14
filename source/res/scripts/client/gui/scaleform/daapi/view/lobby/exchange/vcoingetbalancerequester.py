# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/exchange/VcoinGetBalanceRequester.py
import time
import BigWorld
import Event
from adisp import process
from gui.shared.utils.requesters import ItemsRequester, DeprecatedStatsRequester
import constants

class _VcoinGetBalanceRequester(object):
    CACHE_ENABLED = False

    def __init__(self):
        self.onEbankGetBalanceComplete = Event.Event()
        self.__isCached = False
        self.__isWaitForSync = False
        self.goldBalance = 0
        self.balance = 0
        self.exchangeRate = 0
        self.error = ''
        self.minTransactVal = 50
        self.maxTransactVal = 500000
        self.__balanceCooldown = time.time()
        self.__balanceCallback = None
        return

    def request(self):

        def syncData():
            self.__balanceCallback = None
            if self.__isCached:
                self.onEbankGetBalanceComplete('')
                return
            elif self.__isWaitForSync:
                return
            else:
                self.__isWaitForSync = True
                self.__processSyncEBankData()
                return

        if self.__balanceCallback is None:
            self.__balanceCallback = BigWorld.callback(max(self.__balanceCooldown - time.time(), 0), lambda : syncData())
        return

    @process
    def __processSyncEBankData(self):
        self.balance, self.error = yield DeprecatedStatsRequester().ebankGetBalance()
        self.__isCached = _VcoinGetBalanceRequester.CACHE_ENABLED and not len(self.error)
        self.__isWaitForSync = False
        self.__updateBalanceCooldown()
        if len(self.error) == 0:
            items = yield ItemsRequester().request()
            self.goldBalance = items.stats.actualGold
            self.exchangeRate = items.shop.ebankVCoinExchangeRate
            self.minTransactVal = items.shop.ebankMinTransactionValue
            self.maxTransactVal = items.shop.ebankMaxTransactionValue
        self.onEbankGetBalanceComplete(self.error)

    def __updateBalanceCooldown(self):
        self.__balanceCooldown = time.time() + constants.REQUEST_COOLDOWN.EBANK_GET_BALANCE

    def cancelBalanceCallback(self):
        if self.__balanceCallback is not None:
            BigWorld.cancelCallback(self.__balanceCallback)
            self.__balanceCallback = None
        return


g_instance = _VcoinGetBalanceRequester()
