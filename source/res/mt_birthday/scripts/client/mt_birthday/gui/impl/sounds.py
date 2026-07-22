# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/sounds.py
import SoundGroups
from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager, SoundManagerStates
from shared_utils import CONST_CONTAINER
from gui.sounds.filters import StatesGroup, States
from sound_gui_manager import CommonSoundSpaceSettings

class BirthdaySoundEvents(CONST_CONTAINER):
    VIDEO_START = 'mt_bday_2026_lb_video_start'
    VIDEO_DONE = 'mt_bday_2026_lb_video_stop'
    VIDEO_PAUSE = 'mt_bday_2026_lb_video_pause'
    VIDEO_RESUME = 'mt_bday_2026_lb_video_resume'
    MAIN_VIEW_ENTER = 'mt_bday_2026_enter'
    MAIN_VIEW_EXIT = 'mt_bday_2026_exit'
    REWARD_SCREEN_ANIMATION_SKIP = 'mt_bday_2026_quest_giver_reward_skip'
    OVERLAY_HANGAR_GENERAL = 'STATE_overlay_hangar_general'
    OVERLAY_HANGAR_GENERAL_ON = 'STATE_overlay_hangar_general_on'
    OVERLAY_HANGAR_GENERAL_OFF = 'STATE_overlay_hangar_general_off'


BIRTHDAY_REWARD_VIDEO_SOUND_SPACE = CommonSoundSpaceSettings(name='birthday_video_reward', entranceStates={StatesGroup.VIDEO_OVERLAY: States.VIDEO_OVERLAY_ON}, exitStates={StatesGroup.VIDEO_OVERLAY: States.VIDEO_OVERLAY_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
BIRTHDAY_REWARD_SCREEN_SOUND_SPACE = CommonSoundSpaceSettings(name='birthday_reward_screen', entranceStates={BirthdaySoundEvents.OVERLAY_HANGAR_GENERAL: BirthdaySoundEvents.OVERLAY_HANGAR_GENERAL_ON}, exitStates={BirthdaySoundEvents.OVERLAY_HANGAR_GENERAL: BirthdaySoundEvents.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
BIRTHDAY_PLAYER_SELECT_SOUND_SPACE = CommonSoundSpaceSettings(name='birthday_player_select_screen', entranceStates={BirthdaySoundEvents.OVERLAY_HANGAR_GENERAL: BirthdaySoundEvents.OVERLAY_HANGAR_GENERAL_ON}, exitStates={BirthdaySoundEvents.OVERLAY_HANGAR_GENERAL: BirthdaySoundEvents.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
BIRTHDAY_SOUND_SPACE = CommonSoundSpaceSettings(name='birthday', entranceStates={}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='mt_bday_2026_enter', exitEvent='mt_bday_2026_exit')

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
