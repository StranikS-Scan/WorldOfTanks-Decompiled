# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BaseExchangeWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class BaseExchangeWindowMeta(DAAPIModule):

    def exchange(self, data):
        self._printOverrideError('exchange')

    def as_setPrimaryCurrencyS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setPrimaryCurrency(value)

    def as_exchangeRateS(self, value, actionValue):
        if self._isDAAPIInited():
            return self.flashObject.as_exchangeRate(value, actionValue)
