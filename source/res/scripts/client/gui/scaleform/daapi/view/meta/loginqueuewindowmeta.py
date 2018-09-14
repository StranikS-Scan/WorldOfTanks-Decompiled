# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LoginQueueWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class LoginQueueWindowMeta(AbstractWindowView):

    def onCancelClick(self):
        self._printOverrideError('onCancelClick')

    def onAutoLoginClick(self):
        self._printOverrideError('onAutoLoginClick')

    def as_setTitleS(self, title):
        if self._isDAAPIInited():
            return self.flashObject.as_setTitle(title)

    def as_setMessageS(self, message):
        if self._isDAAPIInited():
            return self.flashObject.as_setMessage(message)

    def as_setCancelLabelS(self, cancelLabel):
        if self._isDAAPIInited():
            return self.flashObject.as_setCancelLabel(cancelLabel)

    def as_showAutoLoginBtnS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_showAutoLoginBtn(value)
