# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/sound_control/sound_control.py
from cosmic_sound import play2DSoundEvent
from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager, SoundManagerStates

class VideoRewardsSoundControl(IVideoSoundManager):
    __slots__ = ('__state',)
    COSMIC_REWARD_VIDEO_START = 'ev_cosmic_lootbox_video_start'
    COSMIC_REWARD_VIDEO_STOP = 'ev_cosmic_lootbox_video_stop'
    COSMIC_REWARD_VIDEO_PAUSE = 'ev_cosmic_lootbox_video_pause'
    COSMIC_REWARD_VIDEO_RESUME = 'ev_cosmic_lootbox_video_resume'
    RTPC_VOLUME_CONTROL = 'RTPC_ext_video_volume'

    def __init__(self):
        self.__state = None
        return

    def start(self):
        self.setVolume()
        play2DSoundEvent(self.COSMIC_REWARD_VIDEO_START)
        self.__state = SoundManagerStates.PLAYING

    def stop(self):
        if self.__state != SoundManagerStates.STOPPED:
            play2DSoundEvent(self.COSMIC_REWARD_VIDEO_STOP)
            self.__state = SoundManagerStates.STOPPED

    def pause(self):
        play2DSoundEvent(self.COSMIC_REWARD_VIDEO_PAUSE)
        self.__state = SoundManagerStates.PAUSE

    def unpause(self):
        play2DSoundEvent(self.COSMIC_REWARD_VIDEO_RESUME)
        self.__state = SoundManagerStates.PLAYING

    def setVolume(self):
        import SoundGroups
        maxVolumeCategoryName = SoundGroups.g_instance.getMaxVolumeFromCategories(SoundGroups.USER_SETTINGS_CATEGORY_NAMES)
        SoundGroups.g_instance.setRTPC(self.RTPC_VOLUME_CONTROL, maxVolumeCategoryName)
