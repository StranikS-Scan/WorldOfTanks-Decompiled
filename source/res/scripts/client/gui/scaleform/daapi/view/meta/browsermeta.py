# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BrowserMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class BrowserMeta(AbstractWindowView):

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

    def as_configureS(self, isDefaultBrowser, title, showActionBtn, showCloseBtn):
        if self._isDAAPIInited():
            return self.flashObject.as_configure(isDefaultBrowser, title, showActionBtn, showCloseBtn)

    def as_setBrowserSizeS(self, width, height):
        if self._isDAAPIInited():
            return self.flashObject.as_setBrowserSize(width, height)

    def as_showServiceViewS(self, header, description):
        if self._isDAAPIInited():
            return self.flashObject.as_showServiceView(header, description)

    def as_hideServiceViewS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_hideServiceView()
