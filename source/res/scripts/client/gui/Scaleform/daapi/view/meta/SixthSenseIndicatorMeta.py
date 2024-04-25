# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SixthSenseIndicatorMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class SixthSenseIndicatorMeta(BaseDAAPIComponent):

    def as_showS(self):
        return self.flashObject.as_show() if self._isDAAPIInited() else None

    def as_hideS(self):
        return self.flashObject.as_hide() if self._isDAAPIInited() else None

    def as_setIsSmallS(self, value):
        return self.flashObject.as_setIsSmall(value) if self._isDAAPIInited() else None

    def as_setAlphaS(self, value):
        return self.flashObject.as_setAlpha(value) if self._isDAAPIInited() else None
