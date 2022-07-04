# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MinimapGridMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class MinimapGridMeta(BaseDAAPIComponent):

    def setClick(self, x, y):
        self._printOverrideError('setClick')

    def as_clickEnabledS(self, value):
        return self.flashObject.as_clickEnabled(value) if self._isDAAPIInited() else None

    def as_addPointS(self, x, y):
        return self.flashObject.as_addPoint(x, y) if self._isDAAPIInited() else None

    def as_clearPointsS(self):
        return self.flashObject.as_clearPoints() if self._isDAAPIInited() else None
