# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/r4_sound_constants.py
from collections import OrderedDict
from gui.battle_control.controllers.commander.common import MappedKeys
from constants import CURRENT_REALM
from RTSShared import RTSSupply
TANK_TYPE_TO_SWITCH = OrderedDict((('heavyTank', 'SWITCH_ext_r4_tank_type_tt'),
 ('mediumTank', 'SWITCH_ext_r4_tank_type_st'),
 ('AT-SPG', 'SWITCH_ext_r4_tank_type_pt'),
 ('lightTank', 'SWITCH_ext_r4_tank_type_lt'),
 ('SPG', 'SWITCH_ext_r4_tank_type_sau')))
TANK_PRIORITY_BY_CLASS_TAG = {tankType:priority for priority, tankType in enumerate(TANK_TYPE_TO_SWITCH.keys())}

class R4_SOUND(object):
    SOUND_REMAPPING_LABEL_TANKMAN = 'rts_tankman'
    SOUND_REMAPPING_LABEL_COMMANDER = 'rts_commander'
    SOUND_REMAPPING_LABEL_RTS_BOOTCAMP = 'rts_bootcamp'
    R4_VO_TANK_TYPE_SWITCH_GROUP_NAME = 'SWITCH_ext_r4_tank_type'
    R4_ALLY_GET_CRITICAL_DAMAGE_UI = 'r4_ally_get_critical_damage_ui'
    R4_DAMAGED_DEVICE_ENGINE = 'r4_allies_damage_engine'
    R4_DAMAGED_DEVICE_AMMOBAY = 'r4_allies_damage_ammo'
    R4_DAMAGED_DEVICE_DRIVER = 'r4_allies_damage_mechanic'
    R4_KILLED_TANKMAN_LOADER = 'r4_allies_damage_loader'
    R4_KILLED_TANKMAN_COMMANDER = 'r4_allies_damage_commander'
    R4_KILLED_TANKMAN_GUNNER = 'r4_allies_damage_gunner'
    R4_DAMAGED_DEVICE_TO_VOICE_EVENT = {'loader1': R4_KILLED_TANKMAN_LOADER,
     'loader2': R4_KILLED_TANKMAN_LOADER,
     'commander': R4_KILLED_TANKMAN_COMMANDER,
     'driver': R4_DAMAGED_DEVICE_DRIVER,
     'gunner1': R4_KILLED_TANKMAN_GUNNER,
     'gunner2': R4_KILLED_TANKMAN_GUNNER,
     'engine': R4_DAMAGED_DEVICE_ENGINE,
     'ammoBay': R4_DAMAGED_DEVICE_AMMOBAY}
    KEYS_TO_MANNER_UI_SOUND = [MappedKeys.getKey(MappedKeys.KEY_HOLD_MANNER),
     MappedKeys.getKey(MappedKeys.KEY_SCOUT_MANNER),
     MappedKeys.getKey(MappedKeys.KEY_SMART_MANNER),
     MappedKeys.getKey(MappedKeys.KEY_HALT),
     MappedKeys.getKey(MappedKeys.KEY_CONTROL_VEHICLE),
     MappedKeys.getKey(MappedKeys.KEY_RETREAT),
     MappedKeys.getKey(MappedKeys.KEY_FORCE_ORDER_MODE)]
    R4_START_BATTLE = 'r4_start_battle'
    R4_MODE_STRATEGIC = 'r4_mode_strategic'
    R4_MODE_ARCADE = 'r4_mode_arcade'
    R4_MODE_STRATEGIC_SFX = 'r4_mode_strategic_sfx'
    R4_MODE_ARCADE_SFX = 'r4_mode_arcade_sfx'
    R4_ARCADE_WELCOME = 'r4_arcade_welcome'
    R4_LOST_EYE_CONTACT = 'r4_lost_eye_contact'
    R4_COMMANDER_ENTER = 'r4_commander_enter'
    R4_COMMANDER_EXIT = 'r4_commander_exit'
    R4_TANKMAN_ENTER = 'r4_tankman_enter'
    R4_TANKMAN_EXIT = 'r4_tankman_exit'
    R4_VICTORY = 'r4_victory'
    R4_DEFEAT = 'r4_defeat'
    R4_DRAW = 'r4_draw'
    R4_TIME_WARNING = 'r4_time'
    R4_ALLY_SELECTED = 'r4_ally_selected'
    R4_ALLY_SELECTED_ARENA_UI = 'r4_ally_selected_arena_ui'
    R4_ALLY_SELECTED_INTERFACE_UI = 'r4_ally_selected_interface_ui'
    R4_ALLY_DETECTED = 'r4_ally_detected'
    R4_ENEMY_DETECTED = 'r4_enemy_detected'
    R4_ENEMY_DETECTED_UI = 'r4_enemy_detected_ui'
    ENEMY_SIGHTED_FOR_TEAM = 'enemy_sighted_for_team'
    R4_ALLY_GET_FIRST_DAMAGE = 'r4_ally_get_first_damage'
    R4_ALLY_GET_MEDIUM_DAMAGE = 'r4_ally_get_medium_damage'
    R4_ALLY_GET_BIG_DAMAGE = 'r4_ally_get_big_damage'
    R4_ALLY_DAMAGE_EVENTS = (R4_ALLY_GET_FIRST_DAMAGE, R4_ALLY_GET_MEDIUM_DAMAGE, R4_ALLY_GET_BIG_DAMAGE)
    R4_ALLY_DESTROYED = 'r4_ally_destroyed'
    R4_ALLY_DESTROYED_UI = 'r4_ally_destroyed_ui'
    R4_ALLY_DESTROYED_REMAIN_5 = 'r4_ally_destroyed_counter_remain_05'
    R4_ALLY_DESTROYED_REMAIN_4 = 'r4_ally_destroyed_counter_remain_04'
    R4_ALLY_DESTROYED_REMAIN_3 = 'r4_ally_destroyed_counter_remain_03'
    R4_ALLY_DESTROYED_REMAIN_2 = 'r4_ally_destroyed_counter_remain_02'
    R4_ALLY_DESTROYED_REMAIN_1 = 'r4_ally_destroyed_counter_remain_01'
    R4_ENEMY_DESTROYED = 'r4_enemy_destroyed'
    R4_ENEMY_DESTROYED_REMAIN_5 = 'r4_enemy_destroyed_counter_remain_5'
    R4_ENEMY_DESTROYED_REMAIN_4 = 'r4_enemy_destroyed_counter_remain_4'
    R4_ENEMY_DESTROYED_REMAIN_3 = 'r4_enemy_destroyed_counter_remain_3'
    R4_ENEMY_DESTROYED_REMAIN_2 = 'r4_enemy_destroyed_counter_remain_2'
    R4_ENEMY_DESTROYED_REMAIN_1 = 'r4_enemy_destroyed_counter_remain_1'
    R4_ENEMY_DESTROYED_LAST = 'r4_enemy_destroyed_last'
    R4_ENEMY_DESTROYED_COUNTER_1 = 'r4_enemy_destroyed_counter_1'
    R4_ENEMY_DESTROYED_COUNTER_2 = 'r4_enemy_destroyed_counter_2'
    R4_ENEMY_DESTROYED_COUNTER_3 = 'r4_enemy_destroyed_counter_3'
    R4_ENEMY_DESTROYED_COUNTER_4 = 'r4_enemy_destroyed_counter_4'
    R4_ENEMY_DESTROYED_COUNTER_5 = 'r4_enemy_destroyed_counter_5'
    R4_ENEMY_DESTROYED_COUNTER_6 = 'r4_enemy_destroyed_counter_6'
    R4_ENEMY_DESTROYED_COUNTER_7 = 'r4_enemy_destroyed_counter_7'
    R4_ALLY_DESTROYED_EVENTS = (None,
     R4_ALLY_DESTROYED_REMAIN_1,
     R4_ALLY_DESTROYED_REMAIN_2,
     R4_ALLY_DESTROYED_REMAIN_3,
     R4_ALLY_DESTROYED_REMAIN_4,
     R4_ALLY_DESTROYED_REMAIN_5)
    R4_ALLY_DESTROYED_MUSIC_STATE_GROUP = 'STATE_music_inBattle_phase'
    R4_ALLY_DESTROYED_MUSIC_STATE_DEFAULT = (R4_ALLY_DESTROYED_MUSIC_STATE_GROUP, 'STATE_music_inBattle_phase_start')
    R4_ALLY_DESTROYED_MUSIC_STATE_REMAIN_2 = (R4_ALLY_DESTROYED_MUSIC_STATE_GROUP, 'STATE_music_inBattle_phase_final')
    R4_ALLY_DESTROYED_MUSIC_STATE_REMAIN_5 = (R4_ALLY_DESTROYED_MUSIC_STATE_GROUP, 'STATE_music_inBattle_phase_middle')
    R4_ALLIES_REMAIN_MUSIC_STATES = {0: R4_ALLY_DESTROYED_MUSIC_STATE_REMAIN_2,
     1: R4_ALLY_DESTROYED_MUSIC_STATE_REMAIN_2,
     2: R4_ALLY_DESTROYED_MUSIC_STATE_REMAIN_2,
     3: R4_ALLY_DESTROYED_MUSIC_STATE_REMAIN_5,
     4: R4_ALLY_DESTROYED_MUSIC_STATE_REMAIN_5,
     5: R4_ALLY_DESTROYED_MUSIC_STATE_REMAIN_5}
    R4_ENEMY_DESTROYED_COUNTER_EVENTS = (None,
     R4_ENEMY_DESTROYED_COUNTER_1,
     R4_ENEMY_DESTROYED_COUNTER_2,
     R4_ENEMY_DESTROYED_COUNTER_3,
     R4_ENEMY_DESTROYED_COUNTER_4,
     R4_ENEMY_DESTROYED_COUNTER_5,
     R4_ENEMY_DESTROYED_COUNTER_6,
     R4_ENEMY_DESTROYED_COUNTER_7)
    R4_ENEMY_DESTROYED_REMAIN_EVENTS = (R4_ENEMY_DESTROYED_LAST,
     R4_ENEMY_DESTROYED_REMAIN_1,
     R4_ENEMY_DESTROYED_REMAIN_2,
     R4_ENEMY_DESTROYED_REMAIN_3,
     R4_ENEMY_DESTROYED_REMAIN_4,
     R4_ENEMY_DESTROYED_REMAIN_5)
    R4_MANNER_UI_EVENT_NAME = ''
    R4_MANNER_UI = 'r4_change_behavior_ui'
    R4_MANNER_ADAPTIVE = 'r4_change_behavior_adaptive'
    R4_MANNER_SCOUT = 'r4_change_behavior_scout'
    R4_MANNER_HOLDER = 'r4_change_behavior_holder'
    R4_MANNER_EVENTS = (R4_MANNER_ADAPTIVE, R4_MANNER_SCOUT, R4_MANNER_HOLDER)
    R4_ORDER_CAPTURE_BASE = 'r4_order_capture_base'
    R4_ORDER_CAPTURE_BASE_UI = 'r4_order_capture_base_ui'
    R4_ORDER_FIGHT_OFF_BASE = 'r4_order_fight_off_base'
    R4_ORDER_FIGHT_OFF_BASE_UI = 'r4_order_fight_off_base_ui'
    R4_ORDER_PROTECT_BASE = 'r4_order_protect_base'
    R4_ORDER_PROTECT_BASE_UI = 'r4_order_protect_base_ui'
    R4_ORDER_ATTACK = 'r4_order_attack'
    R4_ORDER_ATTACK_AGGRESSIVE = 'r4_order_attack_aggressive'
    R4_ORDER_ATTACK_UI = 'r4_order_attack_ui'
    R4_ORDER_ATTACK_AGGRESSIVE_UI = 'r4_order_attack_aggressive_ui'
    R4_ORDER_RETREAT = 'r4_order_retreat'
    R4_ORDER_RETREAT_UI = 'r4_order_retreat_ui'
    R4_ORDER_CANCEL = 'r4_order_cancel'
    R4_ORDER_TERRAIN_UNIVERSAL = 'r4_order_terrain_universal'
    R4_ORDER_TERRAIN_ADAPTIVE = 'r4_order_terrain_adaptive'
    R4_ORDER_TERRAIN_HOLDER = 'r4_order_terrain_holder'
    R4_ORDER_TERRAIN_SCOUT = 'r4_order_terrain_scout'
    R4_ORDER_TERRAIN_UI = 'r4_order_terrain_ui'
    R4_ORDER_TERRAIN_DOUBLE = 'r4_order_terrain_double'
    R4_ORDER_TERRAIN_DOUBLE_UI = 'r4_order_terrain_double_ui'
    R4_ORDER_EVENTS = (R4_ORDER_CAPTURE_BASE,
     R4_ORDER_FIGHT_OFF_BASE,
     R4_ORDER_PROTECT_BASE,
     R4_ORDER_ATTACK,
     R4_ORDER_TERRAIN_UNIVERSAL,
     R4_ORDER_TERRAIN_ADAPTIVE,
     R4_ORDER_TERRAIN_HOLDER,
     R4_ORDER_TERRAIN_SCOUT,
     R4_ORDER_ATTACK_AGGRESSIVE,
     R4_ORDER_TERRAIN_DOUBLE,
     R4_ORDER_RETREAT,
     R4_ORDER_CANCEL)
    R4_EVENTS_FORCED_TO_PLAY_IN_ARCADE_MODE = R4_ARCADE_WELCOME
    R4_GET_DESTINATION = 'r4_get_destination'
    R4_FIGHTING_OFF_BASE = 'r4_fighting_off_base'
    R4_DORMANT = 'r4_dormant'
    R4_DORMANT_ENEMY_SIGHT_RADIUS = 200
    R4_ALLY_CAPTURE_BASE = 'r4_ally_capture_base'
    R4_ENEMY_CAPTURE_BASE = 'r4_enemy_capture_base'
    R4_ALLY_CAPTURE_NEUTRAL_BASE = 'r4_ally_capture_neutral_base'
    R4_ENEMY_CAPTURE_NEUTRAL_BASE = 'r4_enemy_capture_neutral_base'
    R4_MUTED_SOUNDS = ('vehicle_destroyed', 'crew_deactivated', 'ally_killed_by_player', 'ally_killed_by_enemy ', 'track_damaged')
    R4_FOCUS_VEHICLE = 'r4_focus_vehicle'
    R4_ALLY_RELOAD = 'r4_automat_reloading'
    R4_ALLY_RELOAD_NON_EMPTY_CLIP = 'r4_automat_incomplete_reloading'
    R4_PILLBOX_FIRING_ACTIVE = 'r4_firing_point_active'
    R4_ALLY_FIRE_LINE_BLOCKED = {'SPG': 'r4_sau_hindrance'}
    R4_VO_LANGUAGE_SWITCH_GROUP_NAME = 'SWITCH_ext_r4_vo_language'
    R4_VOICE_OVER_SWITCH_NAME_NON_RU = 'SWITCH_ext_r4_vo_language_nonRU'
    R4_VOICE_OVER_SWITCH_NAME_RU = 'SWITCH_ext_r4_vo_language_RU'
    R4_VOICE_OVER_SWITCH_NAME_CN = 'SWITCH_ext_r4_vo_language_CN'
    R4_VOICE_LANGUAGE_SWTICH = {'RU': R4_VOICE_OVER_SWITCH_NAME_RU,
     'CN': R4_VOICE_OVER_SWITCH_NAME_CN}

    @staticmethod
    def getVoiceOverLanguageSwitch():
        switchName = R4_SOUND.R4_VOICE_LANGUAGE_SWTICH.get(CURRENT_REALM, R4_SOUND.R4_VOICE_OVER_SWITCH_NAME_NON_RU)
        return switchName


FIRST_SHOT_VOICE_LINES_BY_VEH_TAG = {RTSSupply.SUPPLY_ID_TO_TAG[RTSSupply.BUNKER]: R4_SOUND.R4_PILLBOX_FIRING_ACTIVE,
 RTSSupply.SUPPLY_ID_TO_TAG[RTSSupply.AT_GUN]: R4_SOUND.R4_PILLBOX_FIRING_ACTIVE,
 RTSSupply.SUPPLY_ID_TO_TAG[RTSSupply.PILLBOX]: R4_SOUND.R4_PILLBOX_FIRING_ACTIVE,
 RTSSupply.SUPPLY_ID_TO_TAG[RTSSupply.MORTAR]: R4_SOUND.R4_PILLBOX_FIRING_ACTIVE,
 RTSSupply.SUPPLY_ID_TO_TAG[RTSSupply.FLAMER]: R4_SOUND.R4_PILLBOX_FIRING_ACTIVE}
