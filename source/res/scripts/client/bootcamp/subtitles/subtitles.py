# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/subtitles/subtitles.py
import BigWorld
from account_helpers.AccountSettings import AccountSettings, SUBTITLES
from gui.Scaleform.framework.entities.View import View
from bootcamp.BootCampEvents import g_bootcampEvents

class SoundMixin(View):

    def playSound(self, voiceover):
        self.soundManager.playSound(voiceover)

    def stopSound(self, voiceover):
        self.soundManager.stopSound(voiceover)

    def isSoundPlaying(self, voiceover):
        return self.soundManager.isSoundPlaying(voiceover)


class SoundSubtitleMixin(SoundMixin):
    __STANDARD_SUBTITLE_DURATION_SEC = 3.0
    __DURATION_ON_TICK = 0.5

    @property
    def userPrefOnSubtitles(self):
        return AccountSettings.getSettings(SUBTITLES)

    def __init__(self, ctx=None):
        super(SoundSubtitleMixin, self).__init__(ctx)
        self.__subtitlesCallback = None
        self.__voiceover = ''
        self.__subtitle = ''
        self.__showTime = 0
        self.__totalTime = 0
        return

    def playSound(self, voiceover):
        self.stopSound()
        self.__voiceover = voiceover['voiceover']
        self.__subtitle = voiceover['subtitle']
        if self.__voiceover:
            super(SoundSubtitleMixin, self).playSound(self.__voiceover)
            self.__subtitlesCallback = BigWorld.callback(self.__DURATION_ON_TICK, self.__onTick)
        else:
            g_bootcampEvents.onHideSubtitle()

    def stopSound(self, voiceover=''):
        if self.__subtitlesCallback is not None:
            BigWorld.cancelCallback(self.__subtitlesCallback)
            self.__subtitlesCallback = None
        super(SoundSubtitleMixin, self).stopSound(self.__voiceover)
        self._hideSubtitles()
        return

    def __onTick(self):
        if self.__subtitlesCallback is not None:
            BigWorld.cancelCallback(self.__subtitlesCallback)
            self.__subtitlesCallback = None
            if not self.__showTime:
                if super(SoundSubtitleMixin, self).isSoundPlaying(self.__voiceover):
                    self.__showTime += self.__DURATION_ON_TICK
                    self.__totalTime += self.__DURATION_ON_TICK
                    if self.__subtitle and self.userPrefOnSubtitles:
                        self._showSubtitles()
                    self.__subtitlesCallback = BigWorld.callback(self.__DURATION_ON_TICK, self.__onTick)
                elif self.__totalTime < self.__STANDARD_SUBTITLE_DURATION_SEC:
                    self.__totalTime += self.__DURATION_ON_TICK
                    self.__subtitlesCallback = BigWorld.callback(self.__DURATION_ON_TICK, self.__onTick)
                else:
                    self.stopSound()
                    g_bootcampEvents.onHideSubtitle()
            elif super(SoundSubtitleMixin, self).isSoundPlaying(self.__voiceover):
                self.__showTime += self.__DURATION_ON_TICK
                self.__totalTime += self.__DURATION_ON_TICK
                self.__subtitlesCallback = BigWorld.callback(self.__DURATION_ON_TICK, self.__onTick)
            else:
                self.stopSound()
                g_bootcampEvents.onHideSubtitle()
        return

    def _showSubtitles(self):
        self._asShowSubtitle(self.__subtitle)

    def _hideSubtitles(self):
        if self.__totalTime and self.__subtitle and self.userPrefOnSubtitles:
            self.__showTime = 0
            self.__totalTime = 0
            self._asHideSubtitle()

    def _asShowSubtitle(self, subtitle):
        raise NotImplementedError

    def _asHideSubtitle(self):
        raise NotImplementedError


class SubtitlesBase(SoundSubtitleMixin):

    def __init__(self, ctx=None):
        super(SubtitlesBase, self).__init__(ctx)
        self._content = ctx
        self.__subtitles = None
        return

    def _populate(self):
        super(SubtitlesBase, self)._populate()
        voiceovers = self._content['voiceovers']
        self.__subtitles = self.__onSubtitle(voiceovers)
        self.__subtitles.next()
        g_bootcampEvents.onHideSubtitle += self.__subtitles.next

    def _dispose(self):
        super(SubtitlesBase, self)._dispose()
        g_bootcampEvents.onHideSubtitle -= self.__subtitles.next
        self.__subtitles = None
        self.stopSound()
        return

    def __onSubtitle(self, voiceovers):
        voiceovers = voiceovers
        for voiceover in voiceovers:
            yield self.playSound(voiceover)

        yield self.destroy()
