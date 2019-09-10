# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicDestroyTimersPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.destroy_timers_panel import DestroyTimersPanel

class EpicDestroyTimersPanelMeta(DestroyTimersPanel):

    def as_showAdditionalTimerS(self, timerTypeID, state):
        return self.flashObject.as_showAdditionalTimer(timerTypeID, state) if self._isDAAPIInited() else None

    def as_hideAdditionalTimerS(self, timerTypeID):
        return self.flashObject.as_hideAdditionalTimer(timerTypeID) if self._isDAAPIInited() else None

    def as_setAdditionalTimerStateS(self, timerTypeID, state):
        return self.flashObject.as_setAdditionalTimerState(timerTypeID, state) if self._isDAAPIInited() else None

    def as_setAdditionalTimerTimeStringS(self, timerTypeID, cooldownTime):
        return self.flashObject.as_setAdditionalTimerTimeString(timerTypeID, cooldownTime) if self._isDAAPIInited() else None

    def as_setAdditionalTimerProgressValueS(self, timerTypeID, progress):
        return self.flashObject.as_setAdditionalTimerProgressValue(timerTypeID, progress) if self._isDAAPIInited() else None
