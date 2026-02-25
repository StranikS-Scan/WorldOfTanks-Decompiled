# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/thermal_vision/sound_event.py
import SoundGroups
from helpers.CallbackDelayer import CallbackDelayer

class SoundEvent(CallbackDelayer):

    def __init__(self, startSound, stopSound=None):
        super(SoundEvent, self).__init__()
        self.startSound = startSound
        self.stopSound = stopSound
        self.active = False
        self.__startSound = None
        return

    def play(self, delay=0):
        self.stopCallback(self._triggerSound)
        if delay > 0:
            self.delayCallback(delay, self._triggerSound)
            return
        self._playStartSound()

    def stop(self, playStopSound=True):
        self.stopCallback(self._triggerSound)
        if playStopSound and self.active and self.stopSound is not None:
            SoundGroups.g_instance.playSound2D(self.stopSound)
        elif self.__startSound and self.__startSound.isPlaying:
            self.__startSound.stop()
        self.__startSound = None
        self.active = False
        return

    def _playStartSound(self):
        self.__startSound = SoundGroups.g_instance.getSound2D(self.startSound)
        if self.__startSound is not None:
            self.__startSound.play()
            self.active = True
        return

    def _triggerSound(self):
        self._playStartSound()
