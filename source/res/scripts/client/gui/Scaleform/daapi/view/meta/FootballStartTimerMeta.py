# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FootballStartTimerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FootballStartTimerMeta(BaseDAAPIComponent):

    def as_setVisibilityS(self, value):
        return self.flashObject.as_setVisibility(value) if self._isDAAPIInited() else None

    def as_setTextS(self, dataVO):
        return self.flashObject.as_setText(dataVO) if self._isDAAPIInited() else None

    def as_setTimerS(self, time):
        return self.flashObject.as_setTimer(time) if self._isDAAPIInited() else None
