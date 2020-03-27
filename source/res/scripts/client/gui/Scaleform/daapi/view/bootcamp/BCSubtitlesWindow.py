# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCSubtitlesWindow.py
import BigWorld
from gui.Scaleform.daapi.view.meta.SubtitlesWindowMeta import SubtitlesWindowMeta
from account_helpers.AccountSettings import AccountSettings, SUBTITLES
from tutorial.gui.Scaleform.pop_ups import TutorialWindow
from bootcamp.BootCampEvents import g_bootcampEvents

def subtitleDecorator(function):

    def showSubtitle(*args):
        from tutorial.data.effects import HasTargetEffect, EFFECT_TYPE
        cls = args[0]
        if cls.content['voiceovers']:
            voiceover, subtitle = cls.content['voiceovers'].pop(0)
            if subtitle:
                effects = [HasTargetEffect(subtitle, EFFECT_TYPE.SHOW_WINDOW, None)]
                cls.tutorial.storeEffectsInQueue(effects, benefit=True, isGlobal=True)
                funcEffect = cls.tutorial.getFirstElementOfTop()
                funcEffect.triggerEffect()
            elif voiceover:
                cls.soundManager.playSound(voiceover)
        return

    def onCall(*args, **kwargs):
        showSubtitle(*args)
        return function(*args, **kwargs)

    return onCall


class TutorialWindowSound(TutorialWindow):

    def _stop(self):
        self._content.clear()
        for _, effect in self._gui.effects.iterEffects():
            if effect.isStillRunning(self.uniqueName):
                effect.stop(effectID=None)

        return

    def playSound(self, voiceover, subtitle=''):
        self.soundManager.playSound(voiceover)

    def stopSound(self, voiceover):
        self.soundManager.stopSound(voiceover)

    def isSoundPlaying(self, voiceover):
        return self.soundManager.isSoundPlaying(voiceover)

    def _asShowSubtitle(self, subtitle):
        raise NotImplementedError

    def _asHideSubtitle(self):
        raise NotImplementedError


class TutorialWindowSoundSubtitle(TutorialWindowSound):
    __STANDARD_SUBTITLE_DURATION_SEC = 3.0
    __DURATION_ON_TICK = 0.5

    @property
    def userPrefOnSubtitles(self):
        return AccountSettings.getSettings(SUBTITLES)

    def __init__(self, ctx=None):
        super(TutorialWindowSoundSubtitle, self).__init__(ctx)
        self.__subtitlesCallback = None
        self.__voiceover = ''
        self.__subtitle = ''
        self.__showTime = 0
        self.__totalTime = 0
        return

    def playSound(self, voiceover, subtitle=''):
        self.stopSound()
        self.__voiceover, self.__subtitle = voiceover, subtitle
        if self.__voiceover:
            super(TutorialWindowSoundSubtitle, self).playSound(self.__voiceover)
            self.__subtitlesCallback = BigWorld.callback(self.__DURATION_ON_TICK, self.__onTick)
        else:
            g_bootcampEvents.onHideSubtitle()

    def stopSound(self, voiceover=''):
        if self.__subtitlesCallback is not None:
            BigWorld.cancelCallback(self.__subtitlesCallback)
            self.__subtitlesCallback = None
        super(TutorialWindowSoundSubtitle, self).stopSound(self.__voiceover)
        self._hideSubtitles()
        return

    def __onTick(self):
        if self.__subtitlesCallback is not None:
            BigWorld.cancelCallback(self.__subtitlesCallback)
            self.__subtitlesCallback = None
            if not self.__showTime:
                if super(TutorialWindowSoundSubtitle, self).isSoundPlaying(self.__voiceover):
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
            elif super(TutorialWindowSoundSubtitle, self).isSoundPlaying(self.__voiceover):
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


class SubtitlesWindow(SubtitlesWindowMeta, TutorialWindowSoundSubtitle):

    def __init__(self, ctx=None):
        super(SubtitlesWindow, self).__init__(ctx)
        self.__subtitles = None
        return

    def _populate(self):
        super(SubtitlesWindow, self)._populate()
        voiceovers = self._content['voiceovers']
        self.__subtitles = self.__onSubtitle(voiceovers)
        self.__subtitles.next()
        g_bootcampEvents.onHideSubtitle += self.__subtitles.next

    def _dispose(self):
        super(SubtitlesWindow, self)._dispose()
        g_bootcampEvents.onHideSubtitle -= self.__subtitles.next
        self.__subtitles = None
        self.stopSound()
        return

    def _asShowSubtitle(self, subtitle):
        self.as_showSubtitleS(subtitle)

    def _asHideSubtitle(self):
        self.as_hideSubtitleS()

    def __onSubtitle(self, voiceovers):
        voiceovers = voiceovers
        for voiceover, subtitle in voiceovers:
            yield self.playSound(voiceover, subtitle)

        yield self.destroy()
