# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/Scaleform/daapi/view/lobby/hangar/sounds.py
import SoundGroups
from gui.impl.gen import R
from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager, SoundManagerStates
from shared_utils import CONST_CONTAINER

class ArmoryYardSounds(CONST_CONTAINER):
    VIDEO_ARMOUR = 'ay_vid_stage_armour'
    VIDEO_GUN = 'ay_vid_stage_gun'
    VIDEO_TURRET = 'ay_vid_stage_turret'
    VIDEO_TRACKS = 'ay_vid_stage_tracks'
    VIDEO_REWARD = 'ay_vid_stage_reward'
    VIDEO_INTRO = 'ay_vid_stage_intro'
    VIDEO_PAUSE = 'ay_video_pause'
    VIDEO_RESUME = 'ay_video_resume'
    VIDEO_STOP = 'ay_video_stop'
    VIDEO_RTPC = 'RTPC_ext_video_volume'


class ArmoryYardVideoSoundControl(IVideoSoundManager):
    __VIDEO_TO_SOUND = {'ay_armour': ArmoryYardSounds.VIDEO_ARMOUR,
     'ay_gun': ArmoryYardSounds.VIDEO_GUN,
     'ay_turret': ArmoryYardSounds.VIDEO_TURRET,
     'ay_tracks': ArmoryYardSounds.VIDEO_TRACKS,
     'ay_reward': ArmoryYardSounds.VIDEO_REWARD,
     'ay_intro': ArmoryYardSounds.VIDEO_INTRO}

    def __init__(self, videoID):
        self.__videoID = videoID
        self.__state = None
        return

    @property
    def videoSoundEvent(self):
        return self.__getMapping().get(self.__videoID)

    def isVideoStarted(self):
        return self.__state is not None

    def start(self):
        sound = self.videoSoundEvent
        if sound:
            self.setVolume()
            SoundGroups.g_instance.playSound2D(sound)
            self.__state = SoundManagerStates.PLAYING

    def stop(self):
        if self.__state != SoundManagerStates.STOPPED:
            SoundGroups.g_instance.playSound2D(ArmoryYardSounds.VIDEO_STOP)
            self.__state = SoundManagerStates.STOPPED

    def pause(self):
        SoundGroups.g_instance.playSound2D(ArmoryYardSounds.VIDEO_PAUSE)
        self.__state = SoundManagerStates.PAUSE

    def unpause(self):
        SoundGroups.g_instance.playSound2D(ArmoryYardSounds.VIDEO_RESUME)
        self.__state = SoundManagerStates.PLAYING

    def setVolume(self):
        volumeLevel = SoundGroups.g_instance.getMaxVolumeFromCategories(SoundGroups.USER_SETTINGS_CATEGORY_NAMES)
        SoundGroups.g_instance.setRTPC(ArmoryYardSounds.VIDEO_RTPC, volumeLevel)

    def __getMapping(self):
        mapping = {}
        for video, sound in self.__VIDEO_TO_SOUND.iteritems():
            videoSource = R.videos.armory_yard.dyn(video)
            if videoSource.exists():
                mapping[videoSource()] = sound

        return mapping


class ArmoryYardRewardVideoSoundControl(ArmoryYardVideoSoundControl):

    def __init__(self):
        super(ArmoryYardRewardVideoSoundControl, self).__init__('')

    @property
    def videoSoundEvent(self):
        return ArmoryYardSounds.VIDEO_REWARD
