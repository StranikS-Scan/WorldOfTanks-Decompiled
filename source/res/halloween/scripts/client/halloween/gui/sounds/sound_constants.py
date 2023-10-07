# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/sounds/sound_constants.py
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings

class SoundLanguage(CONST_CONTAINER):
    RU_VOICEOVER_REALM_CODES = ('RU', 'ST', 'QA', 'DEV', 'SB')
    VOICEOVER_LOCALIZATION_SWITCH = 'SWITCH_ext_ev_halloween_witches_vo_language'
    VOICEOVER_CN = 'SWITCH_ext_ev_halloween_witches_vo_language_cn'
    VOICEOVER_RU = 'SWITCH_ext_ev_halloween_witches_vo_language_ru'
    VOICEOVER_EN = 'SWITCH_ext_ev_halloween_witches_vo_language_en'


class WitchesVO(CONST_CONTAINER):
    GROUP = 'SWITCH_ext_ev_halloween_witches_vo_character'
    SWITCH_PATTERN = 'SWITCH_ext_ev_halloween_witches_vo_character_{}'

    @staticmethod
    def getSwitch(witchIndex):
        return WitchesVO.SWITCH_PATTERN.format(witchIndex)


class HangarEvents(CONST_CONTAINER):
    HW_ENTER = 'ev_shadowPlay_enter'
    HW_EXIT = 'ev_shadowPlay_exit'
    MAGIC_BOOK_ENTER = 'ev_shadowPlay_hangar_magic_book_enter'
    MAGIC_BOOK_EXIT = 'ev_shadowPlay_hangar_magic_book_exit'


class BattleEvents(CONST_CONTAINER):
    EQUIPMENT_ACTIVE = 'ev_shadowPlay_ui_ability_button'
    EQUIPMENT_READY = 'ev_shadowPlay_ui_ability_button_ready'
    EQUIPMENT_NOT_READY = 'ev_shadowPlay_ui_ability_button_not_ready'
    RESPAWN_VEHICLE = 'ev_shadowPlay_respawn'
    VEHICLE_KILLED = 'ev_shadowPlay_buff_off'
    AIR_DROP_SPAWNED = 'ev_shadowPlay_buff_notification'
    LOOT_SPAWNED = 'ev_shadowPlay_buff_pickup_point'
    ARENA_START_BATTLE_VO = 'vo_shadowPlay_gp_start_battle'
    EQUIPMENT_FROZEN_ARROW = 'ev_shadowPlay_ui_ability_button_cold_arrow'
    EQUIPMENT_HEALING_ARROW = 'ev_shadowPlay_ui_ability_button_healing_branch'
    EQUIPMENT_CURSE_ARROW = 'ev_shadowPlay_ui_ability_button_cursed_touch'
    EQUIPMENT_FIRE_ARROW = 'ev_shadowPlay_ui_ability_button_flame_shot'
    EQUIPMENT_LAUGH_ARROW = 'ev_shadowPlay_ui_ability_button_jester_benefit'


MAGIC_BOOK_BG = 'hw_authors_bg.png'

class WitchesMetaState(CONST_CONTAINER):
    GROUP = 'STATE_ev_halloween_witches_meta'
    ON = 'STATE_ev_halloween_witches_meta_main_on'
    OFF = 'STATE_ev_halloween_witches_meta_main_off'
    WINDOW_META = ON
    WINDOW_INTRO = OFF
    WINDOW_HISTORY = ON
    WINDOW_WITCHES = ON
    WINDOW_OUTRO = OFF


WITCHES_SOUND_SPACE = CommonSoundSpaceSettings(name='WitchesMeta', entranceStates={}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='ev_shadowPlay_meta_enter', exitEvent='ev_shadowPlay_meta_exit')

class WitchesMetaEvents(CONST_CONTAINER):
    PATTERN = 'ev_shadowPlay_meta_w{phase}_{view}_{state}'
    INTRO = 'intro'
    OUTRO = 'outro'
    ENTER = 'enter'
    EXIT = 'exit'


HANGAR_WITCHES_VO_PREVIEW = 'ev_shadowPlay_crew_preview_vo_button'
WITCHES_VIEW_OPENED = 'ev_shadowPlay_meta_crew_preview'
REWARDS_SOUND_SPACE = CommonSoundSpaceSettings(name='HWRewards', entranceStates={'STATE_overlay_hangar_general': 'STATE_overlay_hangar_general_on'}, exitStates={'STATE_overlay_hangar_general': 'STATE_overlay_hangar_general_off'}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')

class RewardsEvents(CONST_CONTAINER):
    REWARDS_ENTER = 'ev_shadowPlay_reward_screen_enter'
    REWARDS_EXIT = 'ev_shadowPlay_reward_screen_exit'
    CREW_ENTER = 'ev_shadowPlay_reward_screen_crew_enter'
    CREW_EXIT = 'ev_shadowPlay_reward_screen_crew_exit'


HW_HANGAR_OVERLAYS = CommonSoundSpaceSettings(name='HWHangarOverlays', entranceStates={'STATE_hangar_filtered': 'STATE_hangar_filtered_on'}, exitStates={'STATE_hangar_filtered': 'STATE_hangar_filtered_off'}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')

class TeamBasesVO(CONST_CONTAINER):
    PATTERN = 'vo_shadowPlay_gp_{team}_captured_{count}_base'
    ALLY = 'allies'
    ENEMY = 'enemy'
    ONE = 'first'
    TWO = 'second'

    @staticmethod
    def getVO(isAlly, count):
        return TeamBasesVO.PATTERN.format(team=TeamBasesVO.ALLY if isAlly else TeamBasesVO.ENEMY, count=TeamBasesVO.ONE if count == 1 else TeamBasesVO.TWO)


class BattleEndVO(CONST_CONTAINER):
    ALLY_WINS = 'vo_shadowPlay_gp_time_points_less'
    ENEMY_WINS = 'vo_shadowPlay_gp_time_points_more'
    DRAW = 'vo_shadowPlay_gp_time_points_equally'


INTERACTIVE_EVENT_START_BATTLE = 'ev_shadowPlay_gp_music_start_battle'
INTERACTIVE_EVENT_FIGHT = 'ev_shadowPlay_gp_music_fight'
INTERACTIVE_EVENT_EXPLORATION = 'ev_shadowPlay_gp_music_exploration'
INTERACTIVE_EVENT_2_MINUTES_REMAIN = 'ev_shadowPlay_gp_music_coda_2min'
INTERACTIVE_EVENT_2_BASES_CAPTURED = 'ev_shadowPlay_gp_music_end_battle'
