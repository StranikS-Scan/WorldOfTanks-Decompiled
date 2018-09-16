# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProgressTimersPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ProgressTimersPanelMeta(BaseDAAPIComponent):

    def as_setLocalizedDataS(self, type, data):
        return self.flashObject.as_setLocalizedData(type, data) if self._isDAAPIInited() else None

    def as_showS(self, timerTypeID, state, id):
        return self.flashObject.as_show(timerTypeID, state, id) if self._isDAAPIInited() else None

    def as_hideS(self):
        return self.flashObject.as_hide() if self._isDAAPIInited() else None

    def as_setStateS(self, state):
        return self.flashObject.as_setState(state) if self._isDAAPIInited() else None

    def as_setTimeStringS(self, cooldownTime):
        return self.flashObject.as_setTimeString(cooldownTime) if self._isDAAPIInited() else None

    def as_setProgressValueS(self, progress):
        return self.flashObject.as_setProgressValue(progress) if self._isDAAPIInited() else None
