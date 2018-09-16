# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DestroyTimersPanelMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class DestroyTimersPanelMeta(BaseDAAPIComponent):

    def as_showS(self, timerTypeID, timerViewTypeID, isBubble):
        return self.flashObject.as_show(timerTypeID, timerViewTypeID, isBubble) if self._isDAAPIInited() else None

    def as_showStunS(self, totalSeconds, currentTime):
        return self.flashObject.as_showStun(totalSeconds, currentTime) if self._isDAAPIInited() else None

    def as_hideS(self, timerTypeID):
        return self.flashObject.as_hide(timerTypeID) if self._isDAAPIInited() else None

    def as_hideStunS(self):
        return self.flashObject.as_hideStun() if self._isDAAPIInited() else None

    def as_setTimeInSecondsS(self, timerTypeID, totalSeconds, currentTime):
        return self.flashObject.as_setTimeInSeconds(timerTypeID, totalSeconds, currentTime) if self._isDAAPIInited() else None

    def as_setTimeSnapshotS(self, timerTypeID, totalSeconds, timeLeft):
        return self.flashObject.as_setTimeSnapshot(timerTypeID, totalSeconds, timeLeft) if self._isDAAPIInited() else None

    def as_setStunTimeSnapshotS(self, totalSeconds, timeLeft):
        return self.flashObject.as_setStunTimeSnapshot(totalSeconds, timeLeft) if self._isDAAPIInited() else None

    def as_setSpeedS(self, speed):
        return self.flashObject.as_setSpeed(speed) if self._isDAAPIInited() else None

    def as_turnOnStackViewS(self, value):
        return self.flashObject.as_turnOnStackView(value) if self._isDAAPIInited() else None
