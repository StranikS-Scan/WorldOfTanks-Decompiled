# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BrowserMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class BrowserMeta(DAAPIModule):

    def browserAction(self, action):
        self._printOverrideError('browserAction')

    def browserMove(self, x, y, z):
        self._printOverrideError('browserMove')

    def browserDown(self, x, y, z):
        self._printOverrideError('browserDown')

    def browserUp(self, x, y, z):
        self._printOverrideError('browserUp')

    def browserFocusOut(self):
        self._printOverrideError('browserFocusOut')

    def onBrowserShow(self, needRefresh):
        self._printOverrideError('onBrowserShow')

    def onBrowserHide(self):
        self._printOverrideError('onBrowserHide')

    def as_loadingStartS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_loadingStart()

    def as_loadingStopS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_loadingStop()

    def as_configureS(self, title, showActionBtn):
        if self._isDAAPIInited():
            return self.flashObject.as_configure(title, showActionBtn)
