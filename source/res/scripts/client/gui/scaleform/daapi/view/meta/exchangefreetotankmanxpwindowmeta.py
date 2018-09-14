# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ExchangeFreeToTankmanXpWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ExchangeFreeToTankmanXpWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def apply(self):
        self._printOverrideError('apply')

    def onValueChanged(self, data):
        self._printOverrideError('onValueChanged')

    def calcValueRequest(self, value):
        self._printOverrideError('calcValueRequest')

    def as_setInitDataS(self, value):
        return self.flashObject.as_setInitData(value) if self._isDAAPIInited() else None

    def as_setCalcValueResponseS(self, price, actionPriceData):
        return self.flashObject.as_setCalcValueResponse(price, actionPriceData) if self._isDAAPIInited() else None

    def as_setWalletStatusS(self, walletStatus):
        return self.flashObject.as_setWalletStatus(walletStatus) if self._isDAAPIInited() else None
