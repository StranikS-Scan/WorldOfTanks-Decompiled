# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PointsOfInterestNotificationPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PointsOfInterestNotificationPanelMeta(BaseDAAPIComponent):

    def as_addPoiStatusS(self, data):
        return self.flashObject.as_addPoiStatus(data) if self._isDAAPIInited() else None

    def as_updatePoiStatusS(self, id, status, isAlly):
        return self.flashObject.as_updatePoiStatus(id, status, isAlly) if self._isDAAPIInited() else None

    def as_updatePoiProgressS(self, id, progress):
        return self.flashObject.as_updatePoiProgress(id, progress) if self._isDAAPIInited() else None

    def as_addNotificationS(self, id, isAlly, message):
        return self.flashObject.as_addNotification(id, isAlly, message) if self._isDAAPIInited() else None

    def as_setReplaySpeedS(self, value=1):
        return self.flashObject.as_setReplaySpeed(value) if self._isDAAPIInited() else None
