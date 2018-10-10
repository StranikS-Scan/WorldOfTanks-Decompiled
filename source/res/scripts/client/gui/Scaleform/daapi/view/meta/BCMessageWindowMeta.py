# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCMessageWindowMeta.py
from tutorial.gui.Scaleform.pop_ups import TutorialDialog

class BCMessageWindowMeta(TutorialDialog):

    def onMessageRemoved(self):
        self._printOverrideError('onMessageRemoved')

    def onMessageAppear(self, rendrerer):
        self._printOverrideError('onMessageAppear')

    def onMessageDisappear(self, rendrerer):
        self._printOverrideError('onMessageDisappear')

    def onMessageButtonClicked(self):
        self._printOverrideError('onMessageButtonClicked')

    def as_setMessageDataS(self, value):
        return self.flashObject.as_setMessageData(value) if self._isDAAPIInited() else None
