# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PvePrimaryObjectiveMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PvePrimaryObjectiveMeta(BaseDAAPIComponent):

    def as_showMessageS(self, value):
        return self.flashObject.as_showMessage(value) if self._isDAAPIInited() else None

    def as_hideMessageS(self):
        return self.flashObject.as_hideMessage() if self._isDAAPIInited() else None

    def as_playFxS(self, value, loop):
        return self.flashObject.as_playFx(value, loop) if self._isDAAPIInited() else None

    def as_setHintStateS(self, value):
        return self.flashObject.as_setHintState(value) if self._isDAAPIInited() else None

    def as_setTimerBackgroundS(self, value):
        return self.flashObject.as_setTimerBackground(value) if self._isDAAPIInited() else None

    def as_setTimerStateS(self, state):
        return self.flashObject.as_setTimerState(state) if self._isDAAPIInited() else None

    def as_updateTimeS(self, value):
        return self.flashObject.as_updateTime(value) if self._isDAAPIInited() else None

    def as_updateProgressBarS(self, value, vis):
        return self.flashObject.as_updateProgressBar(value, vis) if self._isDAAPIInited() else None

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_showResultS(self, isWin, icon, header):
        return self.flashObject.as_showResult(isWin, icon, header) if self._isDAAPIInited() else None

    def as_hideResultS(self):
        return self.flashObject.as_hideResult() if self._isDAAPIInited() else None
