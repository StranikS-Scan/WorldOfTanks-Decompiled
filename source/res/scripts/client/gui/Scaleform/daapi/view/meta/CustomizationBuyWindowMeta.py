# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationBuyWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class CustomizationBuyWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def buy(self):
        """
        :return :
        """
        self._printOverrideError('buy')

    def selectItem(self, id):
        """
        :param id:
        :return :
        """
        self._printOverrideError('selectItem')

    def deselectItem(self, id):
        """
        :param id:
        :return :
        """
        self._printOverrideError('deselectItem')

    def changePriceItem(self, id, priceMode):
        """
        :param id:
        :param priceMode:
        :return :
        """
        self._printOverrideError('changePriceItem')

    def as_getPurchaseDPS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getPurchaseDP() if self._isDAAPIInited() else None

    def as_setInitDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setTotalDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setTotalData(data) if self._isDAAPIInited() else None
