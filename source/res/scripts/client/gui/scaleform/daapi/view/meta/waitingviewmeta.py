# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WaitingViewMeta.py
from gui.Scaleform.framework.entities.View import View

class WaitingViewMeta(View):

    def showS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.show(data)

    def hideS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.hide(data)
