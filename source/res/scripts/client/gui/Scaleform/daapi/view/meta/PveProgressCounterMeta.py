# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PveProgressCounterMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PveProgressCounterMeta(BaseDAAPIComponent):

    def as_setDataS(self, icon, title, isAnimated=True):
        return self.flashObject.as_setData(icon, title, isAnimated) if self._isDAAPIInited() else None
