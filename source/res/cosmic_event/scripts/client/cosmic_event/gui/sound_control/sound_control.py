# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/sound_control/sound_control.py
import SoundGroups
from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager, SoundManagerStates
from cosmic_sound import play2DSoundEvent, IntroVideoSound

class BaseVideoSoundControl(IVideoSoundManager):
    __slots__ = ('__state',)
    EVENT_START = None
    EVENT_STOP = None
    EVENT_PAUSE = None
    EVENT_RESUME = None
    RTPC_VOLUME_EVENT = None

    def __init__(self):
        self.__state = SoundManagerStates.STOPPED

    def start(self):
        if self.__state == SoundManagerStates.PLAYING:
            return
        self._onBeforeStart()
        self._playEvent(self.EVENT_START)
        self.__state = SoundManagerStates.PLAYING

    def stop(self):
        if self.__state == SoundManagerStates.STOPPED:
            return
        self._playEvent(self.EVENT_STOP)
        self.__state = SoundManagerStates.STOPPED

    def pause(self):
        if self.__state != SoundManagerStates.PLAYING:
            return
        self._playEvent(self.EVENT_PAUSE)
        self.__state = SoundManagerStates.PAUSE

    def unpause(self):
        if self.__state != SoundManagerStates.PAUSE:
            return
        self._playEvent(self.EVENT_RESUME)
        self.__state = SoundManagerStates.PLAYING

    def setVolume(self, volume):
        if self.RTPC_VOLUME_EVENT:
            SoundGroups.g_instance.setRTPC(self.RTPC_VOLUME_EVENT, volume)

    def _onBeforeStart(self):
        pass

    def _playEvent(self, eventName):
        if eventName:
            play2DSoundEvent(eventName)


class IntroVideoSoundControl(BaseVideoSoundControl):
    EVENT_START = IntroVideoSound.START
    EVENT_STOP = IntroVideoSound.STOP
    EVENT_PAUSE = IntroVideoSound.PAUSE
    EVENT_RESUME = IntroVideoSound.RESUME
    RTPC_VOLUME_EVENT = 'RTPC_ext_volume_fader'

    def _onBeforeStart(self):
        SoundGroups.g_instance.updateVideoVolume()


class VideoRewardsSoundControl(BaseVideoSoundControl):
    EVENT_START = 'ev_cosmic_lootbox_video_start'
    EVENT_STOP = 'ev_cosmic_lootbox_video_stop'
    EVENT_PAUSE = 'ev_cosmic_lootbox_video_pause'
    EVENT_RESUME = 'ev_cosmic_lootbox_video_resume'
    RTPC_VOLUME_EVENT = 'RTPC_ext_video_volume'

    def _onBeforeStart(self):
        maxVolumeCategoryName = SoundGroups.g_instance.getMaxVolumeFromCategories(SoundGroups.USER_SETTINGS_CATEGORY_NAMES)
        SoundGroups.g_instance.setRTPC(self.RTPC_VOLUME_EVENT, maxVolumeCategoryName)
