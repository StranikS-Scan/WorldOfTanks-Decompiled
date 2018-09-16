# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ExchangeWindowMeta.py
from gui.Scaleform.daapi.view.lobby.exchange.BaseExchangeWindow import BaseExchangeWindow

class ExchangeWindowMeta(BaseExchangeWindow):

    def as_setSecondaryCurrencyS(self, credits):
        return self.flashObject.as_setSecondaryCurrency(credits) if self._isDAAPIInited() else None

    def as_setWalletStatusS(self, walletStatus):
        return self.flashObject.as_setWalletStatus(walletStatus) if self._isDAAPIInited() else None
