# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WaitingViewMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class WaitingViewMeta(DAAPIModule):

    def showS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.show(data)

    def hideS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.hide(data)
