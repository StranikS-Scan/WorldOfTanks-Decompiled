# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBrowserScreenMeta.py
from gui.Scaleform.daapi.view.lobby.hangar.BrowserView import BrowserView

class EventBrowserScreenMeta(BrowserView):

    def as_setBrowserPaddingS(self, value):
        return self.flashObject.as_setBrowserPadding(value) if self._isDAAPIInited() else None
