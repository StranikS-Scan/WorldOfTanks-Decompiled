# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsControlMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class QuestsControlMeta(DAAPIModule):

    def showQuestsWindow(self):
        self._printOverrideError('showQuestsWindow')

    def as_isShowAlertIconS(self, value, highlight):
        if self._isDAAPIInited():
            return self.flashObject.as_isShowAlertIcon(value, highlight)

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
