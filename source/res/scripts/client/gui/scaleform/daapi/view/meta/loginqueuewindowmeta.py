# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LoginQueueWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class LoginQueueWindowMeta(DAAPIModule):

    def onCancelClick(self):
        self._printOverrideError('onCancelClick')

    def as_setTitleS(self, title):
        if self._isDAAPIInited():
            return self.flashObject.as_setTitle(title)

    def as_setMessageS(self, message):
        if self._isDAAPIInited():
            return self.flashObject.as_setMessage(message)

    def as_setCancelLabelS(self, cancelLabel):
        if self._isDAAPIInited():
            return self.flashObject.as_setCancelLabel(cancelLabel)
