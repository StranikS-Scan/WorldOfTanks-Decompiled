# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DestroyTimersPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class DestroyTimersPanelMeta(BaseDAAPIComponent):

    def as_showS(self, timerTypeID, timerViewTypeID, isBubble):
        return self.flashObject.as_show(timerTypeID, timerViewTypeID, isBubble) if self._isDAAPIInited() else None

    def as_hideS(self, timerTypeID):
        return self.flashObject.as_hide(timerTypeID) if self._isDAAPIInited() else None

    def as_setTimeInSecondsS(self, timerTypeID, totalSeconds, currentTime):
        return self.flashObject.as_setTimeInSeconds(timerTypeID, totalSeconds, currentTime) if self._isDAAPIInited() else None

    def as_setTimeSnapshotS(self, timerTypeID, totalSeconds, timeLeft):
        return self.flashObject.as_setTimeSnapshot(timerTypeID, totalSeconds, timeLeft) if self._isDAAPIInited() else None

    def as_setSpeedS(self, speed):
        return self.flashObject.as_setSpeed(speed) if self._isDAAPIInited() else None

    def as_turnOnStackViewS(self, value):
        return self.flashObject.as_turnOnStackView(value) if self._isDAAPIInited() else None

    def as_showSecondaryTimerS(self, secTimerID, totalSeconds, currentTime):
        return self.flashObject.as_showSecondaryTimer(secTimerID, totalSeconds, currentTime) if self._isDAAPIInited() else None

    def as_hideSecondaryTimerS(self, secTimerID):
        return self.flashObject.as_hideSecondaryTimer(secTimerID) if self._isDAAPIInited() else None

    def as_setSecondaryTimeSnapshotS(self, secTimerID, totalSeconds, timeLeft):
        return self.flashObject.as_setSecondaryTimeSnapshot(secTimerID, totalSeconds, timeLeft) if self._isDAAPIInited() else None

    def as_setSecondaryTimerTextS(self, secTimerID, text):
        return self.flashObject.as_setSecondaryTimerText(secTimerID, text) if self._isDAAPIInited() else None
