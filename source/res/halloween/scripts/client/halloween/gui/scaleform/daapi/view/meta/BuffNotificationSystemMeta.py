# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/meta/BuffNotificationSystemMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BuffNotificationSystemMeta(BaseDAAPIComponent):

    def onFadeOutFinished(self):
        self._printOverrideError('onFadeOutFinished')

    def as_showBuffNotificationS(self, data):
        return self.flashObject.as_showBuffNotification(data) if self._isDAAPIInited() else None

    def as_hideBuffNotificationS(self):
        return self.flashObject.as_hideBuffNotification() if self._isDAAPIInited() else None

    def as_cancelFadeOutS(self):
        return self.flashObject.as_cancelFadeOut() if self._isDAAPIInited() else None
