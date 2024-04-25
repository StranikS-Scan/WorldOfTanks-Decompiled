# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/Scaleform/daapi/view/lobby/hangar/sounds.py
import WWISE
from gui.impl.gen import R
from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager, SoundManagerStates
from shared_utils import CONST_CONTAINER

class ArmoryYardSounds(CONST_CONTAINER):
    VIDEO_EP3_ARMOUR = 'ay_ep_03_vid_stage_08'
    VIDEO_EP3_GUN = 'ay_ep_03_vid_stage_16'
    VIDEO_EP3_TURRET = 'ay_ep_03_vid_stage_18'
    VIDEO_EP3_TRACKS = 'ay_ep_03_vid_stage_22'
    VIDEO_EP3_REWARD = 'ay_ep_03_vid_stage_26'
    VIDEO_EP3_INTRO = 'ay_ep_03_vid_stage_00'
    VIDEO_PAUSE = 'ay_video_pause'
    VIDEO_RESUME = 'ay_video_resume'
    VIDEO_STOP = 'ay_video_stop'


class ArmoryYardVideoSoundControl(IVideoSoundManager):
    __VIDEO_TO_SOUND = {'ay_ep3_armour': ArmoryYardSounds.VIDEO_EP3_ARMOUR,
     'ay_ep3_gun': ArmoryYardSounds.VIDEO_EP3_GUN,
     'ay_ep3_turret': ArmoryYardSounds.VIDEO_EP3_TURRET,
     'ay_ep3_tracks': ArmoryYardSounds.VIDEO_EP3_TRACKS,
     'ay_ep3_reward': ArmoryYardSounds.VIDEO_EP3_REWARD,
     'ay_ep3_intro': ArmoryYardSounds.VIDEO_EP3_INTRO}

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
        return ArmoryYardSounds.VIDEO_EP3_REWARD
