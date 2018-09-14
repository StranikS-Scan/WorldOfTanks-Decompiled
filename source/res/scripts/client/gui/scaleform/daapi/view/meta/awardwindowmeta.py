# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AwardWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class AwardWindowMeta(DAAPIModule):

    def onOKClick(self):
        self._printOverrideError('onOKClick')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
