# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BrowserViewStackExPaddingMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BrowserViewStackExPaddingMeta(BaseDAAPIComponent):

    def setViewSize(self, width, height):
        self._printOverrideError('setViewSize')

    def as_setAllowWaitingS(self, value, startImmediately):
        return self.flashObject.as_setAllowWaiting(value, startImmediately) if self._isDAAPIInited() else None

    def as_setWaitingMessageS(self, value):
        return self.flashObject.as_setWaitingMessage(value) if self._isDAAPIInited() else None

    def as_createBrowserViewS(self):
        return self.flashObject.as_createBrowserView() if self._isDAAPIInited() else None
