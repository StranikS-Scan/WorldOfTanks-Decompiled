# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BaseExchangeWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class BaseExchangeWindowMeta(AbstractWindowView):

    def exchange(self, data):
        self._printOverrideError('exchange')

    def as_setPrimaryCurrencyS(self, value):
        return self.flashObject.as_setPrimaryCurrency(value) if self._isDAAPIInited() else None

    def as_exchangeRateS(self, data):
        return self.flashObject.as_exchangeRate(data) if self._isDAAPIInited() else None
