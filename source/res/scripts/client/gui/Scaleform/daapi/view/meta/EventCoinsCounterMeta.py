# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventCoinsCounterMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventCoinsCounterMeta(BaseDAAPIComponent):

    def as_setCoinsCountS(self, value):
        return self.flashObject.as_setCoinsCount(value) if self._isDAAPIInited() else None

    def as_setCoinsTooltipS(self, value):
        return self.flashObject.as_setCoinsTooltip(value) if self._isDAAPIInited() else None
