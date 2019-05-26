# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCIntroVideoPageMeta.py
from gui.Scaleform.framework.entities.View import View

class BCIntroVideoPageMeta(View):

    def videoStarted(self):
        self._printOverrideError('videoStarted')

    def videoFinished(self):
        self._printOverrideError('videoFinished')

    def goToBattle(self):
        self._printOverrideError('goToBattle')

    def skipBootcamp(self):
        self._printOverrideError('skipBootcamp')

    def handleError(self, data):
        self._printOverrideError('handleError')

    def as_playVideoS(self, data):
        return self.flashObject.as_playVideo(data) if self._isDAAPIInited() else None

    def as_updateProgressS(self, percent):
        return self.flashObject.as_updateProgress(percent) if self._isDAAPIInited() else None

    def as_loadedS(self):
        return self.flashObject.as_loaded() if self._isDAAPIInited() else None

    def as_showIntroPageS(self, value):
        return self.flashObject.as_showIntroPage(value) if self._isDAAPIInited() else None

    def as_pausePlaybackS(self):
        return self.flashObject.as_pausePlayback() if self._isDAAPIInited() else None

    def as_resumePlaybackS(self):
        return self.flashObject.as_resumePlayback() if self._isDAAPIInited() else None
