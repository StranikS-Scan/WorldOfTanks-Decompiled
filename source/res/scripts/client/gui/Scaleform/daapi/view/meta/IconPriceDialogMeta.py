# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/IconPriceDialogMeta.py
from gui.Scaleform.daapi.view.dialogs.IconDialog import IconDialog

class IconPriceDialogMeta(IconDialog):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends IconDialog
    null
    """

    def as_setMessagePriceS(self, price, currency, actionPriceData):
        """
        :param price:
        :param currency:
        :param actionPriceData:
        :return :
        """
        return self.flashObject.as_setMessagePrice(price, currency, actionPriceData) if self._isDAAPIInited() else None

    def as_setPriceLabelS(self, label):
        """
        :param label:
        :return :
        """
        return self.flashObject.as_setPriceLabel(label) if self._isDAAPIInited() else None

    def as_setOperationAllowedS(self, isAllowed):
        """
        :param isAllowed:
        :return :
        """
        return self.flashObject.as_setOperationAllowed(isAllowed) if self._isDAAPIInited() else None
