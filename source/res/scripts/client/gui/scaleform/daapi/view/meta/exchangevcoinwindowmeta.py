# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ExchangeVcoinWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ExchangeVcoinWindowMeta(DAAPIModule):

    def buyVcoin(self):
        self._printOverrideError('buyVcoin')

    def as_setTargetCurrencyDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setTargetCurrencyData(data)

    def as_setSecondaryCurrencyS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setSecondaryCurrency(value)
