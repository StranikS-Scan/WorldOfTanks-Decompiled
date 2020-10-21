# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/subtitles/subtitles.py
import BigWorld
from account_helpers.AccountSettings import AccountSettings, SUBTITLES
from gui.Scaleform.framework.entities.View import View

class SubtitlesBase(View):
    __STANDARD_SUBTITLE_DURATION_SEC = 3.0
    __DURATION_ON_TICK = 0.5

    def __init__(self, ctx=None):
        super(SubtitlesBase, self).__init__(ctx)
        self._content = ctx
        self.__subtitlesCallback = None
        self.__wasShown = False
        self.__totalTime = 0
        self.__currSound = {}
        return

    def _populate(self):
        super(SubtitlesBase, self)._populate()
        self.playSound()

    def _dispose(self):
        self.stopSound()
        super(SubtitlesBase, self)._dispose()

    def playSound(self):
        self.stopSound()
        if not self._content.get('voiceovers', False):
            self.onWindowClose()
            return
        self.__currSound = self._content['voiceovers'].pop(0)
        if self.__currSound.get('voiceover', ''):
            self.soundManager.playSound(self.__currSound['voiceover'])
            if self.__currSound.get('subtitle', '') and AccountSettings.getSettings(SUBTITLES):
                self.__subtitlesCallback = BigWorld.callback(self.__DURATION_ON_TICK, self.__onTick)

    def stopSound(self):
        if self.__subtitlesCallback is not None:
            BigWorld.cancelCallback(self.__subtitlesCallback)
            self.__subtitlesCallback = None
        self._hideSubtitles()
        if self.__currSound.get('voiceover', ''):
            self.soundManager.stopSound(self.__currSound['voiceover'])
        self.__currSound = {}
        return

    def __onTick(self):
        if self.__subtitlesCallback is not None:
            BigWorld.cancelCallback(self.__subtitlesCallback)
            self.__subtitlesCallback = None
            isSoundPlaying = self.soundManager.isSoundPlaying(self.__currSound['voiceover'])
            if not isSoundPlaying:
                if self.__wasShown or self.__totalTime > self.__STANDARD_SUBTITLE_DURATION_SEC:
                    self.playSound()
                    return
            elif not self.__wasShown:
                self._showSubtitles()
            self.__totalTime += self.__DURATION_ON_TICK
            self.__subtitlesCallback = BigWorld.callback(self.__DURATION_ON_TICK, self.__onTick)
        return

    def _showSubtitles(self):
        self.__wasShown = True
        self._asShowSubtitle(self.__currSound['subtitle'])

    def _hideSubtitles(self):
        self.__totalTime = 0
        self.__wasShown = False
        self._asHideSubtitle()

    def onWindowClose(self):
        raise NotImplementedError

    def _asShowSubtitle(self, subtitle):
        raise NotImplementedError

    def _asHideSubtitle(self):
        raise NotImplementedError
