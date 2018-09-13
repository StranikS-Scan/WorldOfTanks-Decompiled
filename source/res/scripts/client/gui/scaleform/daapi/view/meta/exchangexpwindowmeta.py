# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ExchangeXpWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ExchangeXpWindowMeta(DAAPIModule):

    def as_vehiclesDataChangedS(self, isHaveElite, data):
        if self._isDAAPIInited():
            return self.flashObject.as_vehiclesDataChanged(isHaveElite, data)

    def as_totalExperienceChangedS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_totalExperienceChanged(value)

    def as_setWalletStatusS(self, walletStatus):
        if self._isDAAPIInited():
            return self.flashObject.as_setWalletStatus(walletStatus)
