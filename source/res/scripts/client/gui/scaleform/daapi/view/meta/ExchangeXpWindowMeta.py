# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ExchangeXpWindowMeta.py
from gui.Scaleform.daapi.view.lobby.exchange.BaseExchangeWindow import BaseExchangeWindow

class ExchangeXpWindowMeta(BaseExchangeWindow):

    def getSubmitButtonEnableState(self, selectedXPCount):
        self._printOverrideError('getSubmitButtonEnableState')

    def as_vehiclesDataChangedS(self, data):
        return self.flashObject.as_vehiclesDataChanged(data) if self._isDAAPIInited() else None

    def as_totalExperienceChangedS(self, value):
        return self.flashObject.as_totalExperienceChanged(value) if self._isDAAPIInited() else None

    def as_setWalletStatusS(self, walletStatus, enableSubmitButton):
        return self.flashObject.as_setWalletStatus(walletStatus, enableSubmitButton) if self._isDAAPIInited() else None
