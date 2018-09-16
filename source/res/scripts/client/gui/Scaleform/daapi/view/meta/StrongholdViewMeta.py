# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StrongholdViewMeta.py
from gui.Scaleform.framework.entities.View import View

class StrongholdViewMeta(View):

    def onEscapePress(self):
        self._printOverrideError('onEscapePress')

    def onFocusChange(self, hasFocus):
        self._printOverrideError('onFocusChange')

    def viewSize(self, width, height):
        self._printOverrideError('viewSize')

    def as_loadBrowserS(self):
        return self.flashObject.as_loadBrowser() if self._isDAAPIInited() else None
