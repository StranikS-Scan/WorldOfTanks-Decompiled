# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/exchange/ConfirmExchangeDialog.py
from adisp import adisp_process
from gui import SystemMessages
from gui.Scaleform.daapi.view.meta.ConfirmExchangeDialogMeta import ConfirmExchangeDialogMeta
from gui.impl.lobby.exchange.exchange_rates_helper import handleUserValuesInput, showAllPersonalDiscountsWindow, handleAndRoundStepperInput
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus

class ConfirmExchangeDialog(ConfirmExchangeDialogMeta):

    def __init__(self, meta, handler):
        super(ConfirmExchangeDialog, self).__init__()
        self.handler = handler
        self.__selectedGold, self.__selectedResource = (0, 0)
        self.__exchangeMutex = False
        self.__setMeta(meta)

    def updateDialog(self, meta, handler):
        if self.handler is not None:
            self._callHandler(False)
        self.handler = handler
        self.__removeMeta()
        self.__exchangeMutex = False
        self.__setMeta(meta)
        self.__prepareAndSendData()
        return

    def onSelectedAmountChanged(self, goldValue, needItemsValue):
        if goldValue != self.__selectedGold:
            needItemsValue = 0
        else:
            goldValue = 0
        self.__selectedGold, self.__selectedResource = handleAndRoundStepperInput({'gold': goldValue,
         'currency': needItemsValue}, exchangeRate=self.meta.getExchangeProvider(), validateGold=True)
        isLimitExceeded = self.meta.discountsAmountAppliedForExchange(self.__selectedGold)
        self.as_setExchangeValuesS(self.__selectedGold, self.__selectedResource, isLimitExceeded)
        g_eventBus.handleEvent(events.ExchangeRatesDiscountsEvent(events.ExchangeRatesDiscountsEvent.ON_SELECTED_AMOUNT_CHANGED, {'amount': self.__selectedGold}), scope=EVENT_BUS_SCOPE.LOBBY)

    def openDiscountInfoPage(self):
        showAllPersonalDiscountsWindow(exchangeRateType=self.meta.getExchangeType(), selectedValue={'currency': self.__selectedResource})

    def onWindowClose(self):
        self._callHandler(False)
        self.destroy()

    @adisp_process
    def exchange(self, goldValue):
        if self.__exchangeMutex:
            return
        else:
            self.__exchangeMutex = True
            exchangedValue = self.meta.getResourceAmountToExchangeForGold(goldValue)
            result = yield self.meta.submit(goldValue, exchangedValue)
            if result is not None:
                SystemMessages.pushMessagesFromResult(result)
            if result is not None and result.success and self.meta is not None:
                self._callHandler(True, self.meta.getTypeCompDescr())
                self.destroy()
            else:
                self.__exchangeMutex = False
            return

    def _populate(self):
        super(ConfirmExchangeDialog, self)._populate()
        self.__prepareAndSendData()

    def _dispose(self):
        self.__removeMeta()
        self.handler = None
        super(ConfirmExchangeDialog, self)._dispose()
        return

    def _callHandler(self, success, *kwargs):
        if self.handler is not None:
            self.handler((success, kwargs))
        return

    def __removeMeta(self):
        if self.meta is not None:
            self.meta.onInvalidate -= self.__prepareAndSendData
            self.meta.onCloseDialog -= self.onWindowClose
            self.meta.destroy()
            self.meta = None
        return

    def __setMeta(self, meta):
        self.meta = meta
        self.meta.onInvalidate += self.__prepareAndSendData
        self.meta.onCloseDialog += self.onWindowClose

    def __prepareAndSendData(self, *args):
        self.as_updateS(self.meta.makeVO())
        self.__selectedResource = self.meta.getResourceToExchange()
        self.__selectedGold, self.__selectedResource = handleUserValuesInput(selectedGold=0, selectedCurrency=self.__selectedResource, exchangeProvider=self.meta.getExchangeProvider())
        isLimitExceeded = self.meta.discountsAmountAppliedForExchange(self.__selectedGold)
        self.as_setExchangeValuesS(self.__selectedGold, self.__selectedResource, isLimitExceeded)
