# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/sounds.py
import WWISE
from constants import DEFAULT_LANGUAGE
from gui.impl.gen import R
from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager, SoundManagerStates
from helpers import getClientLanguage
from math_utils import clamp
from shared_utils import CONST_CONTAINER

class BattlePassSounds(CONST_CONTAINER):
    _OVERLAY = 'bp_overlay'
    CONFIRM_BUY = 'bp_overlay_pay'
    REWARD_SCREEN = 'bp_reward_screen'
    TANK_POINTS_CAP = 'bp_tank_point_done'
    VIDEO_STYLE_705A_2 = 'bp_2021_s01_video_obj705_style_01_start'
    VIDEO_STYLE_705A_3 = 'bp_2021_s01_video_obj705_style_02_start'
    VIDEO_STYLE_705A_4 = 'bp_2021_s01_video_obj705_style_03_start'
    VIDEO_STYLE_121_2 = 'bp_2021_s01_video_obj121_style_01_start'
    VIDEO_STYLE_121_3 = 'bp_2021_s01_video_obj121_style_02_start'
    VIDEO_STYLE_121_4 = 'bp_2021_s01_video_obj121_style_03_start'
    VIDEO_STYLE_T110E3_2 = 'bp_2021_s01_video_t110e3_style_01_start'
    VIDEO_STYLE_T110E3_3 = 'bp_2021_s01_video_t110e3_style_02_start'
    VIDEO_STYLE_T110E3_4 = 'bp_2021_s01_video_t110e3_style_03_start'
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
    __VIDEO_TO_SOUND = {'c_65612_2': BattlePassSounds.VIDEO_STYLE_705A_2,
     'c_65612_3': BattlePassSounds.VIDEO_STYLE_705A_3,
     'c_65612_4': BattlePassSounds.VIDEO_STYLE_705A_4,
     'c_65868_2': BattlePassSounds.VIDEO_STYLE_121_2,
     'c_65868_3': BattlePassSounds.VIDEO_STYLE_121_3,
     'c_65868_4': BattlePassSounds.VIDEO_STYLE_121_4,
     'c_66124_2': BattlePassSounds.VIDEO_STYLE_T110E3_2,
     'c_66124_3': BattlePassSounds.VIDEO_STYLE_T110E3_3,
     'c_66124_4': BattlePassSounds.VIDEO_STYLE_T110E3_4}

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
