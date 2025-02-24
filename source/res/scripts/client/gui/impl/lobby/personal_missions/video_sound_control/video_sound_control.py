# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/video_sound_control/video_sound_control.py
import SoundGroups
from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager, SoundManagerStates
from gui.server_events.pm3_constants import VIDEO

class PM3VideoSoundControl(IVideoSoundManager):
    __INTRO_ID = 0
    __VIDEO_SOUND = {__INTRO_ID: VIDEO.SOUND_INTRO,
     8: VIDEO.SOUND_REWARD_1,
     9: VIDEO.SOUND_REWARD_2,
     10: VIDEO.SOUND_REWARD_3}

    def __init__(self, videoID=__INTRO_ID):
        self.__videoID = videoID
        self.__state = SoundManagerStates.STOPPED
        self.__sound = self.__getSound()

    def start(self):
        if self.__sound:
            SoundGroups.g_instance.setState(VIDEO.GROUP, VIDEO.PLAY)
            self.__sound.play()
            self.__state = SoundManagerStates.PLAYING

    def stop(self):
        if self.__state != SoundManagerStates.STOPPED:
            SoundGroups.g_instance.setState(VIDEO.GROUP, VIDEO.STOP)
            SoundGroups.g_instance.playSound2D(VIDEO.STOP_EVENT)
            self.__state = SoundManagerStates.STOPPED

    def pause(self):
        if self.__sound and self.__sound.isPlaying:
            SoundGroups.g_instance.playSound2D(VIDEO.PAUSE)
            self.__state = SoundManagerStates.PAUSE

    def unpause(self):
        if self.__sound and self.__state == SoundManagerStates.PAUSE:
            SoundGroups.g_instance.playSound2D(VIDEO.RESUME)
            self.__state = SoundManagerStates.PLAYING

    def __getSound(self):
        soundEvent = self.__VIDEO_SOUND.get(self.__videoID, None)
        return SoundGroups.g_instance.getSound2D(soundEvent) if soundEvent else None
