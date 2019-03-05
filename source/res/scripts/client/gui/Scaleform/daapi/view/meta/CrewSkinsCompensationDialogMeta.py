# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CrewSkinsCompensationDialogMeta.py
from gui.Scaleform.daapi.view.dialogs.SimpleDialog import SimpleDialog

class CrewSkinsCompensationDialogMeta(SimpleDialog):

    def as_setListS(self, data):
        return self.flashObject.as_setList(data) if self._isDAAPIInited() else None

    def as_setMessagePriceS(self, dialogData):
        return self.flashObject.as_setMessagePrice(dialogData) if self._isDAAPIInited() else None

    def as_setPriceLabelS(self, label):
        return self.flashObject.as_setPriceLabel(label) if self._isDAAPIInited() else None

    def as_setOperationAllowedS(self, isAllowed):
        return self.flashObject.as_setOperationAllowed(isAllowed) if self._isDAAPIInited() else None
