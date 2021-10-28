# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/sound_constants.py
from shared_utils import CONST_CONTAINER

class EnabledStatus(object):
    ENABLED_DEFAULT = 0
    ENABLED_BY_USER = 1
    DISABLED = 2

    @classmethod
    def isEnabled(cls, status):
        return status in (cls.ENABLED_DEFAULT, cls.ENABLED_BY_USER)


PLAYING_SOUND_CHECK_PERIOD = 1.0
IS_ADVANCED_LOGGING = False

class SoundSystems(CONST_CONTAINER):
    UNKNOWN = 0
    WWISE = 1

    @classmethod
    def getUserName(cls, sysID):
        return cls.getKeyByValue(sysID) or cls.UNKNOWN


class SoundFilters(CONST_CONTAINER):
    EMPTY = 1
    FILTERED_HANGAR = 2
    FORT_FILTER = 3
    BATTLE_PASS_FILTER = 4
    HANGAR_OVERLAY = 5
    MARATHON_FILTER = 6
    HANGAR_PLACE_TASKS_DAILY = 7
    HANGAR_PLACE_TASKS_MISSIONS = 8
    HANGAR_PLACE_TASKS_BATTLE_PASS = 9


class SPEAKERS_CONFIG(object):
    AUTO_DETECTION = 0
    SPEAKER_SETUP_2_0 = 2
    SPEAKER_SETUP_5_1 = 5
    SPEAKER_SETUP_7_1 = 7
    RANGE = (AUTO_DETECTION,
     SPEAKER_SETUP_2_0,
     SPEAKER_SETUP_5_1,
     SPEAKER_SETUP_7_1)


class SoundLanguage(CONST_CONTAINER):
    VOICEOVER_LOCALIZATION_SWITCH = 'SWITCH_ext_ev_halloween_2019_voiceover'
    VOICEOVER_RU = 'SWITCH_ext_ev_halloween_2019_voiceover_ru'
    VOICEOVER_EN = 'SWITCH_ext_ev_halloween_2019_voiceover_en'
    VOICEOVER_CN = 'SWITCH_ext_ev_halloween_2019_voiceover_cn'
    VOICEOVER_SILENCE = 'SWITCH_ext_ev_halloween_2019_voiceover_silence'
    HANGAR_LANGUAGE_CONFIG = {('RU', 'ST', 'QA', 'DEV', 'SB'): {'EN': VOICEOVER_EN,
                                       'default': VOICEOVER_RU},
     ('NA', 'EU', 'KR', 'ASIA'): {'EN': VOICEOVER_EN,
                                  'default': VOICEOVER_SILENCE},
     ('CN',): {'default': VOICEOVER_CN}}
    BATTLE_LANGUAGE_CONFIG = {('RU', 'ST', 'QA', 'DEV', 'SB'): {'default': VOICEOVER_RU},
     ('NA', 'EU', 'KR', 'ASIA'): {'default': VOICEOVER_EN},
     ('CN',): {'default': VOICEOVER_CN}}


class HW21SoundConsts(CONST_CONTAINER):
    EVENT_ENTER_EVENT = 'ev_halloween_2019_hangar_metagame_enter'
    EVENT_LEAVE_EVENT = 'ev_halloween_2019_hangar_metagame_exit'
    HANGAR_FIRST_DAILY_VO = 'ev_halloween_2021_hangar_vo_hello_first'
    HANGAR_DAILY_VO = 'ev_halloween_2021_hangar_vo_hello'
    HANGAR_BR_WIN_VO_TEMPLATE = 'ev_halloween_2021_vo_victory_difficulty{}'
    HANGAR_PBS_SLIDER = 'ev_halloween_2021_hangar_pbs_slider'
    HANGAR_PBS_MAIN_POINTS = 'ev_halloween_2020_hangar_pbs_main_points'
    HANGAR_PBS_QUEST = 'ev_halloween_2020_hangar_pbs_quest'
    HANGAR_PBS_REWARD = 'ev_halloween_2020_hangar_pbs_reward'
    HANGAR_PBS_PROGRESSBAR = 'ev_halloween_2020_hangar_pbs_progressbar'
    HANGAR_TEAMFIGHT_LOSE = 'ev_halloween_2019_vo_result_defeat_no_enough_matter'
    HANGAR_BOSSFIGHT_LOSE = 'ev_halloween_2021_vo_defeat_bossfight'
