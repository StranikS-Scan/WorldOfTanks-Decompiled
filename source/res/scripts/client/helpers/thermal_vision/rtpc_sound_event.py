# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/thermal_vision/rtpc_sound_event.py
import BigWorld
import SoundGroups
from helpers.CallbackDelayer import CallbackDelayer

class RTPCSoundEvent(CallbackDelayer):

    def __init__(self, rtpcName, startSound, stopSound):
        super(RTPCSoundEvent, self).__init__()
        self.rtpcName = rtpcName
        self.startSound = startSound
        self.stopSound = stopSound

    def play(self, duration, startTime=None):
        if duration <= 0:
            return
        startTime = startTime or BigWorld.serverTime()
        if not self.hasDelayedCallback(self._updateValue):
            SoundGroups.g_instance.playSound2D(self.startSound)
        self.delayCallback(0, self._updateValue, duration, startTime)

    def stop(self):
        SoundGroups.g_instance.setRTCPGlobal(self.rtpcName, 0)
        SoundGroups.g_instance.playSound2D(self.stopSound)
        self.stopCallback(self._updateValue)

    def _updateValue(self, duration, startTime):
        elapsedTime = BigWorld.serverTime() - startTime
        if elapsedTime >= duration:
            self.stop()
            return
        value = elapsedTime / duration * 100.0
        SoundGroups.g_instance.setRTCPGlobal(self.rtpcName, value)
