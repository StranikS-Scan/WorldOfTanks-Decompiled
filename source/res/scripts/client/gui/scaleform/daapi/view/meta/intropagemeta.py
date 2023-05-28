# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/IntroPageMeta.py
from gui.Scaleform.framework.entities.View import View

class IntroPageMeta(View):

    def stopVideo(self):
        self._printOverrideError('stopVideo')

    def handleError(self, data):
        self._printOverrideError('handleError')

    def tweenComplete(self):
        self._printOverrideError('tweenComplete')

    def videoStarted(self):
        self._printOverrideError('videoStarted')

    def as_playVideoS(self, data):
        return self.flashObject.as_playVideo(data) if self._isDAAPIInited() else None

    def as_fadeOutS(self, time):
        return self.flashObject.as_fadeOut(time) if self._isDAAPIInited() else None
