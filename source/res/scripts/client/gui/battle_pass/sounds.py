# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/sounds.py
import WWISE
from constants import DEFAULT_LANGUAGE
from gui.impl.gen import R
from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager, SoundManagerStates
from helpers import getClientLanguage
from math_utils import clamp
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings

class SOUNDS(CONST_CONTAINER):
    ACTIVATE_CHAPTER_STATE = 'STATE_overlay_hangar_general'
    ACTIVATE_CHAPTER_STATE_ON = 'STATE_overlay_hangar_general_on'
    ACTIVATE_CHAPTER_STATE_OFF = 'STATE_overlay_hangar_general_off'
    HOLIDAY_SOUND_SPACE = 'tasks_holiday'
    HOLIDAY_STATE_PLACE = 'STATE_hangar_place'
    HOLIDAY_STATE_PLACE_TASKS = 'STATE_hangar_place_tasks'
    HOLIDAY_TASKS_ENTER = 'tasks_holiday_enter'
    HOLIDAY_TASKS_EXIT = 'tasks_holiday_exit'


ACTIVATE_CHAPTER_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.ACTIVATE_CHAPTER_STATE, entranceStates={SOUNDS.ACTIVATE_CHAPTER_STATE: SOUNDS.ACTIVATE_CHAPTER_STATE_ON}, exitStates={SOUNDS.ACTIVATE_CHAPTER_STATE: SOUNDS.ACTIVATE_CHAPTER_STATE_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
HOLIDAY_TASKS_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.HOLIDAY_SOUND_SPACE, entranceStates={SOUNDS.HOLIDAY_STATE_PLACE: SOUNDS.HOLIDAY_STATE_PLACE_TASKS}, exitStates={}, enterEvent=SOUNDS.HOLIDAY_TASKS_ENTER, exitEvent=SOUNDS.HOLIDAY_TASKS_EXIT, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)

class BattlePassSounds(CONST_CONTAINER):
    _OVERLAY = 'bp_overlay'
    CONFIRM_BUY = 'bp_overlay_pay'
    REWARD_SCREEN = 'bp_reward_screen'
    TANK_POINTS_CAP = 'bp_tank_point_done'
    VIDEO_STYLE_J20_Type_2605_2 = 'bp_s11_video_type_5_level_2_start'
    VIDEO_STYLE_J20_Type_2605_3 = 'bp_s11_video_type_5_level_3_start'
    VIDEO_STYLE_J20_Type_2605_4 = 'bp_s11_video_type_5_level_4_start'
    VIDEO_STYLE_F64_AMX_50_FOCH_B_2 = 'bp_s11_video_foch_b_level_2_start'
    VIDEO_STYLE_F64_AMX_50_FOCH_B_3 = 'bp_s11_video_foch_b_level_3_start'
    VIDEO_STYLE_F64_AMX_50_FOCH_B_4 = 'bp_s11_video_foch_b_level_4_start'
    VIDEO_STYLE_A67_T57_58_2 = 'bp_s11_video_t57_level_2_start'
    VIDEO_STYLE_A67_T57_58_3 = 'bp_s11_video_t57_level_3_start'
    VIDEO_STYLE_A67_T57_58_4 = 'bp_s11_video_t57_level_4_start'
    VIDEO_PAUSE = 'bp_video_pause'
    VIDEO_RESUME = 'bp_video_resume'
    VIDEO_STOP = 'bp_video_stop'
    VOICEOVER_STOP = 'bp_voiceovers_stop'
    REGULAR_VOICEOVER_STOP = 'bp_regular_voiceovers_stop'
    HOLIDAY_VOICEOVER_STOP = 'bp_holiday_voiceovers_stop'
    HOLIDAY_REWARD_SCREEN = 'bp_holiday_reward_screen'
    SPECIAL_TASKS_ENTER = 'tasks_special_enter'
    SPECIAL_TASKS_EXIT = 'tasks_special_exit'

    @classmethod
    def getOverlay(cls, count):
        return '_'.join([cls._OVERLAY, str(clamp(1, 3, count))])


class BattlePassLanguageSwitch(CONST_CONTAINER):
    GROUP_NAME = 'SWITCH_ext_battle_pass_video_language'
    RU = 'SWITCH_ext_battle_pass_video_language_RU'
    EN = 'SWITCH_ext_battle_pass_video_language_EN'
    CN = 'SWITCH_ext_battle_pass_video_language_CN'


class AwardVideoSoundControl(IVideoSoundManager):
    __LANGUAGE_STATES = {'ru': BattlePassLanguageSwitch.RU,
     'en': BattlePassLanguageSwitch.EN,
     'cn': BattlePassLanguageSwitch.CN}
    __VIDEO_TO_SOUND = {'c_201292_2': BattlePassSounds.VIDEO_STYLE_J20_Type_2605_2,
     'c_201292_3': BattlePassSounds.VIDEO_STYLE_J20_Type_2605_3,
     'c_201292_4': BattlePassSounds.VIDEO_STYLE_J20_Type_2605_4,
     'c_201548_2': BattlePassSounds.VIDEO_STYLE_F64_AMX_50_FOCH_B_2,
     'c_201548_3': BattlePassSounds.VIDEO_STYLE_F64_AMX_50_FOCH_B_3,
     'c_201548_4': BattlePassSounds.VIDEO_STYLE_F64_AMX_50_FOCH_B_4,
     'c_202316_2': BattlePassSounds.VIDEO_STYLE_A67_T57_58_2,
     'c_202316_3': BattlePassSounds.VIDEO_STYLE_A67_T57_58_3,
     'c_202316_4': BattlePassSounds.VIDEO_STYLE_A67_T57_58_4}

    def __init__(self, videoID):
        self.__videoID = videoID
        self.__state = None
        return

    def start(self):
        sound = self.__getMapping().get(self.__videoID)
        if sound:
            WWISE.WW_setSwitch(BattlePassLanguageSwitch.GROUP_NAME, self.__selectLanguageState())
            WWISE.WW_eventGlobal(sound)
            self.__state = SoundManagerStates.PLAYING

    def stop(self):
        if self.__state != SoundManagerStates.STOPPED:
            WWISE.WW_eventGlobal(BattlePassSounds.VIDEO_STOP)
            self.__state = SoundManagerStates.STOPPED

    def pause(self):
        WWISE.WW_eventGlobal(BattlePassSounds.VIDEO_PAUSE)
        self.__state = SoundManagerStates.PAUSE

    def unpause(self):
        WWISE.WW_eventGlobal(BattlePassSounds.VIDEO_RESUME)
        self.__state = SoundManagerStates.PLAYING

    def __selectLanguageState(self):
        language = getClientLanguage()
        if language not in self.__LANGUAGE_STATES:
            language = DEFAULT_LANGUAGE
        if language not in self.__LANGUAGE_STATES:
            language = 'en'
        return self.__LANGUAGE_STATES[language]

    def __getMapping(self):
        mapping = {}
        for video, sound in self.__VIDEO_TO_SOUND.iteritems():
            videoSource = R.videos.battle_pass.dyn(video)
            if videoSource.exists():
                mapping[videoSource()] = sound

        return mapping
