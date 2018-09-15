# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EvilEyeMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EvilEyeMeta(BaseDAAPIComponent):

    def as_showMainS(self):
        return self.flashObject.as_showMain() if self._isDAAPIInited() else None

    def as_showSecondaryS(self):
        return self.flashObject.as_showSecondary() if self._isDAAPIInited() else None

    def as_showNotificationS(self, msg):
        return self.flashObject.as_showNotification(msg) if self._isDAAPIInited() else None

    def as_setEyeLabelsS(self, data):
        """
        :param data: Represented by EvilEyeMessageVO (AS)
        """
        return self.flashObject.as_setEyeLabels(data) if self._isDAAPIInited() else None

    def as_hideAllNowS(self):
        return self.flashObject.as_hideAllNow() if self._isDAAPIInited() else None

    def as_hideMainS(self):
        return self.flashObject.as_hideMain() if self._isDAAPIInited() else None

    def as_hideSecondaryS(self):
        return self.flashObject.as_hideSecondary() if self._isDAAPIInited() else None

    def as_hideNotificationS(self):
        return self.flashObject.as_hideNotification() if self._isDAAPIInited() else None
