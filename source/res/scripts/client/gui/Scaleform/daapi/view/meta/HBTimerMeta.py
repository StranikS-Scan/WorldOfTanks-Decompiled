# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HBTimerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class HBTimerMeta(BaseDAAPIComponent):

    def as_updateTimeS(self, value):
        return self.flashObject.as_updateTime(value) if self._isDAAPIInited() else None

    def as_showMessageS(self, value):
        return self.flashObject.as_showMessage(value) if self._isDAAPIInited() else None

    def as_hideMessageS(self):
        return self.flashObject.as_hideMessage() if self._isDAAPIInited() else None

    def as_setTimerStateS(self, state):
        return self.flashObject.as_setTimerState(state) if self._isDAAPIInited() else None

    def as_setTimerBackgroundS(self, value):
        return self.flashObject.as_setTimerBackground(value) if self._isDAAPIInited() else None

    def as_setHintStateS(self, value):
        return self.flashObject.as_setHintState(value) if self._isDAAPIInited() else None

    def as_playFxS(self, value, loop):
        return self.flashObject.as_playFx(value, loop) if self._isDAAPIInited() else None

    def as_updateTitleS(self, value):
        return self.flashObject.as_updateTitle(value) if self._isDAAPIInited() else None

    def as_updateObjectiveS(self, value):
        return self.flashObject.as_updateObjective(value) if self._isDAAPIInited() else None

    def as_updateObjectiveBigS(self, value):
        return self.flashObject.as_updateObjectiveBig(value) if self._isDAAPIInited() else None

    def as_updateProgressBarS(self, value, vis):
        return self.flashObject.as_updateProgressBar(value, vis) if self._isDAAPIInited() else None
