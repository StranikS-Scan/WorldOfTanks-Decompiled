# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/sounds/sound_constants.py
from last_stand.gui.ls_gui_constants import DifficultyLevel
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings
from gui.sounds.filters import States, StatesGroup
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from last_stand_common.last_stand_constants import ARENA_BONUS_TYPE
from last_stand.gui.sounds.voiceovers import Voiceover

class SoundLanguage(CONST_CONTAINER):
    RU_VOICEOVER_REALM_CODES = ('RU', 'ST', 'QA', 'DEV', 'SB')
    VOICEOVER_LOCALIZATION_SWITCH = 'SWITCH_ext_ev_hw_vo'
    VOICEOVER_CN = 'SWITCH_ext_ev_hw_vo_CN'
    VOICEOVER_RU = 'SWITCH_ext_ev_hw_vo_RU'
    VOICEOVER_UA = 'SWITCH_ext_ev_hw_vo_UA'
    VOICEOVER_EN = 'SWITCH_ext_ev_hw_vo_EN'
    LANGUAGE_UA = 'uk'
    LANGUAGE_RU = 'ru'


PROMO_ENTER = 'ev_last_stand_promo_screen_enter'
PROMO_EXIT = 'ev_last_stand_promo_screen_exit'
LS_ENTER_EVENT = 'ev_last_stand_main_enter'
LS_EXIT_EVENT = 'ev_last_stand_main_exit'
ABOUT_GAME_MODE_ENTER = 'ev_last_stand_about_event_enter'
ABOUT_GAME_MODE_EXIT = 'ev_last_stand_about_event_exit'
REWARD_PATH_ENTER = 'ev_last_stand_reward_path_enter'
REWARD_PATH_EXIT = 'ev_last_stand_reward_path_exit'
META_INTRO_ENTER = 'ev_last_stand_info_objectives_enter'
META_INTRO_EXIT = 'ev_last_stand_info_objectives_exit'
CONSUMABLES_VIEW_ENTER = 'ev_last_stand_consumables_enter'
CONSUMABLES_VIEW_EXIT = 'ev_last_stand_consumables_exit'
PRE_QUEUE_ENTER = 'ev_last_stand_matchmaker_enter'
PRE_QUEUE_EXIT = 'ev_last_stand_matchmaker_exit'
LS_PREVIEW_ENTER = 'ev_hw_hangar_tank_preview_enter'
LS_PREVIEW_EXIT = 'ev_hw_hangar_tank_preview_exit'
META_QUANTUM_OPEN_SOUND = 'ev_last_stand_quantum{}_enter'
META_QUANTUM_CLOSE_SOUND = 'ev_last_stand_quantum{}_exit'
META_VOICEOVER_UNMUTE = 'ev_last_stand_quantum_sound_on'
META_VOICEOVER_MUTE = 'ev_last_stand_quantum_sound_off'
META_VOICEOVER_BUTTON_CLICK_UNMUTE = 'ev_last_stand_quantum_button_sound_on'
META_VOICEOVER_BUTTON_CLICK_MUTE = 'ev_last_stand_quantum_button_sound_off'
PBS_ENTER = 'ev_last_stand_pbs_screen_enter'
PBS_EXIT = 'ev_last_stand_pbs_screen_exit'
DAILY_WIDGET_APPEAR = 'ev_last_stand_daily_widget_anim'
BADGE_MISSION_APPEAR = 'ev_last_stand_badge_widget_anim'
BUNDLE_VIEW_ENTER = 'ev_last_stand_exchange_screen_enter'
BUNDLE_VIEW_EXIT = 'ev_last_stand_exchange_screen_exit'
KING_REWARD_WINDOW_ENTER = 'ev_last_stand_king_reward_screen_enter'
KING_REWARD_WINDOW_EXIT = 'ev_last_stand_king_reward_screen_exit'
DIFFICULTY_SCREEN = {DifficultyLevel.MEDIUM: 'ev_last_stand_chapter_unlocked_02',
 DifficultyLevel.HARD: 'ev_last_stand_chapter_unlocked_03'}

class DifficultyWindowState(CONST_CONTAINER):
    GROUP = 'STATE_hangar_filtered'
    OPEN = 'STATE_hangar_filtered_on'
    CLOSE = 'STATE_hangar_filtered_off'


class KingRewardState(CONST_CONTAINER):
    GROUP = 'STATE_overlay_hangar_general'
    GENERAL_ON = 'STATE_overlay_hangar_general_on'
    GENERAL_OFF = 'STATE_overlay_hangar_general_off'


class PersonalDeathZoneAbilityBossState(CONST_CONTAINER):
    GROUP = 'STATE_ev_halloween_2021_ability_boss'
    ENTER = 'STATE_ev_halloween_2021_ability_boss_enter'
    EXIT = 'STATE_ev_halloween_2021_ability_boss_exit'


BOTS_SPAWN = {'germany:G64_Panther_II_LS_BOT': 'ev_halloween_2019_gameplay_spawn_hunter',
 'usa:A100_T49_LS_BOT': 'ev_hw_mirny13_gameplay_lost_spawn',
 'germany:G25_PzII_Luchs_Alpha_LS_BOT': 'ev_halloween_2019_gameplay_spawn_bunny',
 'germany:G25_PzII_Luchs_LS_BOT': 'ev_halloween_2019_gameplay_spawn_bunny',
 'germany:G00_Bomber_LS_BOT': 'ev_halloween_2019_gameplay_spawn_yorsh',
 'germany:G00_Alpha_Bomber_LS_BOT': 'ev_halloween_2021_gameplay_bomber_queen_spawn',
 'france:F110_Lynx_6x6_LS_BOT': 'ev_hw_gameplay_spawn_trapper'}
DEFAULT_BOT_SPAWN = 'ev_halloween_2019_gameplay_spawn_default'
BOTS_ENGINE = {'usa:A100_T49_LS_BOT': 'ev_hw_mirny13_gameplay_lost_engine',
 'germany:G114_Rheinmetall_Skorpian_LS_BOT': 'ev_hw_mirny13_gameplay_miniboss_engine',
 'germany:G99_RhB_Waffentrager_LS_BOT': 'ev_hw_mirny13_gameplay_miniboss_engine',
 'germany:G97_Waffentrager_IV_LS_BOT': 'ev_hw_mirny13_gameplay_miniboss_engine',
 'germany:G54_E-50_LS_BOT': 'ev_hw_mirny13_gameplay_miniboss_engine',
 'uk:GB81_FV4004_LS_BOT': 'ev_hw_mirny13_gameplay_miniboss_engine',
 'uk:GB83_FV4005_LS_BOT': 'ev_hw_mirny13_gameplay_miniboss_engine',
 'germany:G73_E50_Ausf_M_LS_BOT': 'ev_hw_mirny13_gameplay_miniboss_engine'}
BOTS_EXPLOSION = {'germany:G00_Bomber_LS_BOT': 'ev_halloween_2019_gameplay_bomber_explosion',
 'germany:G00_Alpha_Bomber_LS_BOT': 'ev_halloween_2021_gameplay_bomber_queen_explosion',
 'usa:A100_T49_LS_BOT': 'ev_hw_mirny13_gameplay_lost_explosion',
 'germany:G114_Rheinmetall_Skorpian_LS_BOT': 'ev_hw_mirny13_gameplay_miniboss_explosion',
 'germany:G99_RhB_Waffentrager_LS_BOT': 'ev_hw_mirny13_gameplay_miniboss_explosion',
 'germany:G97_Waffentrager_IV_LS_BOT': 'ev_hw_mirny13_gameplay_miniboss_explosion',
 'germany:G54_E-50_LS_BOT': 'ev_hw_mirny13_gameplay_miniboss_explosion',
 'uk:GB81_FV4004_LS_BOT': 'ev_hw_mirny13_gameplay_miniboss_explosion',
 'uk:GB83_FV4005_LS_BOT': 'ev_hw_mirny13_gameplay_miniboss_explosion',
 'germany:G73_E50_Ausf_M_LS_BOT': 'ev_hw_mirny13_gameplay_miniboss_explosion'}
BATTLE_START = 'ev_halloween_2019_gameplay_start'
BATTLE_FINISH = 'ev_halloween_2019_gameplay_stop'

class DeathZoneSounds(CONST_CONTAINER):
    ENTER = 'ev_halloween_2021_red_zone_red_enter'
    LEAVE = 'ev_halloween_2021_red_zone_red_exit'
    DAMAGE = 'ev_halloween_2021_red_zone_red_damage'


class PersonalDeathZoneSounds(CONST_CONTAINER):
    ACTIVATION = 'ev_halloween_2021_ability_death_zone_activation'
    DEACTIVATION = 'ev_halloween_2021_ability_death_zone_deactivation'


class PostMortemSounds(CONST_CONTAINER):
    ON = 'ev_halloween_2021_postmortem_on'
    OFF = 'ev_halloween_2021_postmortem_off'


ACTIVE_PHASE_RTPC = 'RTPC_ext_hw19_world'

class ActivePhaseState(CONST_CONTAINER):
    GROUP = 'STATE_ev_halloween_2019_world'
    PHASE_1 = 'STATE_ev_halloween_2019_world_m1'
    DEFAULT = PHASE_1
    _STATE_PATTERN = 'PHASE_{}'

    @classmethod
    def getStateByPhase(cls, phaseID):
        return getattr(cls, cls._STATE_PATTERN.format(phaseID), cls.DEFAULT)


VEHICLE_OBJ_NAME_PATTERN = 'hwVehicleSound_{}'

class Difficulty(CONST_CONTAINER):
    EASY = '01'
    MEDIUM = '02'
    HARD = '03'
    DEFAULT = EASY
    _DIFFICULTY_BY_ARENA_BONUS_TYPE = {ARENA_BONUS_TYPE.LAST_STAND: EASY,
     ARENA_BONUS_TYPE.LAST_STAND_MEDIUM: MEDIUM,
     ARENA_BONUS_TYPE.LAST_STAND_HARD: HARD}

    @classmethod
    def getDifficultyByArenaBonusType(cls, arenaBonusType):
        return cls._DIFFICULTY_BY_ARENA_BONUS_TYPE.get(arenaBonusType, cls.DEFAULT)


class DifficultyFormatter(object):

    def __init__(self, str_):
        self._str = str_

    def __call__(self, arenaBonusType):
        return self._str.format(dif=Difficulty.getDifficultyByArenaBonusType(arenaBonusType))


class DifficultyState(CONST_CONTAINER):
    GROUP = 'STATE_ev_last_stand_chapter'
    VALUE = DifficultyFormatter('STATE_ev_last_stand_chapter_{dif}')


class BattleEquipmentPanelSounds(CONST_CONTAINER):
    ACTIVATE = 'ev_halloween_2019_ui_ability_button'
    READY = 'ev_halloween_2019_ui_ability_button_ready'
    NOT_READY = 'ev_halloween_2019_ui_ability_button_not_ready'


class LootSounds(CONST_CONTAINER):

    class Player(CONST_CONTAINER):
        PICKUP_SUCCEED = {'LS_lootSoulsSmall': 'ev_halloween_2019_gameplay_collect',
         'LS_lootSoulsMedium': 'ev_halloween_2019_gameplay_collect',
         'LS_lootSoulsBig': 'ev_halloween_2019_gameplay_collect',
         'LS_lootShells': 'ev_halloween_2020_gameplay_collect_buff'}

    class Ally(CONST_CONTAINER):
        PICKUP_SUCCEED = 'ev_last_stand_collect_all_players'


HANGAR_SOUND_SETTINGS = CommonSoundSpaceSettings(name='hwHangar', entranceStates={Hangar.SOUND_STATE_PLACE: Hangar.SOUND_STATE_PLACE_GARAGE,
 StatesGroup.HANGAR_FILTERED: States.HANGAR_FILTERED_OFF}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')

class LastStandVO(CONST_CONTAINER):
    PLAYER_DEAD = 'ev_last_stand_vo_player_dead'
    ALLY_4_TANKS_LEFT = Voiceover('ev_last_stand_vo_4_tanks_left', aliveOnly=True)
    ALLY_3_TANKS_LEFT = Voiceover('ev_last_stand_vo_3_tanks_left', aliveOnly=True)
    ALLY_2_TANKS_LEFT = Voiceover('ev_last_stand_vo_2_tanks_left', aliveOnly=True)
    ALLY_1_TANKS_LEFT = Voiceover('ev_last_stand_vo_player_last', aliveOnly=True)
    BATTLE_STARTED = Voiceover('ev_last_stand_vo_start', 'ev_last_stand_vo_start_exposition', aliveOnly=True)
    WAVE_2_STARTED = 'ev_last_stand_vo_bots_spawn_02'
    WAVE_3_STARTED = 'ev_last_stand_vo_bots_spawn_03'
    WAVE_4_STARTED = 'ev_last_stand_vo_bots_spawn_04'
    WAVE_5_STARTED = 'ev_last_stand_vo_final_bots_spawn'
    WAVE_FINISHED = Voiceover('ev_last_stand_vo_destroyed_all_bots', aliveOnly=True)
    ONE_MINUTE_LEFT = 'ev_last_stand_vo_1min'
    WIN = 'ev_last_stand_vo_win'
    LOSE = 'ev_last_stand_vo_defeat'

    @classmethod
    def getWaveStartedVO(cls, phase):
        return getattr(cls, 'WAVE_{}_STARTED'.format(phase), None)

    @classmethod
    def getAllyTanksLeftVO(cls, alliesAliveCount):
        return getattr(cls, 'ALLY_{}_TANKS_LEFT'.format(alliesAliveCount), None)


class BattleMusic(CONST_CONTAINER):
    WAVE_STARTED = 'ev_last_stand_music_battle'
    BOTS_DESTROYED = 'ev_last_stand_music_exploration'
    WIN = 'ev_last_stand_music_end'
