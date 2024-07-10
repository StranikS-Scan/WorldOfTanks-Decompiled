# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SixthSenseMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class SixthSenseMeta(BaseDAAPIComponent):

    def as_showS(self):
        return self.flashObject.as_show() if self._isDAAPIInited() else None

    def as_hideS(self, force):
        return self.flashObject.as_hide(force) if self._isDAAPIInited() else None
