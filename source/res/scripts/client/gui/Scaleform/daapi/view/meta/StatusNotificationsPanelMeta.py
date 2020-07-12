# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StatusNotificationsPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StatusNotificationsPanelMeta(BaseDAAPIComponent):

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setDataS(self, items):
        return self.flashObject.as_setData(items) if self._isDAAPIInited() else None

    def as_setVerticalOffsetS(self, offsetY):
        return self.flashObject.as_setVerticalOffset(offsetY) if self._isDAAPIInited() else None

    def as_setSpeedS(self, speed):
        return self.flashObject.as_setSpeed(speed) if self._isDAAPIInited() else None
