# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/customization/HornSoundPlayer.py
# Compiled at: 2011-10-25 18:12:05
import BigWorld, FMOD
import Event
from debug_utils import LOG_DEBUG
from gui import ClientHangarSpace
from items import vehicles

class HornSoundPlayer(object):

    def __init__(self):
        super(HornSoundPlayer, self).__init__()
        self.__hornID = None
        self.__hornSoundIdx = 0
        self.__hornSounds = []
        self.__hornMode = ''
        self.__playing = False
        self.__stopCallback = None
        self.onStartSoundEvent = Event.Event()
        self.onStopSoundEvent = Event.Event()
        return

    def clear(self):
        while 1:
            sound = len(self.__hornSounds) and self.__hornSounds.pop()
            sound.setCallback('SOUNDDEF_START', None)
            sound.setCallback('SOUNDDEF_END', None)
            sound.stop()

        self.__hornID = None
        self.__hornSoundIdx = 0
        self.__hornMode = ''
        self.__playing = False
        return

    def fini(self):
        self.clear()
        self.onStartSoundEvent.clear()
        self.onStopSoundEvent.clear()
        if self.__stopCallback is not None:
            BigWorld.cancelCallback(self.__stopCallback)
            self.__stopCallback = None
        return

    def play(self, hornID):
        hornDesc = vehicles.g_cache.horns().get(hornID)
        if hornDesc is None:
            return
        else:
            LOG_DEBUG('Start playing sound by user')
            self.stop(forceSilence=True)
            self.__hornID = hornID
            self.__hornSounds = []
            self.__hornSoundIdx = 0
            self.__hornMode = hornDesc['mode']
            self.__stopCallback = None
            for sndEventId in hornDesc['sounds']:
                sound = FMOD.getSound(sndEventId)
                sound.position = ClientHangarSpace._V_START_POS
                sound.setCallback('SOUNDDEF_START', self.__soundDefStart)
                sound.setCallback('SOUNDDEF_END', self.__soundDefStop)
                self.__hornSounds.append(sound)

            if len(self.__hornSounds) > 0:
                self.__hornSounds[0].play()
                self.__playing = True
                if self.__hornMode == 'continuous' and hornDesc['maxDuration'] > 0:
                    self.__stopCallback = BigWorld.callback(hornDesc['maxDuration'], self.stop)
            return

    def stop(self, forceSilence=False):
        if not self.__playing:
            self.__stopCallback = None
            return
        else:
            LOG_DEBUG('Stop playing sound by user')
            if not forceSilence and self.__hornMode == 'twoSounds':
                if self.__hornSounds[1] is not None:
                    self.__hornSounds[1].play()
            else:
                self.onStopSoundEvent(self.__hornID)
                self.clear()
            if self.__stopCallback is not None:
                BigWorld.cancelCallback(self.__stopCallback)
                self.__stopCallback = None
            return

    def stopWithDelay(self, delay=2.0):
        if self.__hornMode == 'twoSounds' or delay <= 0:
            self.stop()
            return
        else:
            if self.__stopCallback is not None:
                BigWorld.cancelCallback(self.__stopCallback)
                self.__stopCallback = None
            self.__stopCallback = BigWorld.callback(delay, self.stop)
            return

    def __soundDefStart(self, sound):
        LOG_DEBUG('Start playing sound by event', sound)
        self.onStartSoundEvent(self.__hornID)

    def __soundDefStop(self, sound):
        LOG_DEBUG('Stop playing sound by event', sound)
        if self.__playing:
            self.onStopSoundEvent(self.__hornID)
            self.__hornSoundIdx += 1
            if self.__hornSoundIdx >= len(self.__hornSounds):
                self.clear()
                if self.__stopCallback is not None:
                    BigWorld.cancelCallback(self.__stopCallback)
                    self.__stopCallback = None
        return
