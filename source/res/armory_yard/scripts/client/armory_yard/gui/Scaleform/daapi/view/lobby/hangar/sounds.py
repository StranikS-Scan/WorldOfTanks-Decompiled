# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/Scaleform/daapi/view/lobby/hangar/sounds.py
import WWISE
from gui.impl.gen import R
from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager, SoundManagerStates
from shared_utils import CONST_CONTAINER

class ArmoryYardSounds(CONST_CONTAINER):
    VIDEO_EP2_ARMOUR = 'ay_ep_02_video_stage_09'
    VIDEO_EP2_GUN = 'ay_ep_02_video_stage_22'
    VIDEO_EP2_TURRET = 'ay_ep_02_video_stage_29'
    VIDEO_EP2_TRACKS = 'ay_ep_02_video_stage_32'
    VIDEO_EP2_REWARD = 'ay_ep_02_video_stage_38'
    VIDEO_EP2_INTRO = 'ay_ep_02_video_stage_00'
    VIDEO_PAUSE = 'ay_video_pause'
    VIDEO_RESUME = 'ay_video_resume'
    VIDEO_STOP = 'ay_video_stop'


class ArmoryYardVideoSoundControl(IVideoSoundManager):
    __VIDEO_TO_SOUND = {'ay_ep2_armour': ArmoryYardSounds.VIDEO_EP2_ARMOUR,
     'ay_ep2_gun': ArmoryYardSounds.VIDEO_EP2_GUN,
     'ay_ep2_turret': ArmoryYardSounds.VIDEO_EP2_TURRET,
     'ay_ep2_tracks': ArmoryYardSounds.VIDEO_EP2_TRACKS,
     'ay_ep2_reward': ArmoryYardSounds.VIDEO_EP2_REWARD,
     'ay_ep2_intro': ArmoryYardSounds.VIDEO_EP2_INTRO}

    def __init__(self, videoID):
        self.__videoID = videoID
        self.__state = None
        return

    @property
    def videoSoundEvent(self):
        return self.__getMapping().get(self.__videoID)

    def start(self):
        sound = self.videoSoundEvent
        if sound:
            WWISE.WW_eventGlobal(sound)
            self.__state = SoundManagerStates.PLAYING

    def stop(self):
        if self.__state != SoundManagerStates.STOPPED:
            WWISE.WW_eventGlobal(ArmoryYardSounds.VIDEO_STOP)
            self.__state = SoundManagerStates.STOPPED

    def pause(self):
        WWISE.WW_eventGlobal(ArmoryYardSounds.VIDEO_PAUSE)
        self.__state = SoundManagerStates.PAUSE

    def unpause(self):
        WWISE.WW_eventGlobal(ArmoryYardSounds.VIDEO_RESUME)
        self.__state = SoundManagerStates.PLAYING

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
        return ArmoryYardSounds.VIDEO_EP2_REWARD
