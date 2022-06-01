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


ACTIVATE_CHAPTER_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.ACTIVATE_CHAPTER_STATE, entranceStates={SOUNDS.ACTIVATE_CHAPTER_STATE: SOUNDS.ACTIVATE_CHAPTER_STATE_ON}, exitStates={SOUNDS.ACTIVATE_CHAPTER_STATE: SOUNDS.ACTIVATE_CHAPTER_STATE_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')

class BattlePassSounds(CONST_CONTAINER):
    _OVERLAY = 'bp_overlay'
    CONFIRM_BUY = 'bp_overlay_pay'
    REWARD_SCREEN = 'bp_reward_screen'
    TANK_POINTS_CAP = 'bp_tank_point_done'
    VIDEO_STYLE_430_2 = 'bp_s08_video_430_level_02_start'
    VIDEO_STYLE_430_3 = 'bp_s08_video_430_level_03_start'
    VIDEO_STYLE_430_4 = 'bp_s08_video_430_level_04_start'
    VIDEO_STYLE_E100_2 = 'bp_s08_video_e100_level_02_start'
    VIDEO_STYLE_E100_3 = 'bp_s08_video_e100_level_03_start'
    VIDEO_STYLE_E100_4 = 'bp_s08_video_e100_level_04_start'
    VIDEO_STYLE_STB_2 = 'bp_s08_video_stb_level_02_start'
    VIDEO_STYLE_STB_3 = 'bp_s08_video_stb_level_03_start'
    VIDEO_STYLE_STB_4 = 'bp_s08_video_stb_level_04_start'
    VIDEO_PAUSE = 'bp_video_pause'
    VIDEO_RESUME = 'bp_video_resume'
    VIDEO_STOP = 'bp_video_stop'

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
    __VIDEO_TO_SOUND = {'c_157516_2': BattlePassSounds.VIDEO_STYLE_430_2,
     'c_157516_3': BattlePassSounds.VIDEO_STYLE_430_3,
     'c_157516_4': BattlePassSounds.VIDEO_STYLE_430_4,
     'c_157260_2': BattlePassSounds.VIDEO_STYLE_E100_2,
     'c_157260_3': BattlePassSounds.VIDEO_STYLE_E100_3,
     'c_157260_4': BattlePassSounds.VIDEO_STYLE_E100_4,
     'c_157772_2': BattlePassSounds.VIDEO_STYLE_STB_2,
     'c_157772_3': BattlePassSounds.VIDEO_STYLE_STB_3,
     'c_157772_4': BattlePassSounds.VIDEO_STYLE_STB_4}

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
