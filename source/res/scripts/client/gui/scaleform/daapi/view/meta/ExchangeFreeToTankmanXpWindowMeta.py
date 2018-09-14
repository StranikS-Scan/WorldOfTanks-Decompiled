# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ExchangeFreeToTankmanXpWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ExchangeFreeToTankmanXpWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def apply(self):
        """
        :return :
        """
        self._printOverrideError('apply')

    def onValueChanged(self, data):
        """
        :param data:
        :return :
        """
        self._printOverrideError('onValueChanged')

    def calcValueRequest(self, value):
        """
        :param value:
        :return :
        """
        self._printOverrideError('calcValueRequest')

    def as_setInitDataS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setInitData(value) if self._isDAAPIInited() else None

    def as_setCalcValueResponseS(self, price, actionPriceData):
        """
        :param price:
        :param actionPriceData:
        :return :
        """
        return self.flashObject.as_setCalcValueResponse(price, actionPriceData) if self._isDAAPIInited() else None

    def as_setWalletStatusS(self, walletStatus):
        """
        :param walletStatus:
        :return :
        """
        return self.flashObject.as_setWalletStatus(walletStatus) if self._isDAAPIInited() else None
