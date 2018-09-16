# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCTooltipsWindowMeta.py
from gui.Scaleform.framework.entities.View import View

class BCTooltipsWindowMeta(View):

    def animFinish(self):
        self._printOverrideError('animFinish')

    def as_setRotateTipVisibilityS(self, Visible):
        return self.flashObject.as_setRotateTipVisibility(Visible) if self._isDAAPIInited() else None

    def as_showHandlerS(self):
        return self.flashObject.as_showHandler() if self._isDAAPIInited() else None

    def as_completeHandlerS(self):
        return self.flashObject.as_completeHandler() if self._isDAAPIInited() else None

    def as_hideHandlerS(self):
        return self.flashObject.as_hideHandler() if self._isDAAPIInited() else None
