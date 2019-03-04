# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationStyleInfoMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CustomizationStyleInfoMeta(BaseDAAPIComponent):

    def onClose(self):
        self._printOverrideError('onClose')

    def onApply(self):
        self._printOverrideError('onApply')

    def as_setStyleInfoS(self, data):
        return self.flashObject.as_setStyleInfo(data) if self._isDAAPIInited() else None

    def as_setStylePriceS(self, data):
        return self.flashObject.as_setStylePrice(data) if self._isDAAPIInited() else None

    def as_showS(self):
        return self.flashObject.as_show() if self._isDAAPIInited() else None

    def as_hideS(self):
        return self.flashObject.as_hide() if self._isDAAPIInited() else None
