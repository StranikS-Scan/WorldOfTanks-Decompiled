# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCOutroVideoPageMeta.py
from gui.Scaleform.framework.entities.View import View

class BCOutroVideoPageMeta(View):

    def videoFinished(self):
        self._printOverrideError('videoFinished')

    def handleError(self, data):
        self._printOverrideError('handleError')

    def as_playVideoS(self, data):
        return self.flashObject.as_playVideo(data) if self._isDAAPIInited() else None

    def as_pausePlaybackS(self):
        return self.flashObject.as_pausePlayback() if self._isDAAPIInited() else None

    def as_resumePlaybackS(self):
        return self.flashObject.as_resumePlayback() if self._isDAAPIInited() else None
