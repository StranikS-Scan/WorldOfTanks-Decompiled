# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ExchangeWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ExchangeWindowMeta(DAAPIModule):

    def as_setSecondaryCurrencyS(self, credits):
        if self._isDAAPIInited():
            return self.flashObject.as_setSecondaryCurrency(credits)

    def as_setWalletStatusS(self, walletStatus):
        if self._isDAAPIInited():
            return self.flashObject.as_setWalletStatus(walletStatus)
