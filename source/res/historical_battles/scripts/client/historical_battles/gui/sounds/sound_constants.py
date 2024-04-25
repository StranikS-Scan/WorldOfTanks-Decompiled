# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/sounds/sound_constants.py
from sound_gui_manager import createSpaceSettings
from shared_utils import CONST_CONTAINER
from gui.sounds.filters import States, StatesGroup

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
    ARTILERY_APPOINTED_SOUND = 'ev_secret_event_gameplay_ability_button_radio'
    MINEFIELD_APPOINTED_SOUND = 'ev_secret_event_gameplay_ability_minefield'
    TACTICAL_MINEFIELD_APPOINTED_SOUND = 'ev_secret_event_gameplay_ability_tactical_mine'
    HEAL_POINT_NPC = 'ev_secret_event_gameplay_ability_repair_npc'
    NITRO_DEACTIVATION = 'ev_secret_event_gameplay_ability_nitro_deactivation'


class HBMusicEvents(CONST_CONTAINER):
    BATTLE_MUSIC = 'music_kupalinka_dron'


class HBBattleStates(CONST_CONTAINER):
    GROUP = 'STATE_ev_se_dron'
    SILENCE = 'STATE_ev_se_dron_silence'
    RELAXED = 'STATE_ev_se_dron_relaxed'
    INTENSIVE = 'STATE_ev_se_dron_intensive'
    BOSS_FIGHT = 'STATE_ev_se_dron_bossfight'


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
    LIFE_ADDED = 'vo_se_gameplay_enemy_new_life_added'
    BOSS_TASK = 'vo_se_gameplay_destroy_enemy_command_vehicle'
    WIN = 'vo_se_victory'
    DEFEAT = 'vo_se_defeat'
    PLAYER_VEHICLE_DESTROYED = 'vo_se_gameplay_vehicle_destroyed'
    PLAYER_VEHICLE_DESTROYED_LAST_TIME = 'vo_se_gameplay_vehicle_destroyed_last_time'
    PLAYER_RESPAWN = 'vo_se_gameplay_vehicle_respawn'
    LAST_PLAYER_RESPAWN = 'vo_se_gameplay_latest_vehicle_respawn'
    ADDITIONAL_LIFE_EXPECTATION = 'vo_se_gameplay_expectation'
    PLAYER_ALONE_IN_BATTLE = 'vo_se_gameplay_alone_in_battle'
    DEATH_ZONE_ATTACK = 'vo_se_gameplay_death_zone_attack'
    ABILITY_INCENDIARY_SHOT = 'vo_se_gameplay_incendiary_shot'
    HEAL_POINT_NPC = 'vo_se_ab_field_repair_npc'


class HBHangarProgressionEvents(CONST_CONTAINER):
    PROGRESSION_START = 'ev_se_hangar_progression_01'
    PROGRESSION_START_VOICE_OVER = 'vo_se_story_intro'
    PROGRESSION_COMPLETE = 'ev_se_hangar_progression_02'
    PROGRESSION_COMPLETE_VOICE_OVER = 'vo_se_story_outro'
    PROGRESSION_EXIT = 'ev_se_hangar_progression_exit'


class HBHangarEvents(CONST_CONTAINER):
    ORDER_ANIMATION = 'ev_secret_event_hangar_ui_button_battle_orders'
