# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/meta/WhiteTigerOvertimeMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class WhiteTigerOvertimeMeta(BaseDAAPIComponent):

    def as_updateOvertimeTimerS(self, value):
        return self.flashObject.as_updateOvertimeTimer(value) if self._isDAAPIInited() else None

    def as_getOvertimeInfoS(self, isBoss, isLowQuality):
        return self.flashObject.as_getOvertimeInfo(isBoss, isLowQuality) if self._isDAAPIInited() else None
