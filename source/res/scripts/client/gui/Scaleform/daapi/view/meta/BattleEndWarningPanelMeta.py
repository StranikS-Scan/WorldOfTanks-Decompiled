# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleEndWarningPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleEndWarningPanelMeta(BaseDAAPIComponent):
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

    def as_setTextInfoS(self, text):
        """
        :param text:
        :return :
        """
        return self.flashObject.as_setTextInfo(text) if self._isDAAPIInited() else None

    def as_setStateS(self, isShow):
        """
        :param isShow:
        :return :
        """
        return self.flashObject.as_setState(isShow) if self._isDAAPIInited() else None
