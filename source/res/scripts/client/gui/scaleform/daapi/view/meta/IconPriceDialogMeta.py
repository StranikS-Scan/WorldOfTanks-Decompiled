# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/IconPriceDialogMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.daapi.view.dialogs.IconDialog import IconDialog

class IconPriceDialogMeta(IconDialog):

    def as_setMessagePriceS(self, dialogData):
        """
        :param dialogData: Represented by IconPriceDialogVO (AS)
        """
        return self.flashObject.as_setMessagePrice(dialogData) if self._isDAAPIInited() else None

    def as_setPriceLabelS(self, label):
        return self.flashObject.as_setPriceLabel(label) if self._isDAAPIInited() else None

    def as_setOperationAllowedS(self, isAllowed):
        return self.flashObject.as_setOperationAllowed(isAllowed) if self._isDAAPIInited() else None
