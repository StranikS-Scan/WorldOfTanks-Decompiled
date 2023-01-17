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
    BATTLE_PASS_STATE = 'STATE_overlay_hangar_general'
    BATTLE_PASS_STATE_ON = 'STATE_overlay_hangar_general_on'
    BATTLE_PASS_STATE_OFF = 'STATE_overlay_hangar_general_off'
    ACTIVATE_CHAPTER_STATE = 'STATE_overlay_hangar_tasks'
    ACTIVATE_CHAPTER_STATE_ON = 'STATE_overlay_hangar_tasks_on'
    ACTIVATE_CHAPTER_STATE_OFF = 'STATE_overlay_hangar_tasks_off'


ACTIVATE_CHAPTER_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.ACTIVATE_CHAPTER_STATE, entranceStates={SOUNDS.ACTIVATE_CHAPTER_STATE: SOUNDS.ACTIVATE_CHAPTER_STATE_ON}, exitStates={SOUNDS.ACTIVATE_CHAPTER_STATE: SOUNDS.ACTIVATE_CHAPTER_STATE_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
BATTLE_PASS_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.BATTLE_PASS_STATE, entranceStates={SOUNDS.BATTLE_PASS_STATE: SOUNDS.BATTLE_PASS_STATE_ON}, exitStates={SOUNDS.BATTLE_PASS_STATE: SOUNDS.BATTLE_PASS_STATE_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')

class BattlePassSounds(CONST_CONTAINER):
    _OVERLAY = 'bp_overlay'
    CONFIRM_BUY = 'bp_overlay_pay'
    REWARD_SCREEN = 'bp_reward_screen'
    TANK_POINTS_CAP = 'bp_tank_point_done'
    VIDEO_STYLE_60TP_2 = 'bp_s09_video_60tp_level_02_start'
    VIDEO_STYLE_60TP_3 = 'bp_s09_video_60tp_level_03_start'
    VIDEO_STYLE_60TP_4 = 'bp_s09_video_60tp_level_04_start'
    VIDEO_STYLE_PROGETTO_65_2 = 'bp_s09_video_progetto_65_level_02_start'
    VIDEO_STYLE_PROGETTO_65_3 = 'bp_s09_video_progetto_65_level_03_start'
    VIDEO_STYLE_PROGETTO_65_4 = 'bp_s09_video_progetto_65_level_04_start'
    VIDEO_STYLE_AMX_13_105_2 = 'bp_s09_video_amx_13_105_level_02_start'
    VIDEO_STYLE_AMX_13_105_3 = 'bp_s09_video_amx_13_105_level_03_start'
    VIDEO_STYLE_AMX_13_105_4 = 'bp_s09_video_amx_13_105_level_04_start'
    VIDEO_PAUSE = 'bp_video_pause'
    VIDEO_RESUME = 'bp_video_resume'
    VIDEO_STOP = 'bp_video_stop'
    HOLIDAY_VOICEOVERS_STOP = 'bp_fairyWorld_voiceovers_stop'

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
    __VIDEO_TO_SOUND = {'c_170060_2': BattlePassSounds.VIDEO_STYLE_60TP_2,
     'c_170060_3': BattlePassSounds.VIDEO_STYLE_60TP_3,
     'c_170060_4': BattlePassSounds.VIDEO_STYLE_60TP_4,
     'c_172364_2': BattlePassSounds.VIDEO_STYLE_PROGETTO_65_2,
     'c_172364_3': BattlePassSounds.VIDEO_STYLE_PROGETTO_65_3,
     'c_172364_4': BattlePassSounds.VIDEO_STYLE_PROGETTO_65_4,
     'c_170316_2': BattlePassSounds.VIDEO_STYLE_AMX_13_105_2,
     'c_170316_3': BattlePassSounds.VIDEO_STYLE_AMX_13_105_3,
     'c_170316_4': BattlePassSounds.VIDEO_STYLE_AMX_13_105_4}

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
