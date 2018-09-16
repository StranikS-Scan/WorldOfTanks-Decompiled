# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleEndWarningPanelMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleEndWarningPanelMeta(BaseDAAPIComponent):

    def as_setTotalTimeS(self, minutes, seconds):
        return self.flashObject.as_setTotalTime(minutes, seconds) if self._isDAAPIInited() else None

    def as_setTextInfoS(self, text):
        return self.flashObject.as_setTextInfo(text) if self._isDAAPIInited() else None

    def as_setStateS(self, isShow):
        return self.flashObject.as_setState(isShow) if self._isDAAPIInited() else None
