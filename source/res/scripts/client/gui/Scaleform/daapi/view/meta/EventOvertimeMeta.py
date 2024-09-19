# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventOvertimeMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventOvertimeMeta(BaseDAAPIComponent):

    def as_updateOvertimeTimerS(self, value):
        return self.flashObject.as_updateOvertimeTimer(value) if self._isDAAPIInited() else None

    def as_getOvertimeInfoS(self, isBoss, isLowQuality):
        return self.flashObject.as_getOvertimeInfo(isBoss, isLowQuality) if self._isDAAPIInited() else None
