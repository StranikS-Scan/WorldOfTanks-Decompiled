# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BossLocationMarkerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BossLocationMarkerMeta(BaseDAAPIComponent):

    def as_hideS(self):
        return self.flashObject.as_hide() if self._isDAAPIInited() else None

    def as_showS(self, onLeft):
        return self.flashObject.as_show(onLeft) if self._isDAAPIInited() else None

    def as_updateDistanceS(self, val):
        return self.flashObject.as_updateDistance(val) if self._isDAAPIInited() else None
