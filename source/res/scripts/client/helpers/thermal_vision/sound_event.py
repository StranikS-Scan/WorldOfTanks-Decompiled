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

    def play(self, delay=0):
        self.stopCallback(self._triggerSound)
        if delay > 0:
            self.delayCallback(delay, self._triggerSound)
            return
        SoundGroups.g_instance.playSound2D(self.startSound)
        self.active = True

    def stop(self):
        self.stopCallback(self._triggerSound)
        if self.active and self.stopSound is not None:
            SoundGroups.g_instance.playSound2D(self.stopSound)
        self.active = False
        return

    def _triggerSound(self):
        SoundGroups.g_instance.playSound2D(self.startSound)
        self.active = True
