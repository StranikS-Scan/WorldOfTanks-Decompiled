# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationStyleInfoMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CustomizationStyleInfoMeta(BaseDAAPIComponent):

    def onClose(self):
        self._printOverrideError('onClose')

    def onApply(self):
        self._printOverrideError('onApply')

    def onWidthUpdated(self, x, width, height):
        self._printOverrideError('onWidthUpdated')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_buttonUpdateS(self, data):
        return self.flashObject.as_buttonUpdate(data) if self._isDAAPIInited() else None

    def as_setBackgroundAlphaS(self, alpha):
        return self.flashObject.as_setBackgroundAlpha(alpha) if self._isDAAPIInited() else None

    def as_showS(self):
        return self.flashObject.as_show() if self._isDAAPIInited() else None

    def as_hideS(self):
        return self.flashObject.as_hide() if self._isDAAPIInited() else None
