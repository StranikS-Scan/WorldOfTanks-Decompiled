# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MissionsMarathonViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class MissionsMarathonViewMeta(BaseDAAPIComponent):

    def viewSize(self, width, height):
        self._printOverrideError('viewSize')

    def as_loadBrowserS(self):
        return self.flashObject.as_loadBrowser() if self._isDAAPIInited() else None

    def as_setUnboundInjVisibleS(self, value):
        return self.flashObject.as_setUnboundInjVisible(value) if self._isDAAPIInited() else None
