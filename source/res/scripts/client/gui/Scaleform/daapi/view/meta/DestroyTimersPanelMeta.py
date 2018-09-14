# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DestroyTimersPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class DestroyTimersPanelMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def as_showS(self, timerTypeID, timerViewTypeID):
        """
        :param timerTypeID:
        :param timerViewTypeID:
        :return :
        """
        return self.flashObject.as_show(timerTypeID, timerViewTypeID) if self._isDAAPIInited() else None

    def as_hideS(self, timerTypeID):
        """
        :param timerTypeID:
        :return :
        """
        return self.flashObject.as_hide(timerTypeID) if self._isDAAPIInited() else None

    def as_setTimeInSecondsS(self, timerTypeID, totalSeconds, currentTime):
        """
        :param timerTypeID:
        :param totalSeconds:
        :param currentTime:
        :return :
        """
        return self.flashObject.as_setTimeInSeconds(timerTypeID, totalSeconds, currentTime) if self._isDAAPIInited() else None

    def as_setTimeSnapshotS(self, timerTypeID, totalSeconds, timeLeft):
        """
        :param timerTypeID:
        :param totalSeconds:
        :param timeLeft:
        :return :
        """
        return self.flashObject.as_setTimeSnapshot(timerTypeID, totalSeconds, timeLeft) if self._isDAAPIInited() else None

    def as_setSpeedS(self, speed):
        """
        :param speed:
        :return :
        """
        return self.flashObject.as_setSpeed(speed) if self._isDAAPIInited() else None
