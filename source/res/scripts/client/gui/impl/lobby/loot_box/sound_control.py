# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/sound_control.py
import SoundGroups
from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager, SoundManagerStates

class VideoRewardsSoundControl(IVideoSoundManager):
    __slots__ = ('__state',)
    LOOTBOXES_REWARD_VIDEO_START = 'lootboxes_video_start'
    LOOTBOXES_REWARD_VIDEO_STOP = 'lootboxes_video_stop'
    LOOTBOXES_REWARD_VIDEO_PAUSE = 'lootboxes_video_pause'
    LOOTBOXES_REWARD_VIDEO_RESUME = 'lootboxes_video_resume'
    RTPC_VOLUME_CONTROL = 'RTPC_ext_video_volume'

    def __init__(self):
        self.__state = None
        return

    def start(self):
        self.setVolume()
        SoundGroups.g_instance.playSound2D(self.LOOTBOXES_REWARD_VIDEO_START)
        self.__state = SoundManagerStates.PLAYING

    def stop(self):
        if self.__state != SoundManagerStates.STOPPED:
            SoundGroups.g_instance.playSound2D(self.LOOTBOXES_REWARD_VIDEO_STOP)
            self.__state = SoundManagerStates.STOPPED

    def pause(self):
        SoundGroups.g_instance.playSound2D(self.LOOTBOXES_REWARD_VIDEO_PAUSE)
        self.__state = SoundManagerStates.PAUSE

    def unpause(self):
        SoundGroups.g_instance.playSound2D(self.LOOTBOXES_REWARD_VIDEO_RESUME)
        self.__state = SoundManagerStates.PLAYING

    def setVolume(self):
        maxVolumeCategoryName = SoundGroups.g_instance.getMaxVolumeFromCategories(SoundGroups.USER_SETTINGS_CATEGORY_NAMES)
        SoundGroups.g_instance.setRTPC(self.RTPC_VOLUME_CONTROL, maxVolumeCategoryName)
