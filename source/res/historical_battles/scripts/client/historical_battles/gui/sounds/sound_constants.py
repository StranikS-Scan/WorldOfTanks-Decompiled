# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/sounds/sound_constants.py
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER
from gui.sounds.filters import States, StatesGroup

class GeneralSounds(CONST_CONTAINER):
    GENERAL_STATE = 'STATE_overlay_hangar_general'
    GENERAL_STATE_ON = 'STATE_overlay_hangar_general_on'
    GENERAL_STATE_OFF = 'STATE_overlay_hangar_general_off'


class SoundLanguage(CONST_CONTAINER):
    RU_VOICEOVER_REALM_CODES = ('RU', 'ST', 'QA', 'DEV', 'SB')
    VOICEOVER_LOCALIZATION_SWITCH = 'SWITCH_ext_ev_2022_secret_event_voice_over'
    VOICEOVER_CN = 'SWITCH_ext_ev_2022_secret_event_voice_over_cn'
    VOICEOVER_RU = 'SWITCH_ext_ev_2022_secret_event_voice_over_ru'
    VOICEOVER_EN = 'SWITCH_ext_ev_2020_secret_event_voice_over_en'


class CommanderRole(CONST_CONTAINER):
    SWITCH_GROUP = 'SWITCH_ext_ev_2022_secret_event_voice_over_commander'
    STATE_TEMPLATE = 'SWITCH_ext_ev_2022_secret_event_voice_over_commander_{}'


class ShopSounds(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'hb_show_view'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_SHOP = 'STATE_hangar_place_shop'
    ENTER = 'shop_enter'
    EXIT = 'shop_exit'


def createSpaceSettings(name=None, entranceStates=None, exitStates=None, persistentSounds=None, stoppableSounds=None, priorities=None, autoStart=None, enterEvent=None, exitEvent=None, parentSpace=None):
    return CommonSoundSpaceSettings(name=name, entranceStates=entranceStates or {}, exitStates=exitStates or {}, persistentSounds=persistentSounds or (), stoppableSounds=stoppableSounds or (), priorities=priorities or (), autoStart=autoStart or False, enterEvent=enterEvent, exitEvent=exitEvent, parentSpace=parentSpace)


GENERAL_SOUND_SPACE = createSpaceSettings(name=GeneralSounds.GENERAL_STATE, entranceStates={GeneralSounds.GENERAL_STATE: GeneralSounds.GENERAL_STATE_ON}, exitStates={GeneralSounds.GENERAL_STATE: GeneralSounds.GENERAL_STATE_OFF}, autoStart=True)
SHOP_SOUND_SPACE = createSpaceSettings(name=ShopSounds.COMMON_SOUND_SPACE, entranceStates={ShopSounds.STATE_PLACE: ShopSounds.STATE_PLACE_SHOP}, autoStart=True, enterEvent=ShopSounds.ENTER, exitEvent=ShopSounds.EXIT)

class HangarSounds(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'hb_hangar'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_GARAGE = 'STATE_hangar_place_garage'


HANGAR_SOUND_SPACE = createSpaceSettings(name=HangarSounds.COMMON_SOUND_SPACE, entranceStates={HangarSounds.STATE_PLACE: HangarSounds.STATE_PLACE_GARAGE,
 StatesGroup.HANGAR_FILTERED: States.HANGAR_FILTERED_OFF}, autoStart=True)

class BoostersShopSounds(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'hb_boosters_shop'
    STATE_PLACE = 'STATE_ev_se_moscow_orders'
    STATE_PLACE_ENTER = 'STATE_ev_se_moscow_orders_shop'
    STATE_PLACE_EXIT = 'STATE_ev_se_moscow_orders_hangar'
    ENTER = 'ev_se_moscow_orders_enter'
    EXIT = 'ev_se_moscow_orders_exit'


BOOSTERS_SHOP_SOUND_SPACE = createSpaceSettings(name=ShopSounds.COMMON_SOUND_SPACE, entranceStates={BoostersShopSounds.STATE_PLACE: BoostersShopSounds.STATE_PLACE_ENTER}, exitStates={BoostersShopSounds.STATE_PLACE: BoostersShopSounds.STATE_PLACE_EXIT}, autoStart=True, enterEvent=BoostersShopSounds.ENTER, exitEvent=BoostersShopSounds.EXIT)

class HBUISound(CONST_CONTAINER):
    EMPTY_SOUND = ''
    READY_SOUND = 'ev_secret_event_gameplay_ability_button_ready'
    PRESSED_SOUND = 'ev_secret_event_gameplay_ability_button'
    NOT_READY_SOUND = 'ev_secret_event_gameplay_ability_button_not_ready'
    AOE_ABILITY_APPOINTED_SOUND = 'ev_secret_event_gameplay_ability_button_radio'
    MINEFIELD_APPOINTED_SOUND = 'ev_secret_event_gameplay_ability_minefield'
    TACTICAL_MINEFIELD_APPOINTED_SOUND = 'ev_secret_event_gameplay_ability_tactical_mine'
    HEAL_POINT_NPC = 'ev_secret_event_gameplay_ability_repair_npc'
    NITRO_DEACTIVATION = 'ev_secret_event_gameplay_ability_nitro_deactivation'


class HBMusicEvents(CONST_CONTAINER):
    DEFENCE_MUSIC = 'music_defensive_dron'
    OFFENCE_MUSIC = 'music_attack_dron'


class HBBattleStates(CONST_CONTAINER):
    GROUP = 'STATE_ev_se_dron'
    SILENCE = 'STATE_ev_se_dron_silence'
    RELAXED = 'STATE_ev_se_dron_relaxed'
    INTENSIVE = 'STATE_ev_se_dron_intensive'
    BOSS_FIGHT = 'STATE_ev_se_dron_bossfight'
    VICTORY = 'STATE_ev_se_dron_coda_win'
    DEFEAT = 'STATE_ev_se_dron_coda_defeat'


class HangarParallaxState(CONST_CONTAINER):
    GROUP = 'STATE_ev_se_moscow_parallax'
    DEFENSIVE = 'STATE_ev_se_moscow_parallax1_defensive'
    LAST_STAND = 'STATE_ev_se_moscow_parallax2_last_stand'
    ATTACK = 'STATE_ev_se_moscow_parallax3_attack'
    BLOCK = 'STATE_ev_se_moscow_parallax_block'


class HangarFullscreenState(CONST_CONTAINER):
    GROUP = 'STATE_ev_se_moscow_fullscreen'
    OPEN = 'STATE_ev_se_moscow_fullscreen_open'
    CLOSE = 'STATE_ev_se_moscow_fullscreen_close'


class HBEventGameplayState(CONST_CONTAINER):
    GROUP = 'STATE_ev_2020_secret_event_gameplay'
    ON = 'STATE_ev_2020_secret_event_gameplay_on'
    OFF = 'STATE_ev_2020_secret_event_gameplay_off'


class HangarViewState(CONST_CONTAINER):
    GROUP = 'STATE_hangar_view'
    HANGAR = 'STATE_hangar_view_01'
    PROGRESSION = 'STATE_hangar_view_02'
    DIVISIONS = 'STATE_hangar_view_03'
    ORDERS = 'STATE_hangar_view_04'


class HBHangarEvent(CONST_CONTAINER):
    ENTER = 'ev_se_parallax_enter'
    EXIT = 'ev_se_parallax_exit'


class HBBattleEvent(CONST_CONTAINER):
    ENTER = 'ev_secret_event_gameplay_enter'
    EXIT = 'ev_secret_event_gameplay_exit'


class HBDeathZoneEvent(CONST_CONTAINER):
    SOUND = 'ev_secret_event_gameplay_ability_death_zone'


class HBStaticDeathZoneEvents(CONST_CONTAINER):
    START_TIMER = 'ev_secret_event_gameplay_death_sector_timer_start'
    STOP_TIMER = 'ev_secret_event_gameplay_death_sector_timer_stop'


class HBTimerEvents(CONST_CONTAINER):
    START = 'ev_secret_event_hangar_ui_time_countdown'
    STOP = 'ev_secret_event_hangar_ui_time_countdown_stop'


class HBNotificationEvents(CONST_CONTAINER):
    GENERAL = 'ev_secret_event_gameplay_ui_notification'
    TASK_DONE = 'ev_secret_event_ui_attack_repelled'
    TIME_EMERGENCE = 'ev_secret_event_ui_time_emergence'


class HBGameplayVoiceovers(CONST_CONTAINER):
    ONE_MINUTE_LEFT = 'vo_se_gameplay_time_running_out'
    TWO_MINUTES_LEFT = 'vo_se_gameplay_time_required'
    REPEL_COUNTER_ATTACK = 'vo_se_gameplay_enemy_counter_attack'
    PLAYER_ATTACK = 'vo_se_gameplay_enemy_reinforcement'
    BOSS_TASK = 'vo_se_gameplay_destroy_enemy_command_vehicle'
    DEFENCE_FIRST_WAVE = 'vo_se_gameplay_defensive_first_attack'
    DEFENCE_WAVES = 'vo_se_gameplay_defensive_attack'
    DEFENCE_LAST_WAVE = 'vo_se_gameplay_defensive_last_attack'
    DEFENCE_COUNTER_ATTACK = 'vo_se_gameplay_defensive_counter_attack'
    OFFENCE_WIN = 'vo_se_victory'
    OFFENCE_DEFEAT = 'vo_se_defeat'
    DEFENCE_WIN = 'vo_se_defensive_victory'
    DEFENCE_DEFEAT = 'vo_se_defensive_defeat'
    DEFENCE_DRAW = 'vo_se_defensive_drawn'
    PLAYER_VEHICLE_DESTROYED = 'vo_se_gameplay_vehicle_destroyed'
    PLAYER_VEHICLE_DESTROYED_LAST_TIME = 'vo_se_gameplay_vehicle_destroyed_last_time'
    PLAYER_RESPAWN = 'vo_se_gameplay_vehicle_respawn'
    LAST_PLAYER_RESPAWN = 'vo_se_gameplay_latest_vehicle_respawn'
    PLAYER_ALONE_IN_BATTLE = 'vo_se_gameplay_alone_in_battle'
    DEATH_ZONE_ATTACK = 'vo_se_gameplay_death_zone_attack'
    ABILITY_INCENDIARY_SHOT_HB = 'vo_se_gameplay_incendiary_shot'
    HEAL_POINT_NPC = 'vo_se_ab_field_repair_npc'


class HBHangarProgressionEvents(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'hb_progression'
    PROGRESSION_DEFENCE_ENTERED = 'ev_se_hangar_progression_01'
    PROGRESSION_OFFENCE_ENTERED = 'ev_se_hangar_progression_02'
    PROGRESSION_EXIT = 'ev_se_hangar_progression_exit'


PROGRESSION_SOUND_SPACE = createSpaceSettings(name=HBHangarProgressionEvents.COMMON_SOUND_SPACE, autoStart=True, enterEvent=None, exitEvent=HBHangarProgressionEvents.PROGRESSION_EXIT)

class HBHangarEvents(CONST_CONTAINER):
    ORDER_ANIMATION = 'ev_secret_event_hangar_ui_button_battle_orders'
    ORDER_COUNTER_START = 'comp_7_progressbar_start'
    ORDER_COUNTER_STOP = 'comp_7_progressbar_stop_silent'


class HBProgressionVideoEvents(CONST_CONTAINER):
    PAUSE = 'ev_se_video_pause'
    RESUME = 'ev_se_video_resume'
    STOP = 'ev_se_video_stop'


class HBProgressionVideoSounds(CONST_CONTAINER):
    VIDEO_SOUND_1 = 'ev_se_video_defensive_01'
    VIDEO_SOUND_2 = 'ev_se_video_defensive_02'
    VIDEO_SOUND_3 = 'ev_se_video_attack_01'


class HBRespawnEvent(CONST_CONTAINER):
    TANK_SELECTION = 'ev_se_ui_tank_selection'
