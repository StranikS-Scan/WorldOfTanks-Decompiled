# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PveObjectsWidgetMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PveObjectsWidgetMeta(BaseDAAPIComponent):

    def as_addObjectS(self, data):
        return self.flashObject.as_addObject(data) if self._isDAAPIInited() else None

    def as_removeObjectS(self, id, state):
        return self.flashObject.as_removeObject(id, state) if self._isDAAPIInited() else None

    def as_setProgressBarValueS(self, id, value):
        return self.flashObject.as_setProgressBarValue(id, value) if self._isDAAPIInited() else None

    def as_updateTimeS(self, id, value, isWarning):
        return self.flashObject.as_updateTime(id, value, isWarning) if self._isDAAPIInited() else None

    def as_setAlarmS(self, id, isAlarm):
        return self.flashObject.as_setAlarm(id, isAlarm) if self._isDAAPIInited() else None

    def as_setTitleS(self, id, title):
        return self.flashObject.as_setTitle(id, title) if self._isDAAPIInited() else None
