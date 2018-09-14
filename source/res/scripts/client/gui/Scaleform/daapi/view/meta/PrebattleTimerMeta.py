# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PrebattleTimerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PrebattleTimerMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def as_setTimerS(self, totalTime):
        """
        :param totalTime:
        :return :
        """
        return self.flashObject.as_setTimer(totalTime) if self._isDAAPIInited() else None

    def as_setMessageS(self, msg):
        """
        :param msg:
        :return :
        """
        return self.flashObject.as_setMessage(msg) if self._isDAAPIInited() else None

    def as_hideTimerS(self):
        """
        :return :
        """
        return self.flashObject.as_hideTimer() if self._isDAAPIInited() else None

    def as_hideAllS(self, speed):
        """
        :param speed:
        :return :
        """
        return self.flashObject.as_hideAll(speed) if self._isDAAPIInited() else None

    def as_setWinConditionTextS(self, msg):
        """
        :param msg:
        :return :
        """
        return self.flashObject.as_setWinConditionText(msg) if self._isDAAPIInited() else None
