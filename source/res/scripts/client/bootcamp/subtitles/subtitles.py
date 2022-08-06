# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/subtitles/subtitles.py
import BigWorld
from account_helpers.AccountSettings import AccountSettings, SUBTITLES
from gui.Scaleform.framework.entities.View import View

class SubtitlesBase(View):
    _instance = None
    __STANDARD_DURATION_SEC = 3.0
    __DURATION_ON_TICK = 0.5

    def __new__(cls, *args, **kwargs):
        if cls._instance and not cls._instance.isDisposed():
            cls._instance.onWindowClose()
        cls._instance = View.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, ctx=None):
        super(SubtitlesBase, self).__init__(ctx)
        self._content = ctx
        self.__subtitlesCallback = None
        self.__currSound = {}
        return

    def _populate(self):
        super(SubtitlesBase, self)._populate()
        self.playSound()

    def _dispose(self):
        self.stopSound()
        self.__currSound = {}
        self._instance = None
        super(SubtitlesBase, self)._dispose()
        return

    def playSound(self):
        self.stopSound()
        if self._content.get('voiceovers', False):
            self.__currSound = self._content['voiceovers'].pop(0)
            if self.__currSound.get('voiceover', False):
                self.soundManager.playSound(self.__currSound['voiceover'])
                if self.__currSound.get('subtitle', False) and AccountSettings.getSettings(SUBTITLES):
                    self._asShowSubtitle(self.__currSound['subtitle'])
                self.__subtitlesCallback = BigWorld.callback(self.__STANDARD_DURATION_SEC, self._update)
                return
        self.onWindowClose()

    def stopSound(self):
        self.__clearCallback()
        if self.__currSound.get('subtitle', False):
            self._asHideSubtitle()
            if self.__currSound.get('voiceover', False):
                self.soundManager.stopSound(self.__currSound['voiceover'])

    def _update(self):
        self.__clearCallback()
        voiceover = self.__currSound.get('voiceover', '')
        if voiceover and self.soundManager.isSoundPlaying(voiceover):
            self.__subtitlesCallback = BigWorld.callback(self.__DURATION_ON_TICK, self._update)
            return
        self.playSound()

    def __clearCallback(self):
        if self.__subtitlesCallback is not None:
            BigWorld.cancelCallback(self.__subtitlesCallback)
            self.__subtitlesCallback = None
        return

    def onWindowClose(self):
        self.stopSound()

    def _asShowSubtitle(self, subtitle):
        raise NotImplementedError

    def _asHideSubtitle(self):
        raise NotImplementedError
