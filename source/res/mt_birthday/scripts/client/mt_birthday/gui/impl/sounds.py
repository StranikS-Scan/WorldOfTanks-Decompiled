# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/sounds.py
import SoundGroups
from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager, SoundManagerStates
from shared_utils import CONST_CONTAINER
from gui.sounds.filters import StatesGroup, States
from sound_gui_manager import CommonSoundSpaceSettings

class BirthdaySoundEvents(CONST_CONTAINER):
    VIDEO_START = 'gui_video_mt_birthday_play'
    VIDEO_DONE = 'gui_video_mt_birthday_stop'
    VIDEO_PAUSE = 'gui_video_mt_birthday_pause'
    VIDEO_RESUME = 'gui_video_mt_birthday_resume'
    MAIN_VIEW_ENTER = 'hangar_h15_bday_tank_mail_enter'
    MAIN_VIEW_EXIT = 'hangar_h15_bday_tank_mail_exit'
    OVERLAY_HANGAR_GENERAL = 'STATE_overlay_hangar_general'
    OVERLAY_HANGAR_GENERAL_ON = 'STATE_overlay_hangar_general_on'
    OVERLAY_HANGAR_GENERAL_OFF = 'STATE_overlay_hangar_general_off'


BIRTHDAY_REWARD_VIDEO_SOUND_SPACE = CommonSoundSpaceSettings(name='birthday_video_reward', entranceStates={StatesGroup.VIDEO_OVERLAY: States.VIDEO_OVERLAY_ON}, exitStates={StatesGroup.VIDEO_OVERLAY: States.VIDEO_OVERLAY_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')

class VideoRewardsSoundControl(IVideoSoundManager):
    __slots__ = ('__bonusName', '__state')

    def __init__(self, bonusName):
        self.__bonusName = bonusName
        self.__state = None
        return

    def setBonusName(self, bonusName):
        self.__bonusName = bonusName

    def start(self):
        SoundGroups.g_instance.playSound2D(BirthdaySoundEvents.VIDEO_START)
        self.__state = SoundManagerStates.PLAYING

    def stop(self):
        if self.__state != SoundManagerStates.STOPPED:
            SoundGroups.g_instance.playSound2D(BirthdaySoundEvents.VIDEO_DONE)
            self.__state = SoundManagerStates.STOPPED

    def pause(self):
        SoundGroups.g_instance.playSound2D(BirthdaySoundEvents.VIDEO_PAUSE)
        self.__state = SoundManagerStates.PAUSE

    def unpause(self):
        SoundGroups.g_instance.playSound2D(BirthdaySoundEvents.VIDEO_RESUME)
        self.__state = SoundManagerStates.PLAYING
