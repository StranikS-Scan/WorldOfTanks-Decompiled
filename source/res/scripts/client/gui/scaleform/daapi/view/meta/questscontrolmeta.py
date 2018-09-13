# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsControlMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class QuestsControlMeta(DAAPIModule):

    def showQuestsWindow(self):
        self._printOverrideError('showQuestsWindow')

    def as_highlightControlS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_highlightControl()

    def as_resetControlS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_resetControl()
