# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FootballOvertimeTimerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FootballOvertimeTimerMeta(BaseDAAPIComponent):

    def as_setTimerS(self, minutes, seconds):
        return self.flashObject.as_setTimer(minutes, seconds) if self._isDAAPIInited() else None

    def as_setTextS(self, dataVO):
        return self.flashObject.as_setText(dataVO) if self._isDAAPIInited() else None

    def as_setVisibilityS(self, value):
        return self.flashObject.as_setVisibility(value) if self._isDAAPIInited() else None
