# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventPointCounterMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventPointCounterMeta(BaseDAAPIComponent):

    def as_updateCountS(self, count):
        return self.flashObject.as_updateCount(count) if self._isDAAPIInited() else None
