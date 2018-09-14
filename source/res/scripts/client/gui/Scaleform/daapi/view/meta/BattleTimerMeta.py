# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleTimerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleTimerMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def as_setTotalTimeS(self, minutes, seconds):
        """
        :param minutes:
        :param seconds:
        :return :
        """
        return self.flashObject.as_setTotalTime(minutes, seconds) if self._isDAAPIInited() else None

    def as_setColorS(self, criticalColor):
        """
        :param criticalColor:
        :return :
        """
        return self.flashObject.as_setColor(criticalColor) if self._isDAAPIInited() else None

    def as_showBattleTimerS(self, show):
        """
        :param show:
        :return :
        """
        return self.flashObject.as_showBattleTimer(show) if self._isDAAPIInited() else None
