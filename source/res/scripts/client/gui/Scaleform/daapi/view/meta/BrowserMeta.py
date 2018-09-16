# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BrowserMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
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

    def setBrowserSize(self, width, height):
        self._printOverrideError('setBrowserSize')

    def as_loadingStartS(self):
        return self.flashObject.as_loadingStart() if self._isDAAPIInited() else None

    def as_loadingStopS(self):
        return self.flashObject.as_loadingStop() if self._isDAAPIInited() else None

    def as_showServiceViewS(self, header, description):
        return self.flashObject.as_showServiceView(header, description) if self._isDAAPIInited() else None

    def as_hideServiceViewS(self):
        return self.flashObject.as_hideServiceView() if self._isDAAPIInited() else None

    def as_changeTitleS(self, title):
        return self.flashObject.as_changeTitle(title) if self._isDAAPIInited() else None

    def as_showContextMenuS(self, type, context):
        return self.flashObject.as_showContextMenu(type, context) if self._isDAAPIInited() else None
