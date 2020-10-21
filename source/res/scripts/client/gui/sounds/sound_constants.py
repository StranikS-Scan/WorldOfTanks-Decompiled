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


class HW20SoundConsts(CONST_CONTAINER):
    HANGAR_FIRST_DAILY_VO = 'ev_halloween_2020_hangar_vo_hello_first'
    HANGAR_DAILY_VOS_TEMPLATE = 'ev_halloween_2020_hangar_vo_hello_{:02d}'
    HANGAR_DAILY_VOS_AMOUNT = 6
    HANGAR_BR_WIN_VO_TEMPLATE = 'ev_halloween_2020_vo_victory_difficulty{}'
    HANGAR_BR_VOS_LOW = ['ev_halloween_2020_hangar_vo_story_d1_01',
     'ev_halloween_2020_hangar_vo_story_d1_02',
     'ev_halloween_2020_hangar_vo_story_d1_04',
     'ev_halloween_2020_hangar_vo_story_d1_05',
     'ev_halloween_2020_hangar_vo_story_d1_08',
     'ev_halloween_2020_hangar_vo_story_d1_09',
     'ev_halloween_2020_hangar_vo_story_d1_13',
     'ev_halloween_2020_hangar_vo_story_d1_14',
     'ev_halloween_2020_hangar_vo_story_d1_15',
     'ev_halloween_2020_hangar_vo_story_d1_18',
     'ev_halloween_2020_hangar_vo_story_d1_19',
     'ev_halloween_2020_hangar_vo_story_d1_22',
     'ev_halloween_2020_hangar_vo_story_d1_23',
     'ev_halloween_2020_hangar_vo_story_d1_26',
     'ev_halloween_2020_hangar_vo_story_d1_27',
     'ev_halloween_2020_hangar_vo_story_d1_31',
     'ev_halloween_2020_hangar_vo_story_d1_33',
     'ev_halloween_2020_hangar_vo_story_d1_34']
    HANGAR_BR_VOS_MED = ['ev_halloween_2020_hangar_vo_story_d2_03',
     'ev_halloween_2020_hangar_vo_story_d2_06',
     'ev_halloween_2020_hangar_vo_story_d2_10',
     'ev_halloween_2020_hangar_vo_story_d2_17',
     'ev_halloween_2020_hangar_vo_story_d2_20',
     'ev_halloween_2020_hangar_vo_story_d2_24',
     'ev_halloween_2020_hangar_vo_story_d2_28',
     'ev_halloween_2020_hangar_vo_story_d2_30',
     'ev_halloween_2020_hangar_vo_story_d2_32',
     'ev_halloween_2020_hangar_vo_story_d2_35']
    HANGAR_BR_VOS_HIGH = ['ev_halloween_2020_hangar_vo_story_d3_07',
     'ev_halloween_2020_hangar_vo_story_d3_11',
     'ev_halloween_2020_hangar_vo_story_d3_16',
     'ev_halloween_2020_hangar_vo_story_d3_25',
     'ev_halloween_2020_hangar_vo_story_d3_29',
     'ev_halloween_2020_hangar_vo_story_d3_36']
    HANGAR_PBS_SLIDER = 'ev_halloween_2020_hangar_pbs_slider'
    HANGAR_PBS_MAIN_POINTS = 'ev_halloween_2020_hangar_pbs_main_points'
    HANGAR_PBS_QUEST = 'ev_halloween_2020_hangar_pbs_quest'
    HANGAR_PBS_REWARD = 'ev_halloween_2020_hangar_pbs_reward'
    HANGAR_PBS_PROGRESSBAR = 'ev_halloween_2020_hangar_pbs_progressbar'
