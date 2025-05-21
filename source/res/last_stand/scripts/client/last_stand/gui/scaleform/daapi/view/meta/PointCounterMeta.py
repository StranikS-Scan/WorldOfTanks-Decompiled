# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/meta/PointCounterMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PointCounterMeta(BaseDAAPIComponent):

    def as_updateCountS(self, count, reasonType):
        return self.flashObject.as_updateCount(count, reasonType) if self._isDAAPIInited() else None

    def as_enableAnimationS(self, value=True):
        return self.flashObject.as_enableAnimation(value) if self._isDAAPIInited() else None

    def as_setSoulsCapS(self, value):
        return self.flashObject.as_setSoulsCap(value) if self._isDAAPIInited() else None
