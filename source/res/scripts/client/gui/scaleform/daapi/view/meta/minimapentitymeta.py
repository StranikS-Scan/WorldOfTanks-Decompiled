# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MinimapEntityMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class MinimapEntityMeta(BaseDAAPIComponent):

    def as_updatePointsS(self):
        return self.flashObject.as_updatePoints() if self._isDAAPIInited() else None
