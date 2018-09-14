# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RepairPointTimerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class RepairPointTimerMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def as_setStateS(self, state):
        return self.flashObject.as_setState(state) if self._isDAAPIInited() else None

    def as_setTimeInSecondsS(self, seconds):
        return self.flashObject.as_setTimeInSeconds(seconds) if self._isDAAPIInited() else None

    def as_setTimeStringS(self, timeStr):
        return self.flashObject.as_setTimeString(timeStr) if self._isDAAPIInited() else None

    def as_useActionScriptTimerS(self, isASTimer):
        return self.flashObject.as_useActionScriptTimer(isASTimer) if self._isDAAPIInited() else None

    def as_hideS(self):
        return self.flashObject.as_hide() if self._isDAAPIInited() else None
