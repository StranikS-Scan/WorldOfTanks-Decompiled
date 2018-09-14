# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationBuyWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class CustomizationBuyWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def buy(self):
        self._printOverrideError('buy')

    def selectItem(self, id):
        self._printOverrideError('selectItem')

    def deselectItem(self, id):
        self._printOverrideError('deselectItem')

    def changePriceItem(self, id, priceMode):
        self._printOverrideError('changePriceItem')

    def as_getPurchaseDPS(self):
        return self.flashObject.as_getPurchaseDP() if self._isDAAPIInited() else None

    def as_setInitDataS(self, data):
        """
        :param data: Represented by InitBuyWindowVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setTotalDataS(self, data):
        """
        :param data: Represented by PurchasesTotalVO (AS)
        """
        return self.flashObject.as_setTotalData(data) if self._isDAAPIInited() else None

    def as_setBuyBtnEnabledS(self, isEnabled):
        return self.flashObject.as_setBuyBtnEnabled(isEnabled) if self._isDAAPIInited() else None
