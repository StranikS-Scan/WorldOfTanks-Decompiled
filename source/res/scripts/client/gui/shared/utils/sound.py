# Embedded file name: scripts/client/gui/shared/utils/sound.py
import BigWorld
import FMOD
import SoundGroups
from debug_utils import LOG_DEBUG

class Sound(object):

    def __init__(self, soundPath):
        self.__sndTick = None
        if FMOD.enabled:
            self.__sndTick = SoundGroups.g_instance.playSound2D(soundPath)
        self.__isPlaying = True
        self.stop()
        return

    @property
    def isPlaying(self):
        return self.__isPlaying

    @property
    def fmodSound(self):
        return self.__sndTick

    def play(self):
        if FMOD.enabled:
            self.stop()
            if self.__sndTick:
                self.__sndTick.play()
            self.__isPlaying = True

    def stop(self):
        if self.__sndTick:
            self.__sndTick.stop()
        self.__isPlaying = False


class SoundSequence(object):

    def __init__(self, sounds, beforePlayCB = None, afterPlayCB = None):
        raise sounds is not None or AssertionError
        self.__sounds = sounds
        self.__soundsIter = None
        self.__curPlayingSnd = None
        self.__beforePlayCB = beforePlayCB
        self.__afterPlayCB = afterPlayCB
        self.__bwCbID = None
        return

    def __del__(self):
        self.__beforePlayCB = None
        self.__afterPlayCB = None
        return

    @property
    def sounds(self):
        return self.__sounds

    def play(self):
        self.__playNextSound()

    def stop(self):
        self.__clear()

    def __notifyBeforePlay(self, snd):
        if self.__beforePlayCB is not None:
            self.__beforePlayCB(snd)
        return

    def __notifyAfterPlay(self, snd):
        if self.__afterPlayCB is not None:
            self.__afterPlayCB(snd)
        return

    def __clear(self):
        self.__soundsIter = None
        if self.__curPlayingSnd is not None:
            self.__curPlayingSnd.fmodSound.setCallback('EVENTFINISHED', None)
            self.__curPlayingSnd.stop()
            self.__curPlayingSnd = None
        self.__clearCallback()
        return

    def __playNextSound(self):
        self.__clearCallback()
        if self.__soundsIter is None:
            self.__soundsIter = iter(self.__sounds)
        try:
            self.__curPlayingSnd = Sound(next(self.__soundsIter))
            self.__notifyBeforePlay(self.__curPlayingSnd)
            self.__curPlayingSnd.fmodSound.setCallback('EVENTFINISHED', self.__finishCallback)
            self.__curPlayingSnd.play()
        except StopIteration:
            self.__clear()

        return

    def __clearCallback(self):
        if self.__bwCbID is not None:
            BigWorld.cancelCallback(self.__bwCbID)
            self.__bwCbID = None
        return

    def __finishCallback(self, snd):
        if snd is not None:
            snd.setCallback('EVENTFINISHED', None)
            snd.stop()
            snd = None
        self.__notifyAfterPlay(snd)
        self.__bwCbID = BigWorld.callback(0.1, self.__playNextSound)
        return
