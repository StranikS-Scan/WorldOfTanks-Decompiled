# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LoginQueueWindowMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class LoginQueueWindowMeta(AbstractWindowView):

    def onCancelClick(self):
        self._printOverrideError('onCancelClick')

    def onAutoLoginClick(self):
        self._printOverrideError('onAutoLoginClick')

    def as_setTitleS(self, title):
        return self.flashObject.as_setTitle(title) if self._isDAAPIInited() else None

    def as_setMessageS(self, message):
        return self.flashObject.as_setMessage(message) if self._isDAAPIInited() else None

    def as_setCancelLabelS(self, cancelLabel):
        return self.flashObject.as_setCancelLabel(cancelLabel) if self._isDAAPIInited() else None

    def as_showAutoLoginBtnS(self, value):
        return self.flashObject.as_showAutoLoginBtn(value) if self._isDAAPIInited() else None
