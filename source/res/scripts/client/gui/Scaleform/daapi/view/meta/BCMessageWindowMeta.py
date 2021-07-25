# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCMessageWindowMeta.py
from tutorial.gui.Scaleform.pop_ups import TutorialDialog

class BCMessageWindowMeta(TutorialDialog):

    def onMessageRemoved(self):
        self._printOverrideError('onMessageRemoved')

    def onMessageAppear(self, rendrerer):
        self._printOverrideError('onMessageAppear')

    def onMessageDisappear(self, rendrerer, animation):
        self._printOverrideError('onMessageDisappear')

    def onMessageExecuted(self, rendrerer):
        self._printOverrideError('onMessageExecuted')

    def onMessageButtonClicked(self):
        self._printOverrideError('onMessageButtonClicked')

    def onMessageAnimationStopped(self, animation):
        self._printOverrideError('onMessageAnimationStopped')

    def onMessageAnimationStarted(self, animation):
        self._printOverrideError('onMessageAnimationStarted')

    def hideBlur(self):
        self._printOverrideError('hideBlur')

    def as_setMessageDataS(self, value):
        return self.flashObject.as_setMessageData(value) if self._isDAAPIInited() else None

    def as_blurOtherWindowsS(self, layer):
        return self.flashObject.as_blurOtherWindows(layer) if self._isDAAPIInited() else None
