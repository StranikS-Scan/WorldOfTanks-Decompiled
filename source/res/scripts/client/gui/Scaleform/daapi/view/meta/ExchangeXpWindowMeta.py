# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ExchangeXpWindowMeta.py
from gui.Scaleform.daapi.view.lobby.exchange.BaseExchangeWindow import BaseExchangeWindow

class ExchangeXpWindowMeta(BaseExchangeWindow):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseExchangeWindow
    """

    def as_vehiclesDataChangedS(self, data):
        """
        :param data: Represented by ExchangeXPWindowVO (AS)
        """
        return self.flashObject.as_vehiclesDataChanged(data) if self._isDAAPIInited() else None

    def as_totalExperienceChangedS(self, value):
        return self.flashObject.as_totalExperienceChanged(value) if self._isDAAPIInited() else None

    def as_setWalletStatusS(self, walletStatus):
        return self.flashObject.as_setWalletStatus(walletStatus) if self._isDAAPIInited() else None
