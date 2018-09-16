# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedBattlesBrowserViewMeta.py
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class RankedBattlesBrowserViewMeta(WrapperViewMeta):

    def onEscapePress(self):
        self._printOverrideError('onEscapePress')

    def onCloseBtnClick(self):
        self._printOverrideError('onCloseBtnClick')

    def onFocusChange(self, hasFocus):
        self._printOverrideError('onFocusChange')

    def viewSize(self, width, height):
        self._printOverrideError('viewSize')

    def as_loadBrowserS(self):
        return self.flashObject.as_loadBrowser() if self._isDAAPIInited() else None
