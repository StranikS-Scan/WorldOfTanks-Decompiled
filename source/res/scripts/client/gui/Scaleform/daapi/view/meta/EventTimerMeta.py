# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventTimerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventTimerMeta(BaseDAAPIComponent):

    def as_updateTimeS(self, value):
        return self.flashObject.as_updateTime(value) if self._isDAAPIInited() else None

    def as_setTimerStateS(self, state):
        return self.flashObject.as_setTimerState(state) if self._isDAAPIInited() else None

    def as_playFxS(self):
        return self.flashObject.as_playFx() if self._isDAAPIInited() else None

    def as_updateTitleS(self, value):
        return self.flashObject.as_updateTitle(value) if self._isDAAPIInited() else None
