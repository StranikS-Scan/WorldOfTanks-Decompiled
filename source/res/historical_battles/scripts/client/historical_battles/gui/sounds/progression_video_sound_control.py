# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/sounds/progression_video_sound_control.py
import SoundGroups
from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager, SoundManagerStates
from historical_battles.gui.sounds.sound_constants import HBProgressionVideoSounds as VIDEO_SOUNDS, HBProgressionVideoEvents as VIDEO_EVENTS

class HBProgressionVideoSoundControl(IVideoSoundManager):
    __VIDEO_SOUND = {'progression_defence_1': VIDEO_SOUNDS.VIDEO_SOUND_1,
     'progression_defence_2': VIDEO_SOUNDS.VIDEO_SOUND_2,
     'progression_offence_1': VIDEO_SOUNDS.VIDEO_SOUND_3}

    def __init__(self, videoID):
        self.__videoID = videoID
        self.__state = None
        self.__sound = self.__getSound()
        return

    def isSoundStarted(self):
        return self.__state is not None

    def start(self):
        if self.__sound:
            self.__sound.play()
            self.__state = SoundManagerStates.PLAYING

    def stop(self):
        if self.isSoundStarted() and self.__state != SoundManagerStates.STOPPED:
            SoundGroups.g_instance.playSound2D(VIDEO_EVENTS.STOP)
            self.__state = SoundManagerStates.STOPPED

    def pause(self):
        if self.__sound and self.__sound.isPlaying:
            SoundGroups.g_instance.playSound2D(VIDEO_EVENTS.PAUSE)
            self.__state = SoundManagerStates.PAUSE

    def unpause(self):
        if self.__sound and self.__state == SoundManagerStates.PAUSE:
            SoundGroups.g_instance.playSound2D(VIDEO_EVENTS.RESUME)
            self.__state = SoundManagerStates.PLAYING

    def __getSound(self):
        soundEvent = self.__VIDEO_SOUND.get(self.__videoID, None)
        return SoundGroups.g_instance.getSound2D(soundEvent) if soundEvent else None
