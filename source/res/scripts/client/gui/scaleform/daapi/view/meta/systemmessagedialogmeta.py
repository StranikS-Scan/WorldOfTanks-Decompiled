# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SystemMessageDialogMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class SystemMessageDialogMeta(DAAPIModule):

    def as_setInitDataS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setInitData(value)

    def as_setMessageDataS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setMessageData(value)
