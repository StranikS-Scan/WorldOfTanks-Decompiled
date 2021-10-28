# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBuffNotificationSystemMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventBuffNotificationSystemMeta(BaseDAAPIComponent):

    def as_showBuffNotificationS(self, data):
        return self.flashObject.as_showBuffNotification(data) if self._isDAAPIInited() else None

    def as_hideBuffNotificationS(self):
        return self.flashObject.as_hideBuffNotification() if self._isDAAPIInited() else None
