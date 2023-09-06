# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/meta/IntroVideoMeta.py
from gui.Scaleform.framework.entities.View import View

class IntroVideoMeta(View):

    def onVideoStarted(self):
        self._printOverrideError('onVideoStarted')

    def onVideoComplete(self):
        self._printOverrideError('onVideoComplete')

    def onSkipButtonVisible(self):
        self._printOverrideError('onSkipButtonVisible')

    def onSkipButtonClicked(self):
        self._printOverrideError('onSkipButtonClicked')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setCurrentSubtitleS(self, text):
        return self.flashObject.as_setCurrentSubtitle(text) if self._isDAAPIInited() else None

    def as_loadedS(self):
        return self.flashObject.as_loaded() if self._isDAAPIInited() else None

    def as_pausePlaybackS(self):
        return self.flashObject.as_pausePlayback() if self._isDAAPIInited() else None

    def as_resumePlaybackS(self):
        return self.flashObject.as_resumePlayback() if self._isDAAPIInited() else None

    def as_handleKeydownS(self):
        return self.flashObject.as_handleKeydown() if self._isDAAPIInited() else None
