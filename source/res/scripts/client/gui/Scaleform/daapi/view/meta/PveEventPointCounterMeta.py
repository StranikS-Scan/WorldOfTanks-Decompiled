# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PveEventPointCounterMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PveEventPointCounterMeta(BaseDAAPIComponent):

    def as_updateCountS(self, count, reasonType):
        return self.flashObject.as_updateCount(count, reasonType) if self._isDAAPIInited() else None

    def as_enableAnimationS(self, value=True):
        return self.flashObject.as_enableAnimation(value) if self._isDAAPIInited() else None
