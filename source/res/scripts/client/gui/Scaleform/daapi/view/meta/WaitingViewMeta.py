# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WaitingViewMeta.py
from gui.Scaleform.framework.entities.View import View

class WaitingViewMeta(View):

    def showS(self, data):
        return self.flashObject.show(data) if self._isDAAPIInited() else None

    def hideS(self, data):
        return self.flashObject.hide(data) if self._isDAAPIInited() else None
