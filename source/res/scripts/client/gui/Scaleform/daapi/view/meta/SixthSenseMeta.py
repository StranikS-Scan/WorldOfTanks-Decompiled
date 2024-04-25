# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SixthSenseMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class SixthSenseMeta(BaseDAAPIComponent):

    def as_showS(self, immidiate):
        return self.flashObject.as_show(immidiate) if self._isDAAPIInited() else None

    def as_showIndicatorS(self):
        return self.flashObject.as_showIndicator() if self._isDAAPIInited() else None

    def as_hideS(self, immidiate):
        return self.flashObject.as_hide(immidiate) if self._isDAAPIInited() else None

    def as_setIsBigS(self, value):
        return self.flashObject.as_setIsBig(value) if self._isDAAPIInited() else None

    def as_setAlphaS(self, value):
        return self.flashObject.as_setAlpha(value) if self._isDAAPIInited() else None
