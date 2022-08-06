# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BrowserMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BrowserMeta(BaseDAAPIComponent):

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

    def invalidateView(self):
        self._printOverrideError('invalidateView')

    def setBrowserSize(self, width, height, scale):
        self._printOverrideError('setBrowserSize')

    def as_loadBitmapS(self, url):
        return self.flashObject.as_loadBitmap(url) if self._isDAAPIInited() else None

    def as_resizeS(self, width, height):
        return self.flashObject.as_resize(width, height) if self._isDAAPIInited() else None

    def as_loadingStartS(self, showContentUnderWaiting):
        return self.flashObject.as_loadingStart(showContentUnderWaiting) if self._isDAAPIInited() else None

    def as_loadingStopS(self):
        return self.flashObject.as_loadingStop() if self._isDAAPIInited() else None

    def as_showServiceViewS(self, header, description):
        return self.flashObject.as_showServiceView(header, description) if self._isDAAPIInited() else None

    def as_hideServiceViewS(self):
        return self.flashObject.as_hideServiceView() if self._isDAAPIInited() else None

    def as_changeTitleS(self, title):
        return self.flashObject.as_changeTitle(title) if self._isDAAPIInited() else None
