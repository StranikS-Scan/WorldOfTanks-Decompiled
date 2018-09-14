# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DestroyTimersPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class DestroyTimersPanelMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def as_showS(self, timerTypeID, timerViewTypeID):
        return self.flashObject.as_show(timerTypeID, timerViewTypeID) if self._isDAAPIInited() else None

    def as_hideS(self, timerTypeID):
        return self.flashObject.as_hide(timerTypeID) if self._isDAAPIInited() else None

    def as_setTimeInSecondsS(self, timerTypeID, totalSeconds, currentTime):
        return self.flashObject.as_setTimeInSeconds(timerTypeID, totalSeconds, currentTime) if self._isDAAPIInited() else None

    def as_setTimeSnapshotS(self, timerTypeID, totalSeconds, timeLeft):
        return self.flashObject.as_setTimeSnapshot(timerTypeID, totalSeconds, timeLeft) if self._isDAAPIInited() else None

    def as_setSpeedS(self, speed):
        return self.flashObject.as_setSpeed(speed) if self._isDAAPIInited() else None
