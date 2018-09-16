# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCMessageWindow.py
from gui.Scaleform.framework.entities.View import View

class BCMessageWindow(View):

    def onMessageRemoved(self):
        self._printOverrideError('onMessageRemoved')

    def as_setMessageDataS(self, value):
        return self.flashObject.as_setMessageData(value) if self._isDAAPIInited() else None
