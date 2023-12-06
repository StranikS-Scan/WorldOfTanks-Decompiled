# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/locale/INGAME_GUI.py
from debug_utils import LOG_WARNING

class INGAME_GUI(object):
    DEVICES_ENGINE = '#ingame_gui:devices/engine'
    DEVICES_AMMO_BAY = '#ingame_gui:devices/ammo_bay'
    DEVICES_FUEL_TANK = '#ingame_gui:devices/fuel_tank'
    DEVICES_RADIO = '#ingame_gui:devices/radio'
    DEVICES_TRACK = '#ingame_gui:devices/track'
    DEVICES_TRACK_LEFT = '#ingame_gui:devices/track/left'
    DEVICES_TRACK_RIGHT = '#ingame_gui:devices/track/right'
    DEVICES_TRACK_MAIN = '#ingame_gui:devices/track/main'
    DEVICES_TRACK_OUTER = '#ingame_gui:devices/track/outer'
    DEVICES_LEFT_TRACK = '#ingame_gui:devices/left_track'
    DEVICES_RIGHT_TRACK = '#ingame_gui:devices/right_track'
    DEVICES_GUN = '#ingame_gui:devices/gun'
    DEVICES_TURRET_ROTATOR = '#ingame_gui:devices/turret_rotator'
    DEVICES_SURVEING_DEVICE = '#ingame_gui:devices/surveing_device'
    DEVICES_CHASSIS = '#ingame_gui:devices/chassis'
    DEVICES_WHEEL = '#ingame_gui:devices/wheel'
    TANKMEN_COMMANDER = '#ingame_gui:tankmen/commander'
    TANKMEN_DRIVER = '#ingame_gui:tankmen/driver'
    TANKMEN_RADIOMAN = '#ingame_gui:tankmen/radioman'
    TANKMEN_GUNNER = '#ingame_gui:tankmen/gunner'
    TANKMEN_LOADER = '#ingame_gui:tankmen/loader'
    PLAYER_ERRORS_CANT_MOVE_CREW_INACTIVE = '#ingame_gui:player_errors/cant_move/crew_inactive'
    PLAYER_ERRORS_CANT_MOVE_ENGINE_DAMAGED = '#ingame_gui:player_errors/cant_move/engine_damaged'
    PLAYER_ERRORS_CANT_MOVE_CHASSIS_DAMAGED = '#ingame_gui:player_errors/cant_move/chassis_damaged'
    PLAYER_ERRORS_CANT_MOVE_VEHICLE_DESTROYED = '#ingame_gui:player_errors/cant_move/vehicle_destroyed'
    PLAYER_ERRORS_CANT_SHOOT_VEHICLE_DESTROYED = '#ingame_gui:player_errors/cant_shoot/vehicle_destroyed'
    PLAYER_ERRORS_CANT_SHOOT_CREW_INACTIVE = '#ingame_gui:player_errors/cant_shoot/crew_inactive'
    PLAYER_ERRORS_CANT_SHOOT_NO_AMMO = '#ingame_gui:player_errors/cant_shoot/no_ammo'
    PLAYER_ERRORS_CANT_SHOOT_NO_FLAME_AMMO = '#ingame_gui:player_errors/cant_shoot/no_flame_ammo'
    PLAYER_ERRORS_CANT_SHOOT_GUN_DAMAGED = '#ingame_gui:player_errors/cant_shoot/gun_damaged'
    PLAYER_ERRORS_CANT_SHOOT_GUN_RELOAD = '#ingame_gui:player_errors/cant_shoot/gun_reload'
    PLAYER_ERRORS_CANT_SHOOT_GUN_LOCKED = '#ingame_gui:player_errors/cant_shoot/gun_locked'
    PLAYER_ERRORS_CANT_SWITCH_ENGINE_DESTROYED = '#ingame_gui:player_errors/cant_switch/engine_destroyed'
    PLAYER_ERRORS_EQUIPMENT_ALREADYACTIVATED = '#ingame_gui:player_errors/equipment/alreadyActivated'
    PLAYER_ERRORS_EQUIPMENT_ISINCOOLDOWN = '#ingame_gui:player_errors/equipment/isInCooldown'
    PLAYER_ERRORS_EQUIPMENT_MEDKIT_TANKMANISSAFE = '#ingame_gui:player_errors/equipment/medkit/tankmanIsSafe'
    PLAYER_ERRORS_EQUIPMENT_MEDKIT_ALLTANKMENARESAFE = '#ingame_gui:player_errors/equipment/medkit/allTankmenAreSafe'
    PLAYER_ERRORS_EQUIPMENT_REPAIRKIT_DEVICEISNOTDAMAGED = '#ingame_gui:player_errors/equipment/repairkit/deviceIsNotDamaged'
    PLAYER_ERRORS_EQUIPMENT_REPAIRKIT_ALLDEVICESARENOTDAMAGED = '#ingame_gui:player_errors/equipment/repairkit/allDevicesAreNotDamaged'
    PLAYER_ERRORS_EQUIPMENT_REPAIREVERYTHING_CREWANDDEVICESAREOK = '#ingame_gui:player_errors/equipment/repairEverything/crewAndDevicesAreOk'
    PLAYER_ERRORS_EQUIPMENT_EXTINGUISHER_DOESNOTACTIVATED = '#ingame_gui:player_errors/equipment/extinguisher/doesNotActivated'
    PLAYER_ERRORS_EQUIPMENT_ORDER_NOTREADY = '#ingame_gui:player_errors/equipment/order/notReady'
    PLAYER_ERRORS_EQUIPMENT_POI_UNAVAILABLE = '#ingame_gui:player_errors/equipment/poi/unavailable'
    PLAYER_MESSAGES_DEVICE_CRITICAL_AT_SHOT = '#ingame_gui:player_messages/DEVICE_CRITICAL_AT_SHOT'
    PLAYER_MESSAGES_DEVICE_DESTROYED_AT_SHOT = '#ingame_gui:player_messages/DEVICE_DESTROYED_AT_SHOT'
    PLAYER_MESSAGES_DEVICE_STARTED_FIRE_AT_SHOT = '#ingame_gui:player_messages/DEVICE_STARTED_FIRE_AT_SHOT'
    PLAYER_MESSAGES_TANKMAN_HIT_AT_SHOT = '#ingame_gui:player_messages/TANKMAN_HIT_AT_SHOT'
    PLAYER_MESSAGES_DEVICE_CRITICAL_AT_FIRE = '#ingame_gui:player_messages/DEVICE_CRITICAL_AT_FIRE'
    PLAYER_MESSAGES_ENGINE_CRITICAL_AT_UNLIMITED_RPM = '#ingame_gui:player_messages/ENGINE_CRITICAL_AT_UNLIMITED_RPM'
    PLAYER_MESSAGES_ENGINE_DESTROYED_AT_UNLIMITED_RPM = '#ingame_gui:player_messages/ENGINE_DESTROYED_AT_UNLIMITED_RPM'
    PLAYER_MESSAGES_ENGINE_CRITICAL_AT_BURNOUT = '#ingame_gui:player_messages/ENGINE_CRITICAL_AT_BURNOUT'
    PLAYER_MESSAGES_ENGINE_DESTROYED_AT_BURNOUT = '#ingame_gui:player_messages/ENGINE_DESTROYED_AT_BURNOUT'
    PLAYER_MESSAGES_DEVICE_DESTROYED_AT_FIRE = '#ingame_gui:player_messages/DEVICE_DESTROYED_AT_FIRE'
    PLAYER_MESSAGES_DEVICE_REPAIRED_TO_CRITICAL = '#ingame_gui:player_messages/DEVICE_REPAIRED_TO_CRITICAL'
    PLAYER_MESSAGES_FIRE_STOPPED = '#ingame_gui:player_messages/FIRE_STOPPED'
    PLAYER_MESSAGES_OPT_DEVICE_USED = '#ingame_gui:player_messages/OPT_DEVICE_USED'
    PLAYER_MESSAGES_TANKMAN_RESTORED = '#ingame_gui:player_messages/TANKMAN_RESTORED'
    PLAYER_MESSAGES_DEVICE_REPAIRED = '#ingame_gui:player_messages/DEVICE_REPAIRED'
    PLAYER_MESSAGES_ALLY_HIT = '#ingame_gui:player_messages/ALLY_HIT'
    PLAYER_MESSAGES_ALLY_BASE_CAPTURED_NOTIFICATION = '#ingame_gui:player_messages/ally_base_captured_notification'
    PLAYER_MESSAGES_ENEMY_BASE_CAPTURED_NOTIFICATION = '#ingame_gui:player_messages/enemy_base_captured_notification'
    PLAYER_MESSAGES_BASE_CAPTURED_NOTIFICATION = '#ingame_gui:player_messages/base_captured_notification'
    PLAYER_MESSAGES_ALLY_BASE_CAPTURED_BY_NOTIFICATION = '#ingame_gui:player_messages/ally_base_captured_by_notification'
    PLAYER_MESSAGES_ENEMY_BASE_CAPTURED_BY_NOTIFICATION = '#ingame_gui:player_messages/enemy_base_captured_by_notification'
    PLAYER_MESSAGES_BASE_CAPTURED_BY_NOTIFICATION = '#ingame_gui:player_messages/base_captured_by_notification'
    PLAYER_MESSAGES_BASE_CAPTURE_BLOCKED = '#ingame_gui:player_messages/base_capture_blocked'
    PLAYER_MESSAGES_ALLIED_TEAM_NAME = '#ingame_gui:player_messages/allied_team_name'
    PLAYER_MESSAGES_ENEMY_TEAM_NAME = '#ingame_gui:player_messages/enemy_team_name'
    PLAYER_MESSAGES_POSTMORTEM_CAPTION = '#ingame_gui:player_messages/postmortem_caption'
    PLAYER_MESSAGES_POSTMORTEM_CAPTION_SELF = '#ingame_gui:player_messages/postmortem_caption/self'
    PLAYER_MESSAGES_POSTMORTEM_CAPTION_OTHER = '#ingame_gui:player_messages/postmortem_caption/other'
    PLAYER_MESSAGES_POSTMORTEM_USERNOHASAMMO = '#ingame_gui:player_messages/postmortem_userNoHasAmmo'
    PLAYER_MESSAGES_TANK_IN_FIRE = '#ingame_gui:player_messages/tank_in_fire'
    PLAYER_MESSAGES_POI_EQUIPMENT_USED_BY_ALLY = '#ingame_gui:player_messages/poi_equipment_used_by_ally'
    PLAYER_MESSAGES_POI_EQUIPMENT_USED_BY_ENEMY = '#ingame_gui:player_messages/poi_equipment_used_by_enemy'
    VEHICLE_MESSAGES_POI_EQUIPMENT_USED = '#ingame_gui:vehicle_messages/poi_equipment_used'
    PLAYER_MESSAGES_REPLAYFREECAMERAACTIVATED = '#ingame_gui:player_messages/replayFreeCameraActivated'
    PLAYER_MESSAGES_REPLAYSAVEDCAMERAACTIVATED = '#ingame_gui:player_messages/replaySavedCameraActivated'
    PLAYER_MESSAGES_REPLAYSPEEDCHANGE = '#ingame_gui:player_messages/replaySpeedChange'
    PLAYER_MESSAGES_REPLAYPAUSED = '#ingame_gui:player_messages/replayPaused'
    PLAYER_MESSAGES_REPLAYCONTROLSHELP1 = '#ingame_gui:player_messages/replayControlsHelp1'
    PLAYER_MESSAGES_REPLAYCONTROLSHELP2 = '#ingame_gui:player_messages/replayControlsHelp2'
    PLAYER_MESSAGES_REPLAYCONTROLSHELP3 = '#ingame_gui:player_messages/replayControlsHelp3'
    CHAT_SHORTCUTS_ATTENTION_TO_POSITION_GRIDINFO = '#ingame_gui:chat_shortcuts/attention_to_position_gridInfo'
    CHAT_SHORTCUTS_ATTENTION_TO_POSITION = '#ingame_gui:chat_shortcuts/attention_to_position'
    CHAT_SHORTCUTS_GOING_THERE_GRIDINFO = '#ingame_gui:chat_shortcuts/going_there_gridInfo'
    CHAT_SHORTCUTS_GOING_THERE = '#ingame_gui:chat_shortcuts/going_there'
    CHAT_SHORTCUTS_HELP_ME = '#ingame_gui:chat_shortcuts/help_me'
    CHAT_SHORTCUTS_RELOADING_GUN = '#ingame_gui:chat_shortcuts/reloading_gun'
    CHAT_SHORTCUTS_RELOADING_CASSETTE = '#ingame_gui:chat_shortcuts/reloading_cassette'
    CHAT_SHORTCUTS_RELOADING_READY = '#ingame_gui:chat_shortcuts/reloading_ready'
    CHAT_SHORTCUTS_RELOADING_READY_CASSETTE = '#ingame_gui:chat_shortcuts/reloading_ready_cassette'
    CHAT_SHORTCUTS_RELOADING_UNAVAILABLE = '#ingame_gui:chat_shortcuts/reloading_unavailable'
    CHAT_SHORTCUTS_SPG_AIM_AREA_GRIDINFO = '#ingame_gui:chat_shortcuts/spg_aim_area_gridInfo'
    CHAT_SHORTCUTS_SPG_AIM_AREA = '#ingame_gui:chat_shortcuts/spg_aim_area'
    CHAT_SHORTCUTS_SPG_AIM_AREA_RELOADING_GRIDINFO = '#ingame_gui:chat_shortcuts/spg_aim_area_reloading_gridInfo'
    CHAT_SHORTCUTS_SPG_AIM_AREA_RELOADING = '#ingame_gui:chat_shortcuts/spg_aim_area_reloading'
    CHAT_SHORTCUTS_SPG_AIM_AREA_EMPTY_GRIDINFO = '#ingame_gui:chat_shortcuts/spg_aim_area_empty_gridInfo'
    CHAT_SHORTCUTS_ATTACK_ENEMY = '#ingame_gui:chat_shortcuts/attack_enemy'
    CHAT_SHORTCUTS_ATTACKING_ENEMY = '#ingame_gui:chat_shortcuts/attacking_enemy'
    CHAT_SHORTCUTS_ATTACK_ENEMY_WITH_SPG = '#ingame_gui:chat_shortcuts/attack_enemy_with_SPG'
    CHAT_SHORTCUTS_ATTACK_ENEMY_WITH_SPG_EMPTY = '#ingame_gui:chat_shortcuts/attack_enemy_with_SPG_empty'
    CHAT_SHORTCUTS_ATTACK_ENEMY_WITH_SPG_RELOADING = '#ingame_gui:chat_shortcuts/attack_enemy_with_SPG_reloading'
    CHAT_SHORTCUTS_ATTENTION_TO_BASE_ATK = '#ingame_gui:chat_shortcuts/attention_to_base_atk'
    CHAT_SHORTCUTS_ATTENTION_TO_BASE_ATK_NUMBERED = '#ingame_gui:chat_shortcuts/attention_to_base_atk_numbered'
    CHAT_SHORTCUTS_ATTACKING_BASE = '#ingame_gui:chat_shortcuts/attacking_base'
    CHAT_SHORTCUTS_ATTACKING_BASE_NUMBERED = '#ingame_gui:chat_shortcuts/attacking_base_numbered'
    CHAT_SHORTCUTS_ATTENTION_TO_OBJECTIVE_ATK = '#ingame_gui:chat_shortcuts/attention_to_objective_atk'
    CHAT_SHORTCUTS_ATTENTION_TO_OBJECTIVE_ATK_AUTOCOMMIT = '#ingame_gui:chat_shortcuts/attention_to_objective_atk_autocommit'
    CHAT_SHORTCUTS_ATTENTION_TO_BASE_DEF = '#ingame_gui:chat_shortcuts/attention_to_base_def'
    CHAT_SHORTCUTS_ATTENTION_TO_BASE_DEF_NUMBERED = '#ingame_gui:chat_shortcuts/attention_to_base_def_numbered'
    CHAT_SHORTCUTS_DEFENDING_BASE = '#ingame_gui:chat_shortcuts/defending_base'
    CHAT_SHORTCUTS_DEFENDING_BASE_NUMBERED = '#ingame_gui:chat_shortcuts/defending_base_numbered'
    CHAT_SHORTCUTS_ATTENTION_TO_OBJECTIVE_DEF = '#ingame_gui:chat_shortcuts/attention_to_objective_def'
    CHAT_SHORTCUTS_ATTENTION_TO_OBJECTIVE_DEF_AUTOCOMMIT = '#ingame_gui:chat_shortcuts/attention_to_objective_def_autocommit'
    CHAT_SHORTCUTS_HELP_ME_EX = '#ingame_gui:chat_shortcuts/help_me_ex'
    CHAT_SHORTCUTS_SUPPORTING_ALLY = '#ingame_gui:chat_shortcuts/supporting_ally'
    CHAT_SHORTCUTS_TURN_BACK = '#ingame_gui:chat_shortcuts/turn_back'
    CHAT_SHORTCUTS_THANKS = '#ingame_gui:chat_shortcuts/thanks'
    CHAT_SHORTCUTS_POSITIVE = '#ingame_gui:chat_shortcuts/positive'
    CHAT_SHORTCUTS_AFFIRMATIVE = '#ingame_gui:chat_shortcuts/affirmative'
    CHAT_SHORTCUTS_NEGATIVE = '#ingame_gui:chat_shortcuts/negative'
    CHAT_SHORTCUTS_ATTENTION_TO_CELL = '#ingame_gui:chat_shortcuts/attention_to_cell'
    CHAT_SHORTCUTS_GLOBAL_MSG_ATK_SAVE_TANKS = '#ingame_gui:chat_shortcuts/global_msg/atk/save_tanks'
    CHAT_SHORTCUTS_GLOBAL_MSG_DEF_SAVE_TANKS = '#ingame_gui:chat_shortcuts/global_msg/def/save_tanks'
    CHAT_SHORTCUTS_GLOBAL_MSG_ATK_TIME = '#ingame_gui:chat_shortcuts/global_msg/atk/time'
    CHAT_SHORTCUTS_GLOBAL_MSG_DEF_TIME = '#ingame_gui:chat_shortcuts/global_msg/def/time'
    CHAT_SHORTCUTS_GLOBAL_MSG_LANE_WEST = '#ingame_gui:chat_shortcuts/global_msg/lane/west'
    CHAT_SHORTCUTS_GLOBAL_MSG_LANE_CENTER = '#ingame_gui:chat_shortcuts/global_msg/lane/center'
    CHAT_SHORTCUTS_GLOBAL_MSG_LANE_EAST = '#ingame_gui:chat_shortcuts/global_msg/lane/east'
    CHAT_SHORTCUTS_GLOBAL_MSG_ATK_FOCUS_HQ = '#ingame_gui:chat_shortcuts/global_msg/atk/focus_hq'
    CHAT_SHORTCUTS_GLOBAL_MSG_DEF_FOCUS_HQ = '#ingame_gui:chat_shortcuts/global_msg/def/focus_hq'
    CHAT_EXAMPLE_ATTENTION_TO_BASE_DEF = '#ingame_gui:chat_example/attention_to_base_def'
    CHAT_EXAMPLE_ATTENTION_TO_BASE_ATK = '#ingame_gui:chat_example/attention_to_base_atk'
    CHAT_EXAMPLE_GOING_THERE = '#ingame_gui:chat_example/going_there'
    CHAT_EXAMPLE_GLOBAL_MSG_DEF_SAVE_TANKS = '#ingame_gui:chat_example/global_msg/def/save_tanks'
    MARKER_METERS = '#ingame_gui:marker/meters'
    CHAT_EXAMPLE_GLOBAL_MSG_ATK_SAVE_TANKS = '#ingame_gui:chat_example/global_msg/atk/save_tanks'
    CHAT_EXAMPLE_GLOBAL_MSG_ATK_TIME = '#ingame_gui:chat_example/global_msg/atk/time'
    CHAT_EXAMPLE_GLOBAL_MSG_DEF_TIME = '#ingame_gui:chat_example/global_msg/def/time'
    CHAT_EXAMPLE_GLOBAL_MSG_LANE_WEST = '#ingame_gui:chat_example/global_msg/lane/west'
    CHAT_EXAMPLE_GLOBAL_MSG_LANE_CENTER = '#ingame_gui:chat_example/global_msg/lane/center'
    CHAT_EXAMPLE_GLOBAL_MSG_LANE_EAST = '#ingame_gui:chat_example/global_msg/lane/east'
    CHAT_EXAMPLE_GLOBAL_MSG_ATK_FOCUS_HQ = '#ingame_gui:chat_example/global_msg/atk/focus_hq'
    CHAT_EXAMPLE_GLOBAL_MSG_DEF_FOCUS_HQ = '#ingame_gui:chat_example/global_msg/def/focus_hq'
    CHAT_EXAMPLE_ATTACK_ENEMY = '#ingame_gui:chat_example/attack_enemy'
    CHAT_EXAMPLE_RELOADING_GUN = '#ingame_gui:chat_example/reloading_gun'
    CHAT_EXAMPLE_RELOADING_CASSETTE = '#ingame_gui:chat_example/reloading_cassette'
    CHAT_EXAMPLE_RELOADING_READY = '#ingame_gui:chat_example/reloading_ready'
    CHAT_EXAMPLE_TURN_BACK = '#ingame_gui:chat_example/turn_back'
    CHAT_EXAMPLE_RELOADING_READY_CASSETTE = '#ingame_gui:chat_example/reloading_ready_cassette'
    CHAT_EXAMPLE_RELOADING_UNAVAILABLE = '#ingame_gui:chat_example/reloading_unavailable'
    CHAT_EXAMPLE_HELP_ME = '#ingame_gui:chat_example/help_me'
    CHAT_EXAMPLE_HELP_ME_EX = '#ingame_gui:chat_example/help_me_ex'
    CHAT_EXAMPLE_POSITIVE = '#ingame_gui:chat_example/positive'
    CHAT_EXAMPLE_AFFIRMATIVE = '#ingame_gui:chat_example/affirmative'
    CHAT_EXAMPLE_NEGATIVE = '#ingame_gui:chat_example/negative'
    CHAT_EXAMPLE_THANKS = '#ingame_gui:chat_example/thanks'
    CHAT_EXAMPLE_ATTENTION_TO_CELL = '#ingame_gui:chat_example/attention_to_cell'
    CHAT_EXAMPLE_ATTACK_ENEMY_WITH_SPG = '#ingame_gui:chat_example/attack_enemy_with_SPG'
    CHAT_EXAMPLE_SPG_AIM_AREA = '#ingame_gui:chat_example/spg_aim_area'
    CHAT_EXAMPLE_ATTENTION_TO_POSITION = '#ingame_gui:chat_example/attention_to_position'
    CHAT_EXAMPLE_SUPPORTING_ALLY = '#ingame_gui:chat_example/supporting_ally'
    STATISTICS_TAB_LINE_UP_HEADER = '#ingame_gui:statistics/tab/line_up/header'
    STATISTICS_TAB_LINE_UP_TITLE = '#ingame_gui:statistics/tab/line_up/title'
    STATISTICS_TAB_QUESTS_HEADER = '#ingame_gui:statistics/tab/quests/header'
    STATISTICS_TAB_QUESTS_STATUS_INPROGRESS = '#ingame_gui:statistics/tab/quests/status/inProgress'
    STATISTICS_TAB_QUESTS_STATUS_ONPAUSE = '#ingame_gui:statistics/tab/quests/status/onPause'
    STATISTICS_TAB_QUESTS_STATUS_INCREASERESULT = '#ingame_gui:statistics/tab/quests/status/increaseResult'
    STATISTICS_TAB_QUESTS_STATUS_DONE = '#ingame_gui:statistics/tab/quests/status/done'
    STATISTICS_TAB_QUESTS_STATUS_FULLDONE = '#ingame_gui:statistics/tab/quests/status/fullDone'
    STATISTICS_TAB_QUESTS_NOTHINGTOPERFORM_TITLE = '#ingame_gui:statistics/tab/quests/nothingToPerform/title'
    STATISTICS_TAB_QUESTS_NOTHINGTOPERFORM_DESCR = '#ingame_gui:statistics/tab/quests/nothingToPerform/descr'
    STATISTICS_TAB_QUESTS_SWITCHOFF_TITLE = '#ingame_gui:statistics/tab/quests/switchOff/title'
    STATISTICS_TAB_QUESTS_NOTAVAILABLE_TITLE = '#ingame_gui:statistics/tab/quests/notAvailable/title'
    STATISTICS_TAB_PERSONALRESERVES_HEADER = '#ingame_gui:statistics/tab/personalReserves/header'
    STATISTICS_TAB_PERSONALRESERVES_HEADER_TITLE = '#ingame_gui:statistics/tab/personalReserves/header/title'
    STATISTICS_HEADER = '#ingame_gui:statistics/header'
    STATISTICS_TEAM1TITLE = '#ingame_gui:statistics/team1title'
    STATISTICS_TEAM2TITLE = '#ingame_gui:statistics/team2title'
    STATISTICS_HEADERS_HEADER0 = '#ingame_gui:statistics/headers/header0'
    STATISTICS_HEADERS_HEADER1 = '#ingame_gui:statistics/headers/header1'
    STATISTICS_HEADERS_HEADER2 = '#ingame_gui:statistics/headers/header2'
    STATISTICS_HEADERS_HEADER3 = '#ingame_gui:statistics/headers/header3'
    STATISTICS_HEADERS_HEADER4 = '#ingame_gui:statistics/headers/header4'
    STATISTICS_TABS_GROUP = '#ingame_gui:statistics/tabs/group'
    STATISTICS_TABS_PERSONAL = '#ingame_gui:statistics/tabs/personal'
    STATISTICS_TABS_HEROES = '#ingame_gui:statistics/tabs/heroes'
    STATISTICS_EXIT = '#ingame_gui:statistics/exit'
    STATISTICS_FINAL_STATUS_TIE = '#ingame_gui:statistics/final/status/tie'
    STATISTICS_FINAL_STATUS_WIN = '#ingame_gui:statistics/final/status/win'
    STATISTICS_FINAL_STATUS_LOSE = '#ingame_gui:statistics/final/status/lose'
    BATTLE_NOTIFIER_TIE = '#ingame_gui:battle_notifier/tie'
    BATTLE_NOTIFIER_WIN = '#ingame_gui:battle_notifier/win'
    BATTLE_NOTIFIER_LOSE = '#ingame_gui:battle_notifier/lose'
    STATISTICS_FINAL_REASONS_REASON0 = '#ingame_gui:statistics/final/reasons/reason0'
    STATISTICS_FINAL_REASONS_REASON1WIN = '#ingame_gui:statistics/final/reasons/reason1win'
    STATISTICS_FINAL_REASONS_REASON1LOSE = '#ingame_gui:statistics/final/reasons/reason1lose'
    STATISTICS_FINAL_REASONS_REASON1TIE = '#ingame_gui:statistics/final/reasons/reason1tie'
    STATISTICS_FINAL_REASONS_REASON2 = '#ingame_gui:statistics/final/reasons/reason2'
    STATISTICS_FINAL_REASONS_REASON3 = '#ingame_gui:statistics/final/reasons/reason3'
    STATISTICS_FINAL_STATS_MULTIPLIEDEXP = '#ingame_gui:statistics/final/stats/multipliedExp'
    STATISTICS_FINAL_STATS_EXPERIENCE = '#ingame_gui:statistics/final/stats/experience'
    STATISTICS_FINAL_STATS_CREDITS = '#ingame_gui:statistics/final/stats/credits'
    STATISTICS_FINAL_STATS_REPAIR = '#ingame_gui:statistics/final/stats/repair'
    STATISTICS_FINAL_PERSONAL_POSTMORTEM = '#ingame_gui:statistics/final/personal/postmortem'
    STATISTICS_FINAL_PERSONAL_KILLED = '#ingame_gui:statistics/final/personal/killed'
    STATISTICS_FINAL_PERSONAL_DAMAGED = '#ingame_gui:statistics/final/personal/damaged'
    STATISTICS_FINAL_PERSONAL_SPOTTED = '#ingame_gui:statistics/final/personal/spotted'
    STATISTICS_FINAL_PERSONAL_SHOTS = '#ingame_gui:statistics/final/personal/shots'
    STATISTICS_FINAL_PERSONAL_DIRECTHITS = '#ingame_gui:statistics/final/personal/directHits'
    STATISTICS_FINAL_PERSONAL_DIRECTHITSRECEIVED = '#ingame_gui:statistics/final/personal/directHitsReceived'
    STATISTICS_FINAL_PERSONAL_CAPTUREPOINTS = '#ingame_gui:statistics/final/personal/capturePoints'
    STATISTICS_FINAL_PERSONAL_DROPPEDCAPTUREPOINTS = '#ingame_gui:statistics/final/personal/droppedCapturePoints'
    STATISTICS_FINAL_HEROES = '#ingame_gui:statistics/final/heroes'
    STATISTICS_FINAL_LIFEINFO_ALIVE = '#ingame_gui:statistics/final/lifeInfo/alive'
    STATISTICS_FINAL_LIFEINFO_DEAD = '#ingame_gui:statistics/final/lifeInfo/dead'
    STATISTICS_PLAYERSTATE_0 = '#ingame_gui:statistics/playerState/0'
    STATISTICS_PLAYERSTATE_2 = '#ingame_gui:statistics/playerState/2'
    STATISTICS_PLAYERSTATE_1 = '#ingame_gui:statistics/playerState/1'
    STATISTICS_PLAYERSTATE_3 = '#ingame_gui:statistics/playerState/3'
    STATISTICS_PLAYERSTATE_4 = '#ingame_gui:statistics/playerState/4'
    SHELLS_KINDS_HOLLOW_CHARGE = '#ingame_gui:shells_kinds/HOLLOW_CHARGE'
    SHELLS_KINDS_HIGH_EXPLOSIVE = '#ingame_gui:shells_kinds/HIGH_EXPLOSIVE'
    SHELLS_KINDS_ARMOR_PIERCING = '#ingame_gui:shells_kinds/ARMOR_PIERCING'
    SHELLS_KINDS_ARMOR_PIERCING_HE = '#ingame_gui:shells_kinds/ARMOR_PIERCING_HE'
    SHELLS_KINDS_ARMOR_PIERCING_CR = '#ingame_gui:shells_kinds/ARMOR_PIERCING_CR'
    SHELLS_KINDS_FLAME = '#ingame_gui:shells_kinds/FLAME'
    SHELLS_KINDS_PARAMS_DAMAGE = '#ingame_gui:shells_kinds/params/damage'
    SHELLS_KINDS_PARAMS_PIERCINGPOWER = '#ingame_gui:shells_kinds/params/piercingPower'
    SHELLS_KINDS_PARAMS_SHOTSPEED = '#ingame_gui:shells_kinds/params/shotSpeed'
    SHELLS_KINDS_PARAMS_EXPLOSIONRADIUS = '#ingame_gui:shells_kinds/params/explosionRadius'
    SHELLS_KINDS_PARAMS_STUNDURATION = '#ingame_gui:shells_kinds/params/stunDuration'
    DAMAGE_PANEL_DEVICES_TURRETROTATOR_NORMAL = '#ingame_gui:damage_panel/devices/turretRotator/normal'
    DAMAGE_PANEL_DEVICES_TURRETROTATOR_CRITICAL = '#ingame_gui:damage_panel/devices/turretRotator/critical'
    DAMAGE_PANEL_DEVICES_TURRETROTATOR_DESTROYED = '#ingame_gui:damage_panel/devices/turretRotator/destroyed'
    DAMAGE_PANEL_DEVICES_ENGINE_NORMAL = '#ingame_gui:damage_panel/devices/engine/normal'
    DAMAGE_PANEL_DEVICES_ENGINE_CRITICAL = '#ingame_gui:damage_panel/devices/engine/critical'
    DAMAGE_PANEL_DEVICES_ENGINE_DESTROYED = '#ingame_gui:damage_panel/devices/engine/destroyed'
    DAMAGE_PANEL_DEVICES_GUN_NORMAL = '#ingame_gui:damage_panel/devices/gun/normal'
    DAMAGE_PANEL_DEVICES_GUN_CRITICAL = '#ingame_gui:damage_panel/devices/gun/critical'
    DAMAGE_PANEL_DEVICES_GUN_DESTROYED = '#ingame_gui:damage_panel/devices/gun/destroyed'
    DAMAGE_PANEL_DEVICES_AMMOBAY_NORMAL = '#ingame_gui:damage_panel/devices/ammoBay/normal'
    DAMAGE_PANEL_DEVICES_AMMOBAY_CRITICAL = '#ingame_gui:damage_panel/devices/ammoBay/critical'
    DAMAGE_PANEL_DEVICES_AMMOBAY_DESTROYED = '#ingame_gui:damage_panel/devices/ammoBay/destroyed'
    DAMAGE_PANEL_DEVICES_TRACK_NORMAL = '#ingame_gui:damage_panel/devices/track/normal'
    DAMAGE_PANEL_DEVICES_TRACK_CRITICAL = '#ingame_gui:damage_panel/devices/track/critical'
    DAMAGE_PANEL_DEVICES_TRACK_DESTROYED = '#ingame_gui:damage_panel/devices/track/destroyed'
    DAMAGE_PANEL_DEVICES_CHASSIS_NORMAL = '#ingame_gui:damage_panel/devices/chassis/normal'
    DAMAGE_PANEL_DEVICES_CHASSIS_CRITICAL = '#ingame_gui:damage_panel/devices/chassis/critical'
    DAMAGE_PANEL_DEVICES_CHASSIS_DESTROYED = '#ingame_gui:damage_panel/devices/chassis/destroyed'
    DAMAGE_PANEL_DEVICES_WHEEL_NORMAL = '#ingame_gui:damage_panel/devices/wheel/normal'
    DAMAGE_PANEL_DEVICES_WHEEL_CRITICAL = '#ingame_gui:damage_panel/devices/wheel/critical'
    DAMAGE_PANEL_DEVICES_WHEEL_DESTROYED = '#ingame_gui:damage_panel/devices/wheel/destroyed'
    DAMAGE_PANEL_DEVICES_RADIO_NORMAL = '#ingame_gui:damage_panel/devices/radio/normal'
    DAMAGE_PANEL_DEVICES_RADIO_CRITICAL = '#ingame_gui:damage_panel/devices/radio/critical'
    DAMAGE_PANEL_DEVICES_RADIO_DESTROYED = '#ingame_gui:damage_panel/devices/radio/destroyed'
    DAMAGE_PANEL_DEVICES_FUELTANK_NORMAL = '#ingame_gui:damage_panel/devices/fuelTank/normal'
    DAMAGE_PANEL_DEVICES_FUELTANK_CRITICAL = '#ingame_gui:damage_panel/devices/fuelTank/critical'
    DAMAGE_PANEL_DEVICES_FUELTANK_DESTROYED = '#ingame_gui:damage_panel/devices/fuelTank/destroyed'
    DAMAGE_PANEL_DEVICES_SURVEYINGDEVICE_NORMAL = '#ingame_gui:damage_panel/devices/surveyingDevice/normal'
    DAMAGE_PANEL_DEVICES_SURVEYINGDEVICE_CRITICAL = '#ingame_gui:damage_panel/devices/surveyingDevice/critical'
    DAMAGE_PANEL_DEVICES_SURVEYINGDEVICE_DESTROYED = '#ingame_gui:damage_panel/devices/surveyingDevice/destroyed'
    DAMAGE_PANEL_CREW_COMMANDER_NORMAL = '#ingame_gui:damage_panel/crew/commander/normal'
    DAMAGE_PANEL_CREW_COMMANDER_DESTROYED = '#ingame_gui:damage_panel/crew/commander/destroyed'
    DAMAGE_PANEL_CREW_DRIVER_NORMAL = '#ingame_gui:damage_panel/crew/driver/normal'
    DAMAGE_PANEL_CREW_DRIVER_DESTROYED = '#ingame_gui:damage_panel/crew/driver/destroyed'
    DAMAGE_PANEL_CREW_RADIOMAN1_NORMAL = '#ingame_gui:damage_panel/crew/radioman1/normal'
    DAMAGE_PANEL_CREW_RADIOMAN1_DESTROYED = '#ingame_gui:damage_panel/crew/radioman1/destroyed'
    DAMAGE_PANEL_CREW_RADIOMAN2_NORMAL = '#ingame_gui:damage_panel/crew/radioman2/normal'
    DAMAGE_PANEL_CREW_RADIOMAN2_DESTROYED = '#ingame_gui:damage_panel/crew/radioman2/destroyed'
    DAMAGE_PANEL_CREW_GUNNER1_NORMAL = '#ingame_gui:damage_panel/crew/gunner1/normal'
    DAMAGE_PANEL_CREW_GUNNER1_DESTROYED = '#ingame_gui:damage_panel/crew/gunner1/destroyed'
    DAMAGE_PANEL_CREW_GUNNER2_NORMAL = '#ingame_gui:damage_panel/crew/gunner2/normal'
    DAMAGE_PANEL_CREW_GUNNER2_DESTROYED = '#ingame_gui:damage_panel/crew/gunner2/destroyed'
    DAMAGE_PANEL_CREW_LOADER1_NORMAL = '#ingame_gui:damage_panel/crew/loader1/normal'
    DAMAGE_PANEL_CREW_LOADER1_DESTROYED = '#ingame_gui:damage_panel/crew/loader1/destroyed'
    DAMAGE_PANEL_CREW_LOADER2_NORMAL = '#ingame_gui:damage_panel/crew/loader2/normal'
    DAMAGE_PANEL_CREW_LOADER2_DESTROYED = '#ingame_gui:damage_panel/crew/loader2/destroyed'
    CRUISE_CTRL_SPEEDMETRIC = '#ingame_gui:cruise_ctrl/speedMetric'
    CONSUMABLES_PANEL_EQUIPMENT_TOOLTIP_EMPTY = '#ingame_gui:consumables_panel/equipment/tooltip/empty'
    CONSUMABLES_PANEL_EQUIPMENT_COOLDOWNSECONDS = '#ingame_gui:consumables_panel/equipment/cooldownSeconds'
    CONSUMABLES_PANEL_EQUIPMENT_ACTIVESECONDS = '#ingame_gui:consumables_panel/equipment/activeSeconds'
    TIMER_WAITING = '#ingame_gui:timer/waiting'
    TIMER_STARTING = '#ingame_gui:timer/starting'
    TIMER_STARTED = '#ingame_gui:timer/started'
    TIMER_BATTLEPERIOD = '#ingame_gui:timer/battlePeriod'
    POSTMORTEM_TIPS_OBSERVERMODE_LABEL = '#ingame_gui:postmortem/tips/observerMode/label'
    POSTMORTEM_TIPS_OBSERVERMODE_TEXT = '#ingame_gui:postmortem/tips/observerMode/text'
    POSTMORTEM_TIPS_EXITHANGAR_LABEL = '#ingame_gui:postmortem/tips/exitHangar/label'
    POSTMORTEM_TIPS_EXITHANGAR_TEXT = '#ingame_gui:postmortem/tips/exitHangar/text'
    PLAYERS_PANEL_STATE_NONE_HEADER = '#ingame_gui:players_panel/state/none/header'
    PLAYERS_PANEL_STATE_NONE_BODY = '#ingame_gui:players_panel/state/none/body'
    PLAYERS_PANEL_STATE_NONE_NOTE = '#ingame_gui:players_panel/state/none/note'
    PLAYERS_PANEL_STATE_SHORT_HEADER = '#ingame_gui:players_panel/state/short/header'
    PLAYERS_PANEL_STATE_SHORT_BODY = '#ingame_gui:players_panel/state/short/body'
    PLAYERS_PANEL_STATE_SHORT_NOTE = '#ingame_gui:players_panel/state/short/note'
    PLAYERS_PANEL_STATE_MEDIUM_HEADER = '#ingame_gui:players_panel/state/medium/header'
    PLAYERS_PANEL_STATE_MEDIUM_BODY = '#ingame_gui:players_panel/state/medium/body'
    PLAYERS_PANEL_STATE_MEDIUM_NOTE = '#ingame_gui:players_panel/state/medium/note'
    PLAYERS_PANEL_STATE_MEDIUM2_HEADER = '#ingame_gui:players_panel/state/medium2/header'
    PLAYERS_PANEL_STATE_MEDIUM2_BODY = '#ingame_gui:players_panel/state/medium2/body'
    PLAYERS_PANEL_STATE_MEDIUM2_NOTE = '#ingame_gui:players_panel/state/medium2/note'
    PLAYERS_PANEL_STATE_LARGE_HEADER = '#ingame_gui:players_panel/state/large/header'
    PLAYERS_PANEL_STATE_LARGE_BODY = '#ingame_gui:players_panel/state/large/body'
    PLAYERS_PANEL_STATE_LARGE_NOTE = '#ingame_gui:players_panel/state/large/note'
    PLAYERS_PANEL_UNKNOWN_NAME = '#ingame_gui:players_panel/unknown_name'
    PLAYERS_PANEL_UNKNOWN_VEHICLE = '#ingame_gui:players_panel/unknown_vehicle'
    PLAYERS_PANEL_UNKNOWN_FRAGS = '#ingame_gui:players_panel/unknown_frags'
    PLAYERS_PANEL_UNKNOWN_VEHICLESTATE = '#ingame_gui:players_panel/unknown_vehicleState'
    PLAYERS_PANEL_UNKNOWN_CLAN = '#ingame_gui:players_panel/unknown_clan'
    EPIC_PLAYERS_PANEL_STATE_HIDDEN_HEADER = '#ingame_gui:epic_players_panel/state/hidden/header'
    EPIC_PLAYERS_PANEL_STATE_HIDDEN_BODY = '#ingame_gui:epic_players_panel/state/hidden/body'
    EPIC_PLAYERS_PANEL_STATE_HIDDEN_NOTE = '#ingame_gui:epic_players_panel/state/hidden/note'
    EPIC_PLAYERS_PANEL_STATE_SHORT_HEADER = '#ingame_gui:epic_players_panel/state/short/header'
    EPIC_PLAYERS_PANEL_STATE_SHORT_BODY = '#ingame_gui:epic_players_panel/state/short/body'
    EPIC_PLAYERS_PANEL_STATE_SHORT_NOTE = '#ingame_gui:epic_players_panel/state/short/note'
    EPIC_PLAYERS_PANEL_STATE_MEDIUM_PLAYER_HEADER = '#ingame_gui:epic_players_panel/state/medium_player/header'
    EPIC_PLAYERS_PANEL_STATE_MEDIUM_PLAYER_BODY = '#ingame_gui:epic_players_panel/state/medium_player/body'
    EPIC_PLAYERS_PANEL_STATE_MEDIUM_PLAYER_NOTE = '#ingame_gui:epic_players_panel/state/medium_player/note'
    EPIC_PLAYERS_PANEL_STATE_MEDIUM_TANK_HEADER = '#ingame_gui:epic_players_panel/state/medium_tank/header'
    EPIC_PLAYERS_PANEL_STATE_MEDIUM_TANK_BODY = '#ingame_gui:epic_players_panel/state/medium_tank/body'
    EPIC_PLAYERS_PANEL_STATE_MEDIUM_TANK_NOTE = '#ingame_gui:epic_players_panel/state/medium_tank/note'
    EPIC_PLAYERS_PANEL_STATE_TOGGLE_HEADER = '#ingame_gui:epic_players_panel/state/toggle/header'
    EPIC_PLAYERS_PANEL_STATE_TOGGLE_BODY = '#ingame_gui:epic_players_panel/state/toggle/body'
    EPIC_PLAYERS_PANEL_STATE_TOGGLE_NOTE = '#ingame_gui:epic_players_panel/state/toggle/note'
    VEHICLE_MESSAGES_DEVICE_CRITICAL_AT_WORLD_COLLISION_SELF_SUICIDE = '#ingame_gui:vehicle_messages/DEVICE_CRITICAL_AT_WORLD_COLLISION_SELF_SUICIDE'
    VEHICLE_MESSAGES_DEVICE_CRITICAL_AT_WORLD_COLLISION_ENEMY_SELF = '#ingame_gui:vehicle_messages/DEVICE_CRITICAL_AT_WORLD_COLLISION_ENEMY_SELF'
    VEHICLE_MESSAGES_DEVICE_CRITICAL_AT_WORLD_COLLISION_ALLY_SELF = '#ingame_gui:vehicle_messages/DEVICE_CRITICAL_AT_WORLD_COLLISION_ALLY_SELF'
    VEHICLE_MESSAGES_DEVICE_CRITICAL_AT_WORLD_COLLISION_ALLY_SUICIDE = '#ingame_gui:vehicle_messages/DEVICE_CRITICAL_AT_WORLD_COLLISION_ALLY_SUICIDE'
    VEHICLE_MESSAGES_DEVICE_CRITICAL_AT_WORLD_COLLISION_ENEMY_ALLY = '#ingame_gui:vehicle_messages/DEVICE_CRITICAL_AT_WORLD_COLLISION_ENEMY_ALLY'
    VEHICLE_MESSAGES_DEVICE_CRITICAL_AT_WORLD_COLLISION_ALLY_ALLY = '#ingame_gui:vehicle_messages/DEVICE_CRITICAL_AT_WORLD_COLLISION_ALLY_ALLY'
    VEHICLE_MESSAGES_DEVICE_DESTROYED_AT_WORLD_COLLISION_SELF_SUICIDE = '#ingame_gui:vehicle_messages/DEVICE_DESTROYED_AT_WORLD_COLLISION_SELF_SUICIDE'
    VEHICLE_MESSAGES_DEVICE_DESTROYED_AT_WORLD_COLLISION_ENEMY_SELF = '#ingame_gui:vehicle_messages/DEVICE_DESTROYED_AT_WORLD_COLLISION_ENEMY_SELF'
    VEHICLE_MESSAGES_DEVICE_DESTROYED_AT_WORLD_COLLISION_ALLY_SELF = '#ingame_gui:vehicle_messages/DEVICE_DESTROYED_AT_WORLD_COLLISION_ALLY_SELF'
    VEHICLE_MESSAGES_DEVICE_DESTROYED_AT_WORLD_COLLISION_ALLY_SUICIDE = '#ingame_gui:vehicle_messages/DEVICE_DESTROYED_AT_WORLD_COLLISION_ALLY_SUICIDE'
    VEHICLE_MESSAGES_DEVICE_DESTROYED_AT_WORLD_COLLISION_ENEMY_ALLY = '#ingame_gui:vehicle_messages/DEVICE_DESTROYED_AT_WORLD_COLLISION_ENEMY_ALLY'
    VEHICLE_MESSAGES_DEVICE_DESTROYED_AT_WORLD_COLLISION_ALLY_ALLY = '#ingame_gui:vehicle_messages/DEVICE_DESTROYED_AT_WORLD_COLLISION_ALLY_ALLY'
    VEHICLE_MESSAGES_DEVICE_CRITICAL_AT_RAMMING_SELF_SUICIDE = '#ingame_gui:vehicle_messages/DEVICE_CRITICAL_AT_RAMMING_SELF_SUICIDE'
    VEHICLE_MESSAGES_DEVICE_CRITICAL_AT_RAMMING_ENEMY_SELF = '#ingame_gui:vehicle_messages/DEVICE_CRITICAL_AT_RAMMING_ENEMY_SELF'
    VEHICLE_MESSAGES_DEVICE_CRITICAL_AT_RAMMING_ALLY_SELF = '#ingame_gui:vehicle_messages/DEVICE_CRITICAL_AT_RAMMING_ALLY_SELF'
    VEHICLE_MESSAGES_DEVICE_CRITICAL_AT_RAMMING_ALLY_SUICIDE = '#ingame_gui:vehicle_messages/DEVICE_CRITICAL_AT_RAMMING_ALLY_SUICIDE'
    VEHICLE_MESSAGES_DEVICE_CRITICAL_AT_RAMMING_ENEMY_ALLY = '#ingame_gui:vehicle_messages/DEVICE_CRITICAL_AT_RAMMING_ENEMY_ALLY'
    VEHICLE_MESSAGES_DEVICE_CRITICAL_AT_RAMMING_ALLY_ALLY = '#ingame_gui:vehicle_messages/DEVICE_CRITICAL_AT_RAMMING_ALLY_ALLY'
    VEHICLE_MESSAGES_DEVICE_DESTROYED_AT_RAMMING_SELF_SUICIDE = '#ingame_gui:vehicle_messages/DEVICE_DESTROYED_AT_RAMMING_SELF_SUICIDE'
    VEHICLE_MESSAGES_DEVICE_DESTROYED_AT_RAMMING_ENEMY_SELF = '#ingame_gui:vehicle_messages/DEVICE_DESTROYED_AT_RAMMING_ENEMY_SELF'
    VEHICLE_MESSAGES_DEVICE_DESTROYED_AT_RAMMING_ALLY_SELF = '#ingame_gui:vehicle_messages/DEVICE_DESTROYED_AT_RAMMING_ALLY_SELF'
    VEHICLE_MESSAGES_DEVICE_DESTROYED_AT_RAMMING_ALLY_SUICIDE = '#ingame_gui:vehicle_messages/DEVICE_DESTROYED_AT_RAMMING_ALLY_SUICIDE'
    VEHICLE_MESSAGES_DEVICE_DESTROYED_AT_RAMMING_ENEMY_ALLY = '#ingame_gui:vehicle_messages/DEVICE_DESTROYED_AT_RAMMING_ENEMY_ALLY'
    VEHICLE_MESSAGES_DEVICE_DESTROYED_AT_RAMMING_ALLY_ALLY = '#ingame_gui:vehicle_messages/DEVICE_DESTROYED_AT_RAMMING_ALLY_ALLY'
    VEHICLE_MESSAGES_DEVICE_STARTED_FIRE_AT_RAMMING_SELF_SUICIDE = '#ingame_gui:vehicle_messages/DEVICE_STARTED_FIRE_AT_RAMMING_SELF_SUICIDE'
    VEHICLE_MESSAGES_DEVICE_STARTED_FIRE_AT_RAMMING_ENEMY_SELF = '#ingame_gui:vehicle_messages/DEVICE_STARTED_FIRE_AT_RAMMING_ENEMY_SELF'
    VEHICLE_MESSAGES_DEVICE_STARTED_FIRE_AT_RAMMING_ALLY_SELF = '#ingame_gui:vehicle_messages/DEVICE_STARTED_FIRE_AT_RAMMING_ALLY_SELF'
    VEHICLE_MESSAGES_DEVICE_STARTED_FIRE_AT_RAMMING_ALLY_SUICIDE = '#ingame_gui:vehicle_messages/DEVICE_STARTED_FIRE_AT_RAMMING_ALLY_SUICIDE'
    VEHICLE_MESSAGES_DEVICE_STARTED_FIRE_AT_RAMMING_ENEMY_ALLY = '#ingame_gui:vehicle_messages/DEVICE_STARTED_FIRE_AT_RAMMING_ENEMY_ALLY'
    VEHICLE_MESSAGES_DEVICE_STARTED_FIRE_AT_RAMMING_ALLY_ALLY = '#ingame_gui:vehicle_messages/DEVICE_STARTED_FIRE_AT_RAMMING_ALLY_ALLY'
    VEHICLE_MESSAGES_TANKMAN_HIT_AT_WORLD_COLLISION_SELF_SUICIDE = '#ingame_gui:vehicle_messages/TANKMAN_HIT_AT_WORLD_COLLISION_SELF_SUICIDE'
    VEHICLE_MESSAGES_TANKMAN_HIT_AT_WORLD_COLLISION_ENEMY_SELF = '#ingame_gui:vehicle_messages/TANKMAN_HIT_AT_WORLD_COLLISION_ENEMY_SELF'
    VEHICLE_MESSAGES_TANKMAN_HIT_AT_WORLD_COLLISION_ALLY_SELF = '#ingame_gui:vehicle_messages/TANKMAN_HIT_AT_WORLD_COLLISION_ALLY_SELF'
    VEHICLE_MESSAGES_TANKMAN_HIT_AT_WORLD_COLLISION_ALLY_SUICIDE = '#ingame_gui:vehicle_messages/TANKMAN_HIT_AT_WORLD_COLLISION_ALLY_SUICIDE'
    VEHICLE_MESSAGES_TANKMAN_HIT_AT_WORLD_COLLISION_ENEMY_ALLY = '#ingame_gui:vehicle_messages/TANKMAN_HIT_AT_WORLD_COLLISION_ENEMY_ALLY'
    VEHICLE_MESSAGES_TANKMAN_HIT_AT_WORLD_COLLISION_ALLY_ALLY = '#ingame_gui:vehicle_messages/TANKMAN_HIT_AT_WORLD_COLLISION_ALLY_ALLY'
    VEHICLE_MESSAGES_DEATH_FROM_SHOT = '#ingame_gui:vehicle_messages/DEATH_FROM_SHOT'
    POSTMORTEM_MESSAGES_DEATH_FROM_SHOT = '#ingame_gui:postmortem_messages/DEATH_FROM_SHOT'
    POSTMORTEM_MESSAGES_DEATH_UNKNOWN = '#ingame_gui:postmortem_messages/DEATH_UNKNOWN'
    VEHICLE_MESSAGES_DEATH_FROM_SHOT_ARTILLERY = '#ingame_gui:vehicle_messages/DEATH_FROM_SHOT_ARTILLERY'
    VEHICLE_MESSAGES_DEATH_FROM_SHOT_BOMBER = '#ingame_gui:vehicle_messages/DEATH_FROM_SHOT_BOMBER'
    POSTMORTEM_MESSAGES_DEATH_FROM_SHOT_ARTILLERY = '#ingame_gui:postmortem_messages/DEATH_FROM_SHOT_ARTILLERY'
    POSTMORTEM_MESSAGES_DEATH_FROM_SHOT_BOMBER = '#ingame_gui:postmortem_messages/DEATH_FROM_SHOT_BOMBER'
    POSTMORTEM_MESSAGES_DEATH_FROM_OVERTURN_SELF_SUICIDE = '#ingame_gui:postmortem_messages/DEATH_FROM_OVERTURN_SELF_SUICIDE'
    POSTMORTEM_MESSAGES_DEATH_FROM_OVERTURN_ENEMY_SELF = '#ingame_gui:postmortem_messages/DEATH_FROM_OVERTURN_ENEMY_SELF'
    POSTMORTEM_MESSAGES_DEATH_FROM_OVERTURN_ALLY_SELF = '#ingame_gui:postmortem_messages/DEATH_FROM_OVERTURN_ALLY_SELF'
    POSTMORTEM_MESSAGES_DEATH_FROM_MINE_EXPLOSION = '#ingame_gui:postmortem_messages/DEATH_FROM_MINE_EXPLOSION'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_SELF_ALLY = '#ingame_gui:player_messages/DEATH_FROM_SHOT_SELF_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_SELF_ALLY_ARTILLERY = '#ingame_gui:player_messages/DEATH_FROM_SHOT_SELF_ALLY_ARTILLERY'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_SELF_ALLY_BOMBER = '#ingame_gui:player_messages/DEATH_FROM_SHOT_SELF_ALLY_BOMBER'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_SELF_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_SHOT_SELF_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_SELF_ENEMY_ARTILLERY = '#ingame_gui:player_messages/DEATH_FROM_SHOT_SELF_ENEMY_ARTILLERY'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_SELF_ENEMY_BOMBER = '#ingame_gui:player_messages/DEATH_FROM_SHOT_SELF_ENEMY_BOMBER'
    PLAYER_MESSAGES_DEATH_FROM_MINE_EXPLOSION_SELF_ENEMY_ARCADE = '#ingame_gui:player_messages/DEATH_FROM_MINE_EXPLOSION_SELF_ENEMY_ARCADE'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ALLY_ALLY = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ALLY_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ALLY_ALLY_ARTILLERY = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ALLY_ALLY_ARTILLERY'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ALLY_ALLY_BOMBER = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ALLY_ALLY_BOMBER'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ALLY_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ALLY_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ALLY_ENEMY_ARTILLERY = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ALLY_ENEMY_ARTILLERY'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ALLY_ENEMY_BOMBER = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ALLY_ENEMY_BOMBER'
    PLAYER_MESSAGES_DEATH_FROM_MINE_EXPLOSION_ALLY_ENEMY_ARCADE = '#ingame_gui:player_messages/DEATH_FROM_MINE_EXPLOSION_ALLY_ENEMY_ARCADE'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ALLY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ALLY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ALLY_SUICIDE_ARTILLERY = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ALLY_SUICIDE_ARTILLERY'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ALLY_SUICIDE_BOMBER = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ALLY_SUICIDE_BOMBER'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ENEMY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ENEMY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ENEMY_SUICIDE_ARTILLERY = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ENEMY_SUICIDE_ARTILLERY'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ENEMY_SUICIDE_BOMBER = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ENEMY_SUICIDE_BOMBER'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ENEMY_ALLY = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ENEMY_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ENEMY_ALLY_ARTILLERY = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ENEMY_ALLY_ARTILLERY'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ENEMY_ALLY_BOMBER = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ENEMY_ALLY_BOMBER'
    PLAYER_MESSAGES_DEATH_FROM_MINE_EXPLOSION_ENEMY_ALLY_ARCADE = '#ingame_gui:player_messages/DEATH_FROM_MINE_EXPLOSION_ENEMY_ALLY_ARCADE'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ENEMY_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ENEMY_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ENEMY_ENEMY_ARTILLERY = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ENEMY_ENEMY_ARTILLERY'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ENEMY_ENEMY_BOMBER = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ENEMY_ENEMY_BOMBER'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_SELF_ENEMY_POI = '#ingame_gui:player_messages/DEATH_FROM_SHOT_SELF_ENEMY_POI'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_SELF_ENEMY_COMP7 = '#ingame_gui:player_messages/DEATH_FROM_SHOT_SELF_ENEMY_COMP7'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ALLY_ENEMY_POI = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ALLY_ENEMY_POI'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ALLY_ENEMY_COMP7 = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ALLY_ENEMY_COMP7'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ENEMY_ALLY_POI = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ENEMY_ALLY_POI'
    PLAYER_MESSAGES_DEATH_FROM_SHOT_ENEMY_ALLY_COMP7 = '#ingame_gui:player_messages/DEATH_FROM_SHOT_ENEMY_ALLY_COMP7'
    PLAYER_MESSAGES_DEATH_FROM_ARTILLERY_ENEMY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_ARTILLERY_ENEMY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_ARTILLERY_ALLY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_ARTILLERY_ALLY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_BOMBER_ENEMY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_BOMBER_ENEMY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_BOMBER_ALLY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_BOMBER_ALLY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_ARTILLERY_ALLY_ALLY = '#ingame_gui:player_messages/DEATH_FROM_ARTILLERY_ALLY_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_ARTILLERY_ALLY_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_ARTILLERY_ALLY_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_ARTILLERY_ENEMY_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_ARTILLERY_ENEMY_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_ARTILLERY_ENEMY_ALLY = '#ingame_gui:player_messages/DEATH_FROM_ARTILLERY_ENEMY_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_RECOVERY_ENEMY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_RECOVERY_ENEMY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_RECOVERY_ALLY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_RECOVERY_ALLY_SUICIDE'
    POSTMORTEM_MESSAGES_DEATH_FROM_RECOVERY = '#ingame_gui:postmortem_messages/DEATH_FROM_RECOVERY'
    PLAYER_MESSAGES_DEATH_FROM_ARTILLERY_PROTECTION_UNKNOWN = '#ingame_gui:player_messages/DEATH_FROM_ARTILLERY_PROTECTION_UNKNOWN'
    POSTMORTEM_MESSAGES_DEATH_FROM_ARTILLERY_PROTECTION_UNKNOWN = '#ingame_gui:postmortem_messages/DEATH_FROM_ARTILLERY_PROTECTION_UNKNOWN'
    PLAYER_MESSAGES_DEATH_FROM_ARTILLERY_PROTECTION_UNKNOWN_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_ARTILLERY_PROTECTION_UNKNOWN_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_ARTILLERY_PROTECTION_UNKNOWN_ALLY = '#ingame_gui:player_messages/DEATH_FROM_ARTILLERY_PROTECTION_UNKNOWN_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_SECTOR_PROTECTION_UNKNOWN = '#ingame_gui:player_messages/DEATH_FROM_SECTOR_PROTECTION_UNKNOWN'
    POSTMORTEM_MESSAGES_DEATH_FROM_SECTOR_PROTECTION_UNKNOWN = '#ingame_gui:postmortem_messages/DEATH_FROM_SECTOR_PROTECTION_UNKNOWN'
    PLAYER_MESSAGES_DEATH_FROM_SECTOR_PROTECTION_UNKNOWN_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_SECTOR_PROTECTION_UNKNOWN_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_SECTOR_PROTECTION_UNKNOWN_ALLY = '#ingame_gui:player_messages/DEATH_FROM_SECTOR_PROTECTION_UNKNOWN_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_SECTOR_BOMBERS_UNKNOWN = '#ingame_gui:player_messages/DEATH_FROM_SECTOR_BOMBERS_UNKNOWN'
    POSTMORTEM_MESSAGES_DEATH_FROM_SECTOR_BOMBERS_UNKNOWN = '#ingame_gui:postmortem_messages/DEATH_FROM_SECTOR_BOMBERS_UNKNOWN'
    PLAYER_MESSAGES_DEATH_FROM_SECTOR_BOMBERS_UNKNOWN_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_SECTOR_BOMBERS_UNKNOWN_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_SECTOR_BOMBERS_UNKNOWN_ALLY = '#ingame_gui:player_messages/DEATH_FROM_SECTOR_BOMBERS_UNKNOWN_ALLY'
    POSTMORTEM_MESSAGES_DEATH_FROM_ARTILLERY_SECTOR = '#ingame_gui:postmortem_messages/DEATH_FROM_ARTILLERY_SECTOR'
    POSTMORTEM_MESSAGES_DEATH_FROM_ARTILLERY_PROTECTION = '#ingame_gui:postmortem_messages/DEATH_FROM_ARTILLERY_PROTECTION'
    POSTMORTEM_MESSAGES_DEATH_FROM_BOMBER = '#ingame_gui:postmortem_messages/DEATH_FROM_BOMBER'
    VEHICLE_MESSAGES_DEATH_FROM_FIRE = '#ingame_gui:vehicle_messages/DEATH_FROM_FIRE'
    POSTMORTEM_MESSAGES_DEATH_FROM_FIRE = '#ingame_gui:postmortem_messages/DEATH_FROM_FIRE'
    PLAYER_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_SHOT = '#ingame_gui:player_messages/DEATH_FROM_INACTIVE_CREW_AT_SHOT'
    POSTMORTEM_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_SHOT = '#ingame_gui:postmortem_messages/DEATH_FROM_INACTIVE_CREW_AT_SHOT'
    PLAYER_MESSAGES_DEATH_FROM_INACTIVE_CREW = '#ingame_gui:player_messages/DEATH_FROM_INACTIVE_CREW'
    PLAYER_MESSAGES_DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT = '#ingame_gui:player_messages/DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT'
    POSTMORTEM_MESSAGES_DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT = '#ingame_gui:postmortem_messages/DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT'
    PLAYER_MESSAGES_DEATH_FROM_DEVICE_EXPLOSION_AT_FIRE = '#ingame_gui:player_messages/DEATH_FROM_DEVICE_EXPLOSION_AT_FIRE'
    POSTMORTEM_MESSAGES_DEATH_FROM_DEVICE_EXPLOSION_AT_FIRE = '#ingame_gui:postmortem_messages/DEATH_FROM_DEVICE_EXPLOSION_AT_FIRE'
    VEHICLE_MESSAGES_DEATH_FROM_DROWNING_SELF_SUICIDE = '#ingame_gui:vehicle_messages/DEATH_FROM_DROWNING_SELF_SUICIDE'
    POSTMORTEM_MESSAGES_DEATH_FROM_DROWNING_SELF_SUICIDE = '#ingame_gui:postmortem_messages/DEATH_FROM_DROWNING_SELF_SUICIDE'
    VEHICLE_MESSAGES_DEATH_FROM_DROWNING_ENEMY_SELF = '#ingame_gui:vehicle_messages/DEATH_FROM_DROWNING_ENEMY_SELF'
    POSTMORTEM_MESSAGES_DEATH_FROM_DROWNING_ENEMY_SELF = '#ingame_gui:postmortem_messages/DEATH_FROM_DROWNING_ENEMY_SELF'
    VEHICLE_MESSAGES_DEATH_FROM_DROWNING_ALLY_SELF = '#ingame_gui:vehicle_messages/DEATH_FROM_DROWNING_ALLY_SELF'
    POSTMORTEM_MESSAGES_DEATH_FROM_DROWNING_ALLY_SELF = '#ingame_gui:postmortem_messages/DEATH_FROM_DROWNING_ALLY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_DROWNING_SELF_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_DROWNING_SELF_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_DROWNING_SELF_ALLY = '#ingame_gui:player_messages/DEATH_FROM_DROWNING_SELF_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_DROWNING_SELF_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_DROWNING_SELF_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_DROWNING_ALLY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_DROWNING_ALLY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_DROWNING_ALLY_SELF = '#ingame_gui:player_messages/DEATH_FROM_DROWNING_ALLY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_DROWNING_ALLY_ALLY = '#ingame_gui:player_messages/DEATH_FROM_DROWNING_ALLY_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_DROWNING_ALLY_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_DROWNING_ALLY_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_DROWNING_ENEMY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_DROWNING_ENEMY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_DROWNING_ENEMY_SELF = '#ingame_gui:player_messages/DEATH_FROM_DROWNING_ENEMY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_DROWNING_ENEMY_ALLY = '#ingame_gui:player_messages/DEATH_FROM_DROWNING_ENEMY_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_DROWNING_ENEMY_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_DROWNING_ENEMY_ENEMY'
    PLAYER_MESSAGES_COMBAT_EQUIPMENT_READY_ARTILLERY = '#ingame_gui:player_messages/COMBAT_EQUIPMENT_READY_ARTILLERY'
    PLAYER_MESSAGES_COMBAT_EQUIPMENT_READY_BOMBER = '#ingame_gui:player_messages/COMBAT_EQUIPMENT_READY_BOMBER'
    PLAYER_MESSAGES_COMBAT_EQUIPMENT_READY_RECON = '#ingame_gui:player_messages/COMBAT_EQUIPMENT_READY_RECON'
    PLAYER_MESSAGES_COMBAT_EQUIPMENT_READY_SMOKE = '#ingame_gui:player_messages/COMBAT_EQUIPMENT_READY_SMOKE'
    PLAYER_MESSAGES_COMBAT_EQUIPMENT_READY_INSPIRE = '#ingame_gui:player_messages/COMBAT_EQUIPMENT_READY_INSPIRE'
    PLAYER_MESSAGES_COMBAT_EQUIPMENT_READY_REGENERATION_KIT_EPIC = '#ingame_gui:player_messages/COMBAT_EQUIPMENT_READY_REGENERATION_KIT_EPIC'
    PLAYER_MESSAGES_COMBAT_EQUIPMENT_READY_MINEFIELD_EPIC = '#ingame_gui:player_messages/COMBAT_EQUIPMENT_READY_MINEFIELD_EPIC'
    PLAYER_MESSAGES_COMBAT_EQUIPMENT_READY_STEALTH_RADAR = '#ingame_gui:player_messages/COMBAT_EQUIPMENT_READY_STEALTH_RADAR'
    PLAYER_MESSAGES_COMBAT_EQUIPMENT_USED_ARTILLERY = '#ingame_gui:player_messages/COMBAT_EQUIPMENT_USED_ARTILLERY'
    PLAYER_MESSAGES_COMBAT_EQUIPMENT_USED_BOMBER = '#ingame_gui:player_messages/COMBAT_EQUIPMENT_USED_BOMBER'
    PLAYER_MESSAGES_COMBAT_EQUIPMENT_USED_RECON = '#ingame_gui:player_messages/COMBAT_EQUIPMENT_USED_RECON'
    PLAYER_MESSAGES_COMBAT_EQUIPMENT_USED_SMOKE = '#ingame_gui:player_messages/COMBAT_EQUIPMENT_USED_SMOKE'
    PLAYER_MESSAGES_COMBAT_EQUIPMENT_USED_INSPIRE = '#ingame_gui:player_messages/COMBAT_EQUIPMENT_USED_INSPIRE'
    PLAYER_MESSAGES_COMBAT_EQUIPMENT_USED_HEALPOINT = '#ingame_gui:player_messages/COMBAT_EQUIPMENT_USED_HEALPOINT'
    PLAYER_MESSAGES_COMBAT_EQUIPMENT_USED_REGENERATION_KIT_EPIC = '#ingame_gui:player_messages/COMBAT_EQUIPMENT_USED_REGENERATION_KIT_EPIC'
    PLAYER_MESSAGES_COMBAT_EQUIPMENT_USED_MINEFIELD_EPIC = '#ingame_gui:player_messages/COMBAT_EQUIPMENT_USED_MINEFIELD_EPIC'
    PLAYER_MESSAGES_COMBAT_EQUIPMENT_USED_STEALTH_RADAR = '#ingame_gui:player_messages/COMBAT_EQUIPMENT_USED_STEALTH_RADAR'
    PLAYER_MESSAGES_COMBAT_BR_EQUIPMENT_READY = '#ingame_gui:player_messages/COMBAT_BR_EQUIPMENT_READY'
    VEHICLE_MESSAGES_DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE = '#ingame_gui:vehicle_messages/DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE'
    POSTMORTEM_MESSAGES_DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE = '#ingame_gui:postmortem_messages/DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE'
    VEHICLE_MESSAGES_DEATH_FROM_WORLD_COLLISION_ENEMY_SELF = '#ingame_gui:vehicle_messages/DEATH_FROM_WORLD_COLLISION_ENEMY_SELF'
    POSTMORTEM_MESSAGES_DEATH_FROM_WORLD_COLLISION_ENEMY_SELF = '#ingame_gui:postmortem_messages/DEATH_FROM_WORLD_COLLISION_ENEMY_SELF'
    VEHICLE_MESSAGES_DEATH_FROM_WORLD_COLLISION_ALLY_SELF = '#ingame_gui:vehicle_messages/DEATH_FROM_WORLD_COLLISION_ALLY_SELF'
    POSTMORTEM_MESSAGES_DEATH_FROM_WORLD_COLLISION_ALLY_SELF = '#ingame_gui:postmortem_messages/DEATH_FROM_WORLD_COLLISION_ALLY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_WORLD_COLLISION_SELF_ALLY = '#ingame_gui:player_messages/DEATH_FROM_WORLD_COLLISION_SELF_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_WORLD_COLLISION_SELF_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_WORLD_COLLISION_SELF_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_WORLD_COLLISION_ALLY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_WORLD_COLLISION_ALLY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_WORLD_COLLISION_ALLY_SELF = '#ingame_gui:player_messages/DEATH_FROM_WORLD_COLLISION_ALLY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_WORLD_COLLISION_ALLY_ALLY = '#ingame_gui:player_messages/DEATH_FROM_WORLD_COLLISION_ALLY_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_WORLD_COLLISION_ALLY_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_WORLD_COLLISION_ALLY_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_WORLD_COLLISION_ENEMY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_WORLD_COLLISION_ENEMY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_WORLD_COLLISION_ENEMY_SELF = '#ingame_gui:player_messages/DEATH_FROM_WORLD_COLLISION_ENEMY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_WORLD_COLLISION_ENEMY_ALLY = '#ingame_gui:player_messages/DEATH_FROM_WORLD_COLLISION_ENEMY_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_WORLD_COLLISION_ENEMY_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_WORLD_COLLISION_ENEMY_ENEMY'
    VEHICLE_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_SUICIDE = '#ingame_gui:vehicle_messages/DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_SUICIDE'
    POSTMORTEM_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_SUICIDE = '#ingame_gui:postmortem_messages/DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_SUICIDE'
    VEHICLE_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF = '#ingame_gui:vehicle_messages/DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF'
    POSTMORTEM_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF = '#ingame_gui:postmortem_messages/DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF'
    VEHICLE_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SELF = '#ingame_gui:vehicle_messages/DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SELF'
    POSTMORTEM_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SELF = '#ingame_gui:postmortem_messages/DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_ALLY = '#ingame_gui:player_messages/DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SELF = '#ingame_gui:player_messages/DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_ALLY = '#ingame_gui:player_messages/DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF = '#ingame_gui:player_messages/DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_ALLY = '#ingame_gui:player_messages/DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_ENEMY'
    VEHICLE_MESSAGES_DEATH_FROM_DEATH_ZONE_SELF_SUICIDE = '#ingame_gui:vehicle_messages/DEATH_FROM_DEATH_ZONE_SELF_SUICIDE'
    POSTMORTEM_MESSAGES_DEATH_FROM_DEATH_ZONE_SELF_SUICIDE = '#ingame_gui:postmortem_messages/DEATH_FROM_DEATH_ZONE_SELF_SUICIDE'
    POSTMORTEM_MESSAGES_DEATH_FROM_STATIC_DEATH_ZONE_SELF_SUICIDE = '#ingame_gui:postmortem_messages/DEATH_FROM_STATIC_DEATH_ZONE_SELF_SUICIDE'
    VEHICLE_MESSAGES_DEATH_FROM_DEATH_ZONE_ENEMY_SELF = '#ingame_gui:vehicle_messages/DEATH_FROM_DEATH_ZONE_ENEMY_SELF'
    POSTMORTEM_MESSAGES_DEATH_FROM_DEATH_ZONE_ENEMY_SELF = '#ingame_gui:postmortem_messages/DEATH_FROM_DEATH_ZONE_ENEMY_SELF'
    VEHICLE_MESSAGES_DEATH_FROM_DEATH_ZONE_ALLY_SELF = '#ingame_gui:vehicle_messages/DEATH_FROM_DEATH_ZONE_ALLY_SELF'
    POSTMORTEM_MESSAGES_DEATH_FROM_DEATH_ZONE_ALLY_SELF = '#ingame_gui:postmortem_messages/DEATH_FROM_DEATH_ZONE_ALLY_SELF'
    VEHICLE_MESSAGES_DEATH_FROM_GAS_ATTACK_ENEMY_SELF = '#ingame_gui:vehicle_messages/DEATH_FROM_GAS_ATTACK_ENEMY_SELF'
    VEHICLE_MESSAGES_DEATH_FROM_GAS_ATTACK_ALLY_SELF = '#ingame_gui:vehicle_messages/DEATH_FROM_GAS_ATTACK_ALLY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_DEATH_ZONE_SELF_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_DEATH_ZONE_SELF_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_DEATH_ZONE_SELF_ALLY = '#ingame_gui:player_messages/DEATH_FROM_DEATH_ZONE_SELF_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_DEATH_ZONE_SELF_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_DEATH_ZONE_SELF_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_DEATH_ZONE_ALLY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_DEATH_ZONE_ALLY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_STATIC_DEATH_ZONE_ALLY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_STATIC_DEATH_ZONE_ALLY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_DEATH_ZONE_ALLY_SELF = '#ingame_gui:player_messages/DEATH_FROM_DEATH_ZONE_ALLY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_DEATH_ZONE_ALLY_ALLY = '#ingame_gui:player_messages/DEATH_FROM_DEATH_ZONE_ALLY_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_DEATH_ZONE_ALLY_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_DEATH_ZONE_ALLY_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_DEATH_ZONE_ENEMY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_DEATH_ZONE_ENEMY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_DEATH_ZONE_ENEMY_SELF = '#ingame_gui:player_messages/DEATH_FROM_DEATH_ZONE_ENEMY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_DEATH_ZONE_ENEMY_ALLY = '#ingame_gui:player_messages/DEATH_FROM_DEATH_ZONE_ENEMY_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_DEATH_ZONE_ENEMY_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_DEATH_ZONE_ENEMY_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_GAS_ATTACK_SELF_ALLY = '#ingame_gui:player_messages/DEATH_FROM_GAS_ATTACK_SELF_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_GAS_ATTACK_SELF_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_GAS_ATTACK_SELF_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_GAS_ATTACK_ALLY_SELF = '#ingame_gui:player_messages/DEATH_FROM_GAS_ATTACK_ALLY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_GAS_ATTACK_ALLY_ALLY = '#ingame_gui:player_messages/DEATH_FROM_GAS_ATTACK_ALLY_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_GAS_ATTACK_ALLY_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_GAS_ATTACK_ALLY_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_GAS_ATTACK_ENEMY_SELF = '#ingame_gui:player_messages/DEATH_FROM_GAS_ATTACK_ENEMY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_GAS_ATTACK_ENEMY_ALLY = '#ingame_gui:player_messages/DEATH_FROM_GAS_ATTACK_ENEMY_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_GAS_ATTACK_ENEMY_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_GAS_ATTACK_ENEMY_ENEMY'
    VEHICLE_MESSAGES_DEATH_FROM_RAMMING_SELF_SUICIDE = '#ingame_gui:vehicle_messages/DEATH_FROM_RAMMING_SELF_SUICIDE'
    POSTMORTEM_MESSAGES_DEATH_FROM_RAMMING_SELF_SUICIDE = '#ingame_gui:postmortem_messages/DEATH_FROM_RAMMING_SELF_SUICIDE'
    VEHICLE_MESSAGES_DEATH_FROM_RAMMING_ENEMY_SELF = '#ingame_gui:vehicle_messages/DEATH_FROM_RAMMING_ENEMY_SELF'
    POSTMORTEM_MESSAGES_DEATH_FROM_RAMMING_ENEMY_SELF = '#ingame_gui:postmortem_messages/DEATH_FROM_RAMMING_ENEMY_SELF'
    VEHICLE_MESSAGES_DEATH_FROM_RAMMING_ALLY_SELF = '#ingame_gui:vehicle_messages/DEATH_FROM_RAMMING_ALLY_SELF'
    POSTMORTEM_MESSAGES_DEATH_FROM_RAMMING_ALLY_SELF = '#ingame_gui:postmortem_messages/DEATH_FROM_RAMMING_ALLY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_RAMMING_SELF_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_RAMMING_SELF_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_RAMMING_SELF_ALLY = '#ingame_gui:player_messages/DEATH_FROM_RAMMING_SELF_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_RAMMING_SELF_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_RAMMING_SELF_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_RAMMING_ALLY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_RAMMING_ALLY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_RAMMING_ALLY_SELF = '#ingame_gui:player_messages/DEATH_FROM_RAMMING_ALLY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_RAMMING_ALLY_ALLY = '#ingame_gui:player_messages/DEATH_FROM_RAMMING_ALLY_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_RAMMING_ALLY_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_RAMMING_ALLY_ENEMY'
    POSTMORTEM_MESSAGES_DEATH_FROM_KAMIKAZE = '#ingame_gui:postmortem_messages/DEATH_FROM_KAMIKAZE'
    POSTMORTEM_MESSAGES_DEATH_FROM_FIRE_CIRCLE = '#ingame_gui:postmortem_messages/DEATH_FROM_FIRE_CIRCLE'
    POSTMORTEM_MESSAGES_DEATH_FROM_THUNDER_STRIKE = '#ingame_gui:postmortem_messages/DEATH_FROM_THUNDER_STRIKE'
    POSTMORTEM_MESSAGES_DEATH_FROM_CORRODING_SHOT = '#ingame_gui:postmortem_messages/DEATH_FROM_CORRODING_SHOT'
    POSTMORTEM_MESSAGES_DEATH_FROM_CLING_BRANDER = '#ingame_gui:postmortem_messages/DEATH_FROM_CLING_BRANDER'
    POSTMORTEM_MESSAGES_DEATH_FROM_SHOT_ARCADE_BOMBER_BATTLE_ROYALE = '#ingame_gui:postmortem_messages/DEATH_FROM_SHOT_ARCADE_BOMBER_BATTLE_ROYALE'
    PLAYER_MESSAGES_DEATH_FROM_OVERTURN_SELF_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_OVERTURN_SELF_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_OVERTURN_SELF_ALLY = '#ingame_gui:player_messages/DEATH_FROM_OVERTURN_SELF_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_OVERTURN_SELF_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_OVERTURN_SELF_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_OVERTURN_ALLY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_OVERTURN_ALLY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_OVERTURN_ALLY_SELF = '#ingame_gui:player_messages/DEATH_FROM_OVERTURN_ALLY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_OVERTURN_ALLY_ALLY = '#ingame_gui:player_messages/DEATH_FROM_OVERTURN_ALLY_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_OVERTURN_ALLY_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_OVERTURN_ALLY_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_OVERTURN_ENEMY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_OVERTURN_ENEMY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_OVERTURN_ENEMY_SELF = '#ingame_gui:player_messages/DEATH_FROM_OVERTURN_ENEMY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_OVERTURN_ENEMY_ALLY = '#ingame_gui:player_messages/DEATH_FROM_OVERTURN_ENEMY_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_OVERTURN_ENEMY_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_OVERTURN_ENEMY_ENEMY'
    PLAYER_MESSAGES_DEATH_FROM_RAMMING_ENEMY_SUICIDE = '#ingame_gui:player_messages/DEATH_FROM_RAMMING_ENEMY_SUICIDE'
    PLAYER_MESSAGES_DEATH_FROM_RAMMING_ENEMY_SELF = '#ingame_gui:player_messages/DEATH_FROM_RAMMING_ENEMY_SELF'
    PLAYER_MESSAGES_DEATH_FROM_RAMMING_ENEMY_ALLY = '#ingame_gui:player_messages/DEATH_FROM_RAMMING_ENEMY_ALLY'
    PLAYER_MESSAGES_DEATH_FROM_RAMMING_ENEMY_ENEMY = '#ingame_gui:player_messages/DEATH_FROM_RAMMING_ENEMY_ENEMY'
    PERSONALMISSIONS_TIP_MAINHEADER = '#ingame_gui:personalMissions/tip/mainHeader'
    PERSONALMISSIONS_TIP_ADDITIONALHEADER = '#ingame_gui:personalMissions/tip/additionalHeader'
    PERSONALMISSIONS_TIP_NOQUESTS_VEHICLETYPE = '#ingame_gui:personalMissions/tip/noQuests/vehicleType'
    PERSONALMISSIONS_TIP_NOQUESTS_BATTLETYPE = '#ingame_gui:personalMissions/tip/noQuests/battleType'
    FORTCONSUMABLES_TIMER_POSTFIX = '#ingame_gui:fortConsumables/timer/postfix'
    FLAGS_TIMER = '#ingame_gui:flags/timer'
    COUNTRIBBONS_MULTISEPARATOR = '#ingame_gui:countRibbons/multiSeparator'
    EFFICIENCYRIBBONS_ARMOR = '#ingame_gui:efficiencyRibbons/armor'
    EFFICIENCYRIBBONS_CAPTURE = '#ingame_gui:efficiencyRibbons/capture'
    EFFICIENCYRIBBONS_DAMAGE = '#ingame_gui:efficiencyRibbons/damage'
    EFFICIENCYRIBBONS_RAM = '#ingame_gui:efficiencyRibbons/ram'
    EFFICIENCYRIBBONS_BURN = '#ingame_gui:efficiencyRibbons/burn'
    EFFICIENCYRIBBONS_DEFENCE = '#ingame_gui:efficiencyRibbons/defence'
    EFFICIENCYRIBBONS_KILL = '#ingame_gui:efficiencyRibbons/kill'
    EFFICIENCYRIBBONS_SPOTTED = '#ingame_gui:efficiencyRibbons/spotted'
    EFFICIENCYRIBBONS_ASSISTTRACK = '#ingame_gui:efficiencyRibbons/assistTrack'
    EFFICIENCYRIBBONS_ASSISTSPOT = '#ingame_gui:efficiencyRibbons/assistSpot'
    EFFICIENCYRIBBONS_CRITS = '#ingame_gui:efficiencyRibbons/crits'
    EFFICIENCYRIBBONS_WORLDCOLLISION = '#ingame_gui:efficiencyRibbons/worldCollision'
    EFFICIENCYRIBBONS_RECEIVEDCRITS = '#ingame_gui:efficiencyRibbons/receivedCrits'
    EFFICIENCYRIBBONS_RECEIVEDDAMAGE = '#ingame_gui:efficiencyRibbons/receivedDamage'
    EFFICIENCYRIBBONS_RECEIVEDBURN = '#ingame_gui:efficiencyRibbons/receivedBurn'
    EFFICIENCYRIBBONS_BERSERKER = '#ingame_gui:efficiencyRibbons/berserker'
    EFFICIENCYRIBBONS_SPAWNEDBOTDMG = '#ingame_gui:efficiencyRibbons/spawnedBotDmg'
    EFFICIENCYRIBBONS_RECEIVEDDMGBYSPAWNEDBOT = '#ingame_gui:efficiencyRibbons/receivedDmgBySpawnedBot'
    EFFICIENCYRIBBONS_DAMAGEBYMINEFIELD = '#ingame_gui:efficiencyRibbons/damageByMinefield'
    EFFICIENCYRIBBONS_RECEIVEDBYMINEFIELD = '#ingame_gui:efficiencyRibbons/receivedByMinefield'
    EFFICIENCYRIBBONS_RECEIVEDBYSMOKE = '#ingame_gui:efficiencyRibbons/receivedBySmoke'
    EFFICIENCYRIBBONS_DEALTDAMAGEBYCORRODINGSHOT = '#ingame_gui:efficiencyRibbons/dealtDamageByCorrodingShot'
    EFFICIENCYRIBBONS_RECEIVEDBYCORRODINGSHOT = '#ingame_gui:efficiencyRibbons/receivedByCorrodingShot'
    EFFICIENCYRIBBONS_DEALTDAMAGEBYFIRECIRCLE = '#ingame_gui:efficiencyRibbons/dealtDamageByFireCircle'
    EFFICIENCYRIBBONS_RECEIVEDBYFIRECIRCLE = '#ingame_gui:efficiencyRibbons/receivedByFireCircle'
    EFFICIENCYRIBBONS_DEALTDAMAGEBYCLINGBRANDER = '#ingame_gui:efficiencyRibbons/dealtDamageByClingBrander'
    EFFICIENCYRIBBONS_RECEIVEDBYCLINGBRANDER = '#ingame_gui:efficiencyRibbons/receivedByClingBrander'
    EFFICIENCYRIBBONS_DEALTDAMAGEBYTHUNDERSTRIKE = '#ingame_gui:efficiencyRibbons/dealtDamageByThunderStrike'
    EFFICIENCYRIBBONS_RECEIVEDBYTHUNDERSTRIKE = '#ingame_gui:efficiencyRibbons/receivedByThunderStrike'
    EFFICIENCYRIBBONS_RECEIVEDRAM = '#ingame_gui:efficiencyRibbons/receivedRam'
    EFFICIENCYRIBBONS_RECEIVEDWORLDCOLLISION = '#ingame_gui:efficiencyRibbons/receivedWorldCollision'
    EFFICIENCYRIBBONS_VEHICLERECOVERY = '#ingame_gui:efficiencyRibbons/vehicleRecovery'
    EFFICIENCYRIBBONS_BONUSRIBBON = '#ingame_gui:efficiencyRibbons/bonusRibbon'
    EFFICIENCYRIBBONS_STUN = '#ingame_gui:efficiencyRibbons/stun'
    EFFICIENCYRIBBONS_ASSISTSTUN = '#ingame_gui:efficiencyRibbons/assistStun'
    EFFICIENCYRIBBONS_DEATHZONE = '#ingame_gui:efficiencyRibbons/deathZone'
    EFFICIENCYRIBBONS_STATICDEATHZONE = '#ingame_gui:efficiencyRibbons/staticDeathZone'
    EFFICIENCYRIBBONS_CANNONDMG = '#ingame_gui:efficiencyRibbons/CannonDmg'
    EFFICIENCYRIBBONS_AIRSTRIKEDMG = '#ingame_gui:efficiencyRibbons/AirstrikeDmg'
    EFFICIENCYRIBBONS_ARTILLERYDMG = '#ingame_gui:efficiencyRibbons/ArtilleryDmg'
    DAMAGELOG_SHELLTYPE_ARMOR_PIERCING = '#ingame_gui:damageLog/shellType/ARMOR_PIERCING'
    DAMAGELOG_SHELLTYPE_HIGH_EXPLOSIVE = '#ingame_gui:damageLog/shellType/HIGH_EXPLOSIVE'
    DAMAGELOG_SHELLTYPE_FLAME = '#ingame_gui:damageLog/shellType/FLAME'
    DAMAGELOG_SHELLTYPE_ARMOR_PIERCING_HE = '#ingame_gui:damageLog/shellType/ARMOR_PIERCING_HE'
    DAMAGELOG_SHELLTYPE_ARMOR_PIERCING_CR = '#ingame_gui:damageLog/shellType/ARMOR_PIERCING_CR'
    DAMAGELOG_SHELLTYPE_HOLLOW_CHARGE = '#ingame_gui:damageLog/shellType/HOLLOW_CHARGE'
    DAMAGELOG_MULTIPLIER = '#ingame_gui:damageLog/multiplier'
    HITMARKER_BLOCKED = '#ingame_gui:hitMarker/blocked'
    HITMARKER_RICOCHET = '#ingame_gui:hitMarker/ricochet'
    HITMARKER_CRITICAL = '#ingame_gui:hitMarker/critical'
    HITMARKER_SPACEDARMORBLOCKED = '#ingame_gui:hitMarker/spacedArmorBlocked'
    HITMARKER_MISSARMOR = '#ingame_gui:hitMarker/missArmor'
    HITMARKER_TRACKBLOCKED = '#ingame_gui:hitMarker/trackBlocked'
    HITMARKER_WHEELBLOCKED = '#ingame_gui:hitMarker/wheelBlocked'
    RESPAWNVIEW_TITLE = '#ingame_gui:respawnView/title'
    RESPAWNVIEW_ADDITIONALTIP = '#ingame_gui:respawnView/additionalTip'
    RESPAWNVIEW_ADDITIONALTIPLIMITED = '#ingame_gui:respawnView/additionalTipLimited'
    RESPAWNVIEW_COOLDOWNLBL = '#ingame_gui:respawnView/cooldownLbl'
    RESPAWNVIEW_DESTROYEDLBL = '#ingame_gui:respawnView/destroyedLbl'
    RESPAWNVIEW_DISABLEDLBL = '#ingame_gui:respawnView/disabledLbl'
    RESPAWNVIEW_NEXTVEHICLENAME = '#ingame_gui:respawnView/nextVehicleName'
    RESPAWNVIEW_EMPTYSLOTINFO = '#ingame_gui:respawnView/emptySlotInfo'
    RESPAWNVIEW_EMPTYSLOTINFOTOOLTIP = '#ingame_gui:respawnView/emptySlotInfoTooltip'
    RESPAWNVIEW_CLASSNOTAVAILABLE = '#ingame_gui:respawnView/classNotAvailable'
    FLAGNOTIFICATION_FLAGCAPTURED = '#ingame_gui:flagNotification/flagCaptured'
    FLAGNOTIFICATION_FLAGINBASE = '#ingame_gui:flagNotification/flagInbase'
    FLAGNOTIFICATION_FLAGDELIVERED = '#ingame_gui:flagNotification/flagDelivered'
    FLAGNOTIFICATION_FLAGABSORBED = '#ingame_gui:flagNotification/flagAbsorbed'
    SCOREPANEL_SQUADLBL = '#ingame_gui:scorePanel/squadLbl'
    SCOREPANEL_MYSQUADLBL = '#ingame_gui:scorePanel/mySquadLbl'
    SCOREPANEL_PLAYERSCORE = '#ingame_gui:scorePanel/playerScore'
    DYNAMICSQUAD_ALLY_ADD = '#ingame_gui:dynamicSquad/ally/add'
    DYNAMICSQUAD_ENEMY_ADD = '#ingame_gui:dynamicSquad/enemy/add'
    DYNAMICSQUAD_ALLY_DISABLED = '#ingame_gui:dynamicSquad/ally/disabled'
    DYNAMICSQUAD_ENEMY_DISABLED = '#ingame_gui:dynamicSquad/enemy/disabled'
    DYNAMICSQUAD_ALLY_WASSENT = '#ingame_gui:dynamicSquad/ally/wasSent'
    DYNAMICSQUAD_ENEMY_WASSENT = '#ingame_gui:dynamicSquad/enemy/wasSent'
    DYNAMICSQUAD_INVITE = '#ingame_gui:dynamicSquad/invite'
    DYNAMICSQUAD_ALLY_RECEIVED = '#ingame_gui:dynamicSquad/ally/received'
    DYNAMICSQUAD_ENEMY_RECEIVED = '#ingame_gui:dynamicSquad/enemy/received'
    DYNAMICSQUAD_ALLY_ANONYMIZED_CLAN = '#ingame_gui:dynamicSquad/ally/anonymized/clan'
    DYNAMICSQUAD_ALLY_ANONYMIZED_NOCLAN = '#ingame_gui:dynamicSquad/ally/anonymized/noClan'
    DYNAMICSQUAD_HINT_VOIPTOGGLEKEYLEFT = '#ingame_gui:dynamicSquad/hint/voipToggleKeyLeft'
    DYNAMICSQUAD_HINT_VOIPTOGGLEKEYRIGHT = '#ingame_gui:dynamicSquad/hint/voipToggleKeyRight'
    AIM_ZOOM = '#ingame_gui:aim/zoom'
    DISTANCE_METERS = '#ingame_gui:distance/meters'
    TABSTATSHINT = '#ingame_gui:tabStatsHint'
    REPAIRPOINT_TITLE = '#ingame_gui:repairPoint/title'
    REPAIRPOINT_UNAVAILABLE = '#ingame_gui:repairPoint/unavailable'
    BATTLEENDWARNING_TEXT = '#ingame_gui:battleEndWarning/text'
    DAMAGEINDICATOR_MULTIPLIER = '#ingame_gui:damageIndicator/multiplier'
    VEHICLE_MESSAGES_DEATH_FROM_OVERTURN_SELF_SUICIDE = '#ingame_gui:vehicle_messages/DEATH_FROM_OVERTURN_SELF_SUICIDE'
    VEHICLE_MESSAGES_DEATH_FROM_OVERTURN_ENEMY_SELF = '#ingame_gui:vehicle_messages/DEATH_FROM_OVERTURN_ENEMY_SELF'
    VEHICLE_MESSAGES_DEATH_FROM_OVERTURN_ALLY_SELF = '#ingame_gui:vehicle_messages/DEATH_FROM_OVERTURN_ALLY_SELF'
    BATTLEMESSENGER_TOXIC_BLACKLIST_ADD_IN_BLACKLIST_HEADER = '#ingame_gui:battleMessenger/toxic/blackList/ADD_IN_BLACKLIST/header'
    BATTLEMESSENGER_TOXIC_BLACKLIST_ADD_IN_BLACKLIST_BODY = '#ingame_gui:battleMessenger/toxic/blackList/ADD_IN_BLACKLIST/body'
    BATTLEMESSENGER_TOXIC_BLACKLIST_CANT_ADD_IN_BLACKLIST_HEADER = '#ingame_gui:battleMessenger/toxic/blackList/CANT_ADD_IN_BLACKLIST/header'
    BATTLEMESSENGER_TOXIC_BLACKLIST_CANT_ADD_IN_BLACKLIST_BODY = '#ingame_gui:battleMessenger/toxic/blackList/CANT_ADD_IN_BLACKLIST/body'
    BATTLEMESSENGER_TOXIC_BLACKLIST_REMOVE_FROM_BLACKLIST_HEADER = '#ingame_gui:battleMessenger/toxic/blackList/REMOVE_FROM_BLACKLIST/header'
    BATTLEMESSENGER_TOXIC_BLACKLIST_REMOVE_FROM_BLACKLIST_BODY = '#ingame_gui:battleMessenger/toxic/blackList/REMOVE_FROM_BLACKLIST/body'
    PLAYER_MESSAGES_DESTRUCTIBLE_DESTROYED_SELF = '#ingame_gui:player_messages/DESTRUCTIBLE_DESTROYED_SELF'
    PLAYER_MESSAGES_DESTRUCTIBLE_DESTROYED_ALLY = '#ingame_gui:player_messages/DESTRUCTIBLE_DESTROYED_ALLY'
    PLAYER_MESSAGES_DESTRUCTIBLE_DESTROYED_ENEMY = '#ingame_gui:player_messages/DESTRUCTIBLE_DESTROYED_ENEMY'
    SIEGEMODE_HINT_PRESS = '#ingame_gui:siegeMode/hint/press'
    SIEGEMODE_HINT_FORMODE_0 = '#ingame_gui:siegeMode/hint/forMode/0'
    SIEGEMODE_HINT_FORMODE_1 = '#ingame_gui:siegeMode/hint/forMode/1'
    SIEGEMODE_HINT_FORMODE_2 = '#ingame_gui:siegeMode/hint/forMode/2'
    SIEGEMODE_HINT_FORMODE_3 = '#ingame_gui:siegeMode/hint/forMode/3'
    SIEGEMODE_HINT_NOBINDING = '#ingame_gui:siegeMode/hint/noBinding'
    SIEGEMODE_HINT_WHEELED = '#ingame_gui:siegeMode/hint/wheeled'
    SIEGEMODE_HINT_TURBOSHAFTENGINE = '#ingame_gui:siegeMode/hint/turboshaftEngine'
    SIEGEMODE_HINT_ROCKETACCELERATION = '#ingame_gui:siegeMode/hint/rocketAcceleration'
    EFFICIENCYRIBBONS_ENEMYSECTORCAPTURED = '#ingame_gui:efficiencyRibbons/enemySectorCaptured'
    EFFICIENCYRIBBONS_DESTRUCTIBLEDAMAGED = '#ingame_gui:efficiencyRibbons/destructibleDamaged'
    EFFICIENCYRIBBONS_DESTRUCTIBLEDESTROYED = '#ingame_gui:efficiencyRibbons/destructibleDestroyed'
    EFFICIENCYRIBBONS_DESTRUCTIBLESDEFENDED = '#ingame_gui:efficiencyRibbons/destructiblesDefended'
    EFFICIENCYRIBBONS_DEFENDERBONUS = '#ingame_gui:efficiencyRibbons/defenderBonus'
    EFFICIENCYRIBBONS_ASSISTBYABILITY = '#ingame_gui:efficiencyRibbons/assistByAbility'
    RECOVERY_HINT1 = '#ingame_gui:recovery/hint1'
    RECOVERY_HINT2 = '#ingame_gui:recovery/hint2'
    RECOVERY_COOLDOWN = '#ingame_gui:recovery/cooldown'
    ATTACKREASON_ARTILLERYPROTECTION = '#ingame_gui:attackReason/artilleryProtection'
    ATTACKREASON_ARTILLERY_SECTOR = '#ingame_gui:attackReason/artillery_sector'
    ATTACKREASON_BOMBERS = '#ingame_gui:attackReason/bombers'
    TRAJECTORYVIEW_HINT_NOBINDINGKEY = '#ingame_gui:trajectoryView/hint/noBindingKey'
    TRAJECTORYVIEW_HINT_ALTERNATEMODELEFT = '#ingame_gui:trajectoryView/hint/alternateModeLeft'
    TRAJECTORYVIEW_HINT_ALTERNATEMODERIGHT = '#ingame_gui:trajectoryView/hint/alternateModeRight'
    STUN_INDICATOR = '#ingame_gui:stun/indicator'
    STUNFLAME_INDICATOR = '#ingame_gui:stunFlame/indicator'
    STUN_SECONDS = '#ingame_gui:stun/seconds'
    BATTLEPROGRESS_HINT_PRESS = '#ingame_gui:battleProgress/hint/press'
    BATTLEPROGRESS_HINT_DESCRIPTION = '#ingame_gui:battleProgress/hint/description'
    COLORSETTINGSTIPPANEL_BTNLABEL = '#ingame_gui:colorSettingsTipPanel/btnLabel'
    REWARDWINDOW_WINHEADERTEXT = '#ingame_gui:rewardWindow/winHeaderText'
    REWARDWINDOW_COUNTLABEL = '#ingame_gui:rewardWindow/countLabel'
    REWARDWINDOW_BASE_SUBHEADERTEXT = '#ingame_gui:rewardWindow/base/subHeaderText'
    REWARDWINDOW_BASE_HEADERTEXT = '#ingame_gui:rewardWindow/base/headerText'
    REWARDWINDOW_BASE_DESCTEXT = '#ingame_gui:rewardWindow/base/descText'
    REWARDWINDOW_BASE_BTNLABEL = '#ingame_gui:rewardWindow/base/btnLabel'
    REWARDWINDOW_WGCQ_CLAN_REWARD_WINHEADERTEXT = '#ingame_gui:rewardWindow/wgcq_clan_reward/winHeaderText'
    REWARDWINDOW_WGCQ_CLAN_REWARD_HEADERTEXT = '#ingame_gui:rewardWindow/wgcq_clan_reward/headerText'
    REWARDWINDOW_WGCQ_CLAN_REWARD_SUBHEADERTEXT = '#ingame_gui:rewardWindow/wgcq_clan_reward/subHeaderText'
    REWARDWINDOW_WGCQ_CLAN_REWARD_DESCTEXT = '#ingame_gui:rewardWindow/wgcq_clan_reward/descText'
    REWARDWINDOW_WGCQ_CLAN_REWARD_BTNLABEL = '#ingame_gui:rewardWindow/wgcq_clan_reward/btnLabel'
    REWARDWINDOW_WGCQ_CLAN_REWARD_SECONDBTNLABEL = '#ingame_gui:rewardWindow/wgcq_clan_reward/secondBtnLabel'
    REWARDWINDOW_WGCQ_PLAYER_REWARD_WINHEADERTEXT = '#ingame_gui:rewardWindow/wgcq_player_reward/winHeaderText'
    REWARDWINDOW_WGCQ_PLAYER_REWARD_HEADERTEXT = '#ingame_gui:rewardWindow/wgcq_player_reward/headerText'
    REWARDWINDOW_WGCQ_PLAYER_REWARD_SUBHEADERTEXT = '#ingame_gui:rewardWindow/wgcq_player_reward/subHeaderText'
    REWARDWINDOW_WGCQ_PLAYER_REWARD_DESCTEXT = '#ingame_gui:rewardWindow/wgcq_player_reward/descText'
    REWARDWINDOW_WGCQ_PLAYER_REWARD_BTNLABEL = '#ingame_gui:rewardWindow/wgcq_player_reward/btnLabel'
    REWARDWINDOW_WGCQ_PLAYER_REWARD_SECONDBTNLABEL = '#ingame_gui:rewardWindow/wgcq_player_reward/secondBtnLabel'
    REWARDWINDOW_TWITCH0_HEADERTEXT = '#ingame_gui:rewardWindow/twitch0/headerText'
    REWARDWINDOW_TWITCH0_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch0/subHeaderText'
    REWARDWINDOW_TWITCH0_DESCTEXT = '#ingame_gui:rewardWindow/twitch0/descText'
    REWARDWINDOW_TWITCH0_BTNLABEL = '#ingame_gui:rewardWindow/twitch0/btnLabel'
    REWARDWINDOW_TWITCH1_HEADERTEXT = '#ingame_gui:rewardWindow/twitch1/headerText'
    REWARDWINDOW_TWITCH1_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch1/subHeaderText'
    REWARDWINDOW_TWITCH1_DESCTEXT = '#ingame_gui:rewardWindow/twitch1/descText'
    REWARDWINDOW_TWITCH1_BTNLABEL = '#ingame_gui:rewardWindow/twitch1/btnLabel'
    REWARDWINDOW_TWITCH2_HEADERTEXT = '#ingame_gui:rewardWindow/twitch2/headerText'
    REWARDWINDOW_TWITCH2_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch2/subHeaderText'
    REWARDWINDOW_TWITCH2_DESCTEXT = '#ingame_gui:rewardWindow/twitch2/descText'
    REWARDWINDOW_TWITCH2_BTNLABEL = '#ingame_gui:rewardWindow/twitch2/btnLabel'
    REWARDWINDOW_TWITCH3_HEADERTEXT = '#ingame_gui:rewardWindow/twitch3/headerText'
    REWARDWINDOW_TWITCH3_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch3/subHeaderText'
    REWARDWINDOW_TWITCH3_DESCTEXT = '#ingame_gui:rewardWindow/twitch3/descText'
    REWARDWINDOW_TWITCH3_BTNLABEL = '#ingame_gui:rewardWindow/twitch3/btnLabel'
    REWARDWINDOW_TWITCH4_HEADERTEXT = '#ingame_gui:rewardWindow/twitch4/headerText'
    REWARDWINDOW_TWITCH4_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch4/subHeaderText'
    REWARDWINDOW_TWITCH4_DESCTEXT = '#ingame_gui:rewardWindow/twitch4/descText'
    REWARDWINDOW_TWITCH4_BTNLABEL = '#ingame_gui:rewardWindow/twitch4/btnLabel'
    REWARDWINDOW_TWITCH5_HEADERTEXT = '#ingame_gui:rewardWindow/twitch5/headerText'
    REWARDWINDOW_TWITCH5_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch5/subHeaderText'
    REWARDWINDOW_TWITCH5_DESCTEXT = '#ingame_gui:rewardWindow/twitch5/descText'
    REWARDWINDOW_TWITCH5_BTNLABEL = '#ingame_gui:rewardWindow/twitch5/btnLabel'
    REWARDWINDOW_TWITCH6_HEADERTEXT = '#ingame_gui:rewardWindow/twitch6/headerText'
    REWARDWINDOW_TWITCH6_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch6/subHeaderText'
    REWARDWINDOW_TWITCH6_DESCTEXT = '#ingame_gui:rewardWindow/twitch6/descText'
    REWARDWINDOW_TWITCH6_BTNLABEL = '#ingame_gui:rewardWindow/twitch6/btnLabel'
    REWARDWINDOW_TWITCH7_HEADERTEXT = '#ingame_gui:rewardWindow/twitch7/headerText'
    REWARDWINDOW_TWITCH7_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch7/subHeaderText'
    REWARDWINDOW_TWITCH7_DESCTEXT = '#ingame_gui:rewardWindow/twitch7/descText'
    REWARDWINDOW_TWITCH7_BTNLABEL = '#ingame_gui:rewardWindow/twitch7/btnLabel'
    REWARDWINDOW_TWITCH8_HEADERTEXT = '#ingame_gui:rewardWindow/twitch8/headerText'
    REWARDWINDOW_TWITCH8_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch8/subHeaderText'
    REWARDWINDOW_TWITCH8_DESCTEXT = '#ingame_gui:rewardWindow/twitch8/descText'
    REWARDWINDOW_TWITCH8_BTNLABEL = '#ingame_gui:rewardWindow/twitch8/btnLabel'
    REWARDWINDOW_TWITCH9_HEADERTEXT = '#ingame_gui:rewardWindow/twitch9/headerText'
    REWARDWINDOW_TWITCH9_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch9/subHeaderText'
    REWARDWINDOW_TWITCH9_DESCTEXT = '#ingame_gui:rewardWindow/twitch9/descText'
    REWARDWINDOW_TWITCH9_BTNLABEL = '#ingame_gui:rewardWindow/twitch9/btnLabel'
    REWARDWINDOW_TWITCH10_HEADERTEXT = '#ingame_gui:rewardWindow/twitch10/headerText'
    REWARDWINDOW_TWITCH10_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch10/subHeaderText'
    REWARDWINDOW_TWITCH10_DESCTEXT = '#ingame_gui:rewardWindow/twitch10/descText'
    REWARDWINDOW_TWITCH10_BTNLABEL = '#ingame_gui:rewardWindow/twitch10/btnLabel'
    REWARDWINDOW_TWITCH11_HEADERTEXT = '#ingame_gui:rewardWindow/twitch11/headerText'
    REWARDWINDOW_TWITCH11_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch11/subHeaderText'
    REWARDWINDOW_TWITCH11_DESCTEXT = '#ingame_gui:rewardWindow/twitch11/descText'
    REWARDWINDOW_TWITCH11_BTNLABEL = '#ingame_gui:rewardWindow/twitch11/btnLabel'
    REWARDWINDOW_TWITCH12_HEADERTEXT = '#ingame_gui:rewardWindow/twitch12/headerText'
    REWARDWINDOW_TWITCH12_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch12/subHeaderText'
    REWARDWINDOW_TWITCH12_DESCTEXT = '#ingame_gui:rewardWindow/twitch12/descText'
    REWARDWINDOW_TWITCH12_BTNLABEL = '#ingame_gui:rewardWindow/twitch12/btnLabel'
    REWARDWINDOW_TWITCH13_HEADERTEXT = '#ingame_gui:rewardWindow/twitch13/headerText'
    REWARDWINDOW_TWITCH13_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch13/subHeaderText'
    REWARDWINDOW_TWITCH13_DESCTEXT = '#ingame_gui:rewardWindow/twitch13/descText'
    REWARDWINDOW_TWITCH13_BTNLABEL = '#ingame_gui:rewardWindow/twitch13/btnLabel'
    REWARDWINDOW_TWITCH14_HEADERTEXT = '#ingame_gui:rewardWindow/twitch14/headerText'
    REWARDWINDOW_TWITCH14_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch14/subHeaderText'
    REWARDWINDOW_TWITCH14_DESCTEXT = '#ingame_gui:rewardWindow/twitch14/descText'
    REWARDWINDOW_TWITCH14_BTNLABEL = '#ingame_gui:rewardWindow/twitch14/btnLabel'
    REWARDWINDOW_TWITCH15_HEADERTEXT = '#ingame_gui:rewardWindow/twitch15/headerText'
    REWARDWINDOW_TWITCH15_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch15/subHeaderText'
    REWARDWINDOW_TWITCH15_DESCTEXT = '#ingame_gui:rewardWindow/twitch15/descText'
    REWARDWINDOW_TWITCH15_BTNLABEL = '#ingame_gui:rewardWindow/twitch15/btnLabel'
    REWARDWINDOW_TWITCH16_HEADERTEXT = '#ingame_gui:rewardWindow/twitch16/headerText'
    REWARDWINDOW_TWITCH16_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch16/subHeaderText'
    REWARDWINDOW_TWITCH16_DESCTEXT = '#ingame_gui:rewardWindow/twitch16/descText'
    REWARDWINDOW_TWITCH16_BTNLABEL = '#ingame_gui:rewardWindow/twitch16/btnLabel'
    REWARDWINDOW_TWITCH17_HEADERTEXT = '#ingame_gui:rewardWindow/twitch17/headerText'
    REWARDWINDOW_TWITCH17_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch17/subHeaderText'
    REWARDWINDOW_TWITCH17_DESCTEXT = '#ingame_gui:rewardWindow/twitch17/descText'
    REWARDWINDOW_TWITCH17_BTNLABEL = '#ingame_gui:rewardWindow/twitch17/btnLabel'
    REWARDWINDOW_TWITCH18_HEADERTEXT = '#ingame_gui:rewardWindow/twitch18/headerText'
    REWARDWINDOW_TWITCH18_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch18/subHeaderText'
    REWARDWINDOW_TWITCH18_DESCTEXT = '#ingame_gui:rewardWindow/twitch18/descText'
    REWARDWINDOW_TWITCH18_BTNLABEL = '#ingame_gui:rewardWindow/twitch18/btnLabel'
    REWARDWINDOW_TWITCH19_HEADERTEXT = '#ingame_gui:rewardWindow/twitch19/headerText'
    REWARDWINDOW_TWITCH19_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch19/subHeaderText'
    REWARDWINDOW_TWITCH19_DESCTEXT = '#ingame_gui:rewardWindow/twitch19/descText'
    REWARDWINDOW_TWITCH19_BTNLABEL = '#ingame_gui:rewardWindow/twitch19/btnLabel'
    REWARDWINDOW_TWITCH20_HEADERTEXT = '#ingame_gui:rewardWindow/twitch20/headerText'
    REWARDWINDOW_TWITCH20_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch20/subHeaderText'
    REWARDWINDOW_TWITCH20_DESCTEXT = '#ingame_gui:rewardWindow/twitch20/descText'
    REWARDWINDOW_TWITCH20_BTNLABEL = '#ingame_gui:rewardWindow/twitch20/btnLabel'
    REWARDWINDOW_TWITCH21_HEADERTEXT = '#ingame_gui:rewardWindow/twitch21/headerText'
    REWARDWINDOW_TWITCH21_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch21/subHeaderText'
    REWARDWINDOW_TWITCH21_DESCTEXT = '#ingame_gui:rewardWindow/twitch21/descText'
    REWARDWINDOW_TWITCH21_BTNLABEL = '#ingame_gui:rewardWindow/twitch21/btnLabel'
    REWARDWINDOW_TWITCH22_HEADERTEXT = '#ingame_gui:rewardWindow/twitch22/headerText'
    REWARDWINDOW_TWITCH22_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch22/subHeaderText'
    REWARDWINDOW_TWITCH22_DESCTEXT = '#ingame_gui:rewardWindow/twitch22/descText'
    REWARDWINDOW_TWITCH22_BTNLABEL = '#ingame_gui:rewardWindow/twitch22/btnLabel'
    REWARDWINDOW_TWITCH23_HEADERTEXT = '#ingame_gui:rewardWindow/twitch23/headerText'
    REWARDWINDOW_TWITCH23_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch23/subHeaderText'
    REWARDWINDOW_TWITCH23_DESCTEXT = '#ingame_gui:rewardWindow/twitch23/descText'
    REWARDWINDOW_TWITCH23_BTNLABEL = '#ingame_gui:rewardWindow/twitch23/btnLabel'
    REWARDWINDOW_TWITCH24_HEADERTEXT = '#ingame_gui:rewardWindow/twitch24/headerText'
    REWARDWINDOW_TWITCH24_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch24/subHeaderText'
    REWARDWINDOW_TWITCH24_DESCTEXT = '#ingame_gui:rewardWindow/twitch24/descText'
    REWARDWINDOW_TWITCH24_BTNLABEL = '#ingame_gui:rewardWindow/twitch24/btnLabel'
    REWARDWINDOW_TWITCH25_HEADERTEXT = '#ingame_gui:rewardWindow/twitch25/headerText'
    REWARDWINDOW_TWITCH25_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch25/subHeaderText'
    REWARDWINDOW_TWITCH25_DESCTEXT = '#ingame_gui:rewardWindow/twitch25/descText'
    REWARDWINDOW_TWITCH25_BTNLABEL = '#ingame_gui:rewardWindow/twitch25/btnLabel'
    REWARDWINDOW_TWITCH26_HEADERTEXT = '#ingame_gui:rewardWindow/twitch26/headerText'
    REWARDWINDOW_TWITCH26_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch26/subHeaderText'
    REWARDWINDOW_TWITCH26_DESCTEXT = '#ingame_gui:rewardWindow/twitch26/descText'
    REWARDWINDOW_TWITCH26_BTNLABEL = '#ingame_gui:rewardWindow/twitch26/btnLabel'
    REWARDWINDOW_TWITCH27_HEADERTEXT = '#ingame_gui:rewardWindow/twitch27/headerText'
    REWARDWINDOW_TWITCH27_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch27/subHeaderText'
    REWARDWINDOW_TWITCH27_DESCTEXT = '#ingame_gui:rewardWindow/twitch27/descText'
    REWARDWINDOW_TWITCH27_BTNLABEL = '#ingame_gui:rewardWindow/twitch27/btnLabel'
    REWARDWINDOW_TWITCH28_HEADERTEXT = '#ingame_gui:rewardWindow/twitch28/headerText'
    REWARDWINDOW_TWITCH28_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch28/subHeaderText'
    REWARDWINDOW_TWITCH28_DESCTEXT = '#ingame_gui:rewardWindow/twitch28/descText'
    REWARDWINDOW_TWITCH28_BTNLABEL = '#ingame_gui:rewardWindow/twitch28/btnLabel'
    REWARDWINDOW_TWITCH29_HEADERTEXT = '#ingame_gui:rewardWindow/twitch29/headerText'
    REWARDWINDOW_TWITCH29_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch29/subHeaderText'
    REWARDWINDOW_TWITCH29_DESCTEXT = '#ingame_gui:rewardWindow/twitch29/descText'
    REWARDWINDOW_TWITCH29_BTNLABEL = '#ingame_gui:rewardWindow/twitch29/btnLabel'
    REWARDWINDOW_TWITCH30_HEADERTEXT = '#ingame_gui:rewardWindow/twitch30/headerText'
    REWARDWINDOW_TWITCH30_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch30/subHeaderText'
    REWARDWINDOW_TWITCH30_DESCTEXT = '#ingame_gui:rewardWindow/twitch30/descText'
    REWARDWINDOW_TWITCH30_BTNLABEL = '#ingame_gui:rewardWindow/twitch30/btnLabel'
    REWARDWINDOW_TWITCH31_HEADERTEXT = '#ingame_gui:rewardWindow/twitch31/headerText'
    REWARDWINDOW_TWITCH31_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch31/subHeaderText'
    REWARDWINDOW_TWITCH31_DESCTEXT = '#ingame_gui:rewardWindow/twitch31/descText'
    REWARDWINDOW_TWITCH31_BTNLABEL = '#ingame_gui:rewardWindow/twitch31/btnLabel'
    REWARDWINDOW_TWITCH32_HEADERTEXT = '#ingame_gui:rewardWindow/twitch32/headerText'
    REWARDWINDOW_TWITCH32_SUBHEADERTEXT = '#ingame_gui:rewardWindow/twitch32/subHeaderText'
    REWARDWINDOW_TWITCH32_DESCTEXT = '#ingame_gui:rewardWindow/twitch32/descText'
    REWARDWINDOW_TWITCH32_BTNLABEL = '#ingame_gui:rewardWindow/twitch32/btnLabel'
    REWARDWINDOW_TWITCH33_HEADERTEXT = '#ingame_gui:rewardWindow/twitch33/headerText'
    REWARDWINDOW_TWITCH33_DESCTEXT = '#ingame_gui:rewardWindow/twitch33/descText'
    REWARDWINDOW_TWITCH33_MAINREWARD_1 = '#ingame_gui:rewardWindow/twitch33/mainReward_1'
    REWARDWINDOW_TWITCH33_MAINREWARD_2 = '#ingame_gui:rewardWindow/twitch33/mainReward_2'
    REWARDWINDOW_TWITCH33_MAINREWARD_3 = '#ingame_gui:rewardWindow/twitch33/mainReward_3'
    REWARDWINDOW_TWITCH33_MAINREWARD_4 = '#ingame_gui:rewardWindow/twitch33/mainReward_4'
    REWARDWINDOW_TWITCH34_HEADERTEXT = '#ingame_gui:rewardWindow/twitch34/headerText'
    REWARDWINDOW_TWITCH34_DESCTEXT = '#ingame_gui:rewardWindow/twitch34/descText'
    REWARDWINDOW_TWITCH34_MAINREWARD_1 = '#ingame_gui:rewardWindow/twitch34/mainReward_1'
    REWARDWINDOW_TWITCH34_MAINREWARD_2 = '#ingame_gui:rewardWindow/twitch34/mainReward_2'
    REWARDWINDOW_TWITCH34_MAINREWARD_3 = '#ingame_gui:rewardWindow/twitch34/mainReward_3'
    REWARDWINDOW_TWITCH34_MAINREWARD_4 = '#ingame_gui:rewardWindow/twitch34/mainReward_4'
    REWARDWINDOW_TWITCH35_HEADERTEXT = '#ingame_gui:rewardWindow/twitch35/headerText'
    REWARDWINDOW_TWITCH35_DESCTEXT = '#ingame_gui:rewardWindow/twitch35/descText'
    REWARDWINDOW_TWITCH35_MAINREWARD_1 = '#ingame_gui:rewardWindow/twitch35/mainReward_1'
    REWARDWINDOW_TWITCH35_MAINREWARD_2 = '#ingame_gui:rewardWindow/twitch35/mainReward_2'
    REWARDWINDOW_TWITCH35_MAINREWARD_3 = '#ingame_gui:rewardWindow/twitch35/mainReward_3'
    REWARDWINDOW_TWITCH35_MAINREWARD_4 = '#ingame_gui:rewardWindow/twitch35/mainReward_4'
    REWARDWINDOW_TWITCH36_HEADERTEXT = '#ingame_gui:rewardWindow/twitch36/headerText'
    REWARDWINDOW_TWITCH36_DESCTEXT = '#ingame_gui:rewardWindow/twitch36/descText'
    REWARDWINDOW_TWITCH36_MAINREWARD_1 = '#ingame_gui:rewardWindow/twitch36/mainReward_1'
    REWARDWINDOW_TWITCH36_MAINREWARD_2 = '#ingame_gui:rewardWindow/twitch36/mainReward_2'
    REWARDWINDOW_TWITCH36_MAINREWARD_3 = '#ingame_gui:rewardWindow/twitch36/mainReward_3'
    REWARDWINDOW_TWITCH36_MAINREWARD_4 = '#ingame_gui:rewardWindow/twitch36/mainReward_4'
    REWARDWINDOW_TWITCH37_HEADERTEXT = '#ingame_gui:rewardWindow/twitch37/headerText'
    REWARDWINDOW_TWITCH37_DESCTEXT = '#ingame_gui:rewardWindow/twitch37/descText'
    REWARDWINDOW_TWITCH37_MAINREWARD_1 = '#ingame_gui:rewardWindow/twitch37/mainReward_1'
    REWARDWINDOW_TWITCH37_MAINREWARD_2 = '#ingame_gui:rewardWindow/twitch37/mainReward_2'
    REWARDWINDOW_TWITCH37_MAINREWARD_3 = '#ingame_gui:rewardWindow/twitch37/mainReward_3'
    REWARDWINDOW_TWITCH37_MAINREWARD_4 = '#ingame_gui:rewardWindow/twitch37/mainReward_4'
    REWARDWINDOW_TWITCH37_BTNLABEL = '#ingame_gui:rewardWindow/twitch37/btnLabel'
    BATTLEPROGRESS_HINT_NOBINDINGKEY = '#ingame_gui:battleProgress/hint/noBindingKey'
    HELPSCREEN_HINT_PRESS = '#ingame_gui:helpScreen/hint/press'
    HELPSCREEN_HINT_DESCRIPTION = '#ingame_gui:helpScreen/hint/description'
    HELPSCREEN_MAPBOX_PRESS = '#ingame_gui:helpScreen/mapbox/press'
    HELPSCREEN_MAPBOX_DESCRIPTION = '#ingame_gui:helpScreen/mapbox/description'
    COMMANDERCAM_HINT_DESCRIPTION = '#ingame_gui:commanderCam/hint/description'
    BATTLECOMMUNICATION_HINT_PRESS = '#ingame_gui:battleCommunication/hint/press'
    BATTLECOMMUNICATION_HINT_DESCRIPTION = '#ingame_gui:battleCommunication/hint/description'
    BURNOUT_HINT_ENGINEDAMAGEWARNING = '#ingame_gui:burnout/hint/engineDamageWarning'
    BURNOUT_HINT_ENGINEDAMAGED = '#ingame_gui:burnout/hint/engineDamaged'
    REWARDWINDOW_ANNIVERSARY_GA_WINHEADERTEXT = '#ingame_gui:rewardWindow/anniversary_ga/winHeaderText'
    REWARDWINDOW_ANNIVERSARY_GA_HEADERTEXT = '#ingame_gui:rewardWindow/anniversary_ga/headerText'
    REWARDWINDOW_ANNIVERSARY_GA_SUBHEADERTEXT = '#ingame_gui:rewardWindow/anniversary_ga/subHeaderText'
    REWARDWINDOW_ANNIVERSARY_GA_DESCTEXT = '#ingame_gui:rewardWindow/anniversary_ga/descText'
    REWARDWINDOW_ANNIVERSARY_GA_BTNLABEL = '#ingame_gui:rewardWindow/anniversary_ga/btnLabel'
    QUICKREPLY_HINT_PRESS = '#ingame_gui:quickReply/hint/press'
    QUICKREPLY_HINT_TOHELP = '#ingame_gui:quickReply/hint/toHelp'
    QUICKREPLY_HINT_TOACKNOWLEDGE = '#ingame_gui:quickReply/hint/toAcknowledge'
    QUICKREPLY_HINT_TOTHANK = '#ingame_gui:quickReply/hint/toThank'
    REWARDWINDOW_PIGGYBANK_WINHEADERTEXT = '#ingame_gui:rewardWindow/piggyBank/winHeaderText'
    REWARDWINDOW_PIGGYBANK_HEADERTEXT = '#ingame_gui:rewardWindow/piggyBank/headerText'
    REWARDWINDOW_PIGGYBANK_SUBHEADERTEXT = '#ingame_gui:rewardWindow/piggyBank/subHeaderText'
    REWARDWINDOW_PIGGYBANK_DESCTEXT = '#ingame_gui:rewardWindow/piggyBank/descText'
    REWARDWINDOW_PIGGYBANK_BTNLABEL = '#ingame_gui:rewardWindow/piggyBank/btnLabel'
    REWARDWINDOW_COMMANDER_MARINA_HEADERTEXT = '#ingame_gui:rewardWindow/commander_marina/headerText'
    REWARDWINDOW_COMMANDER_MARINA_SUBHEADERTEXT = '#ingame_gui:rewardWindow/commander_marina/subHeaderText'
    REWARDWINDOW_COMMANDER_MARINA_DESCTEXT = '#ingame_gui:rewardWindow/commander_marina/descText'
    REWARDWINDOW_COMMANDER_MARINA_BTNLABEL = '#ingame_gui:rewardWindow/commander_marina/btnLabel'
    REWARDWINDOW_COMMANDER_PATRICK_HEADERTEXT = '#ingame_gui:rewardWindow/commander_patrick/headerText'
    REWARDWINDOW_COMMANDER_PATRICK_SUBHEADERTEXT = '#ingame_gui:rewardWindow/commander_patrick/subHeaderText'
    REWARDWINDOW_COMMANDER_PATRICK_DESCTEXT = '#ingame_gui:rewardWindow/commander_patrick/descText'
    REWARDWINDOW_COMMANDER_PATRICK_BTNLABEL = '#ingame_gui:rewardWindow/commander_patrick/btnLabel'
    DAMAGEINDICATOR_FRIENDLYFIRE_NODAMAGELABEL = '#ingame_gui:damageIndicator/friendlyFire/noDamageLabel'
    PREBATTLEMARKER_PREBATTLEMARKER_0 = '#ingame_gui:prebattlemarker/prebattlemarker_0'
    PREBATTLEMARKER_PREBATTLEMARKER_1 = '#ingame_gui:prebattlemarker/prebattlemarker_1'
    PREBATTLEMARKER_PREBATTLEMARKER_2 = '#ingame_gui:prebattlemarker/prebattlemarker_2'
    PREBATTLEMARKER_PREBATTLEMARKER_3 = '#ingame_gui:prebattlemarker/prebattlemarker_3'
    PREBATTLEMARKER_PREBATTLEMARKER_4 = '#ingame_gui:prebattlemarker/prebattlemarker_4'
    PREBATTLEMARKER_PREBATTLEMARKER_5 = '#ingame_gui:prebattlemarker/prebattlemarker_5'
    PREBATTLEMARKER_PREBATTLEMARKER_6 = '#ingame_gui:prebattlemarker/prebattlemarker_6'
    PREBATTLEMARKER_PREBATTLEMARKER_7 = '#ingame_gui:prebattlemarker/prebattlemarker_7'
    PREBATTLEMARKER_PREBATTLEMARKER_8 = '#ingame_gui:prebattlemarker/prebattlemarker_8'
    PREBATTLEMARKER_PREBATTLEMARKER_9 = '#ingame_gui:prebattlemarker/prebattlemarker_9'
    PREBATTLEMARKER_PREBATTLEMARKER_10 = '#ingame_gui:prebattlemarker/prebattlemarker_10'
    PREBATTLEMARKER_PREBATTLEMARKER_11 = '#ingame_gui:prebattlemarker/prebattlemarker_11'
    PREBATTLEMARKER_PREBATTLEMARKER_12 = '#ingame_gui:prebattlemarker/prebattlemarker_12'
    PREBATTLEMARKER_PREBATTLEMARKER_13 = '#ingame_gui:prebattlemarker/prebattlemarker_13'
    PREBATTLEMARKER_PREBATTLEMARKER_14 = '#ingame_gui:prebattlemarker/prebattlemarker_14'
    PREBATTLEMARKER_PREBATTLEMARKER_15 = '#ingame_gui:prebattlemarker/prebattlemarker_15'
    PREBATTLEMARKER_PREBATTLEMARKER_16 = '#ingame_gui:prebattlemarker/prebattlemarker_16'
    PREBATTLEMARKER_PREBATTLEMARKER_17 = '#ingame_gui:prebattlemarker/prebattlemarker_17'
    PREBATTLEMARKER_PREBATTLEMARKER_18 = '#ingame_gui:prebattlemarker/prebattlemarker_18'
    PREBATTLEMARKER_PREBATTLEMARKER_19 = '#ingame_gui:prebattlemarker/prebattlemarker_19'
    PREBATTLEMARKER_PREBATTLEMARKER_20 = '#ingame_gui:prebattlemarker/prebattlemarker_20'
    PREBATTLEMARKER_PREBATTLEMARKER_21 = '#ingame_gui:prebattlemarker/prebattlemarker_21'
    PREBATTLEMARKER_PREBATTLEMARKER_22 = '#ingame_gui:prebattlemarker/prebattlemarker_22'
    PREBATTLEMARKER_PREBATTLEMARKER_23 = '#ingame_gui:prebattlemarker/prebattlemarker_23'
    PREBATTLEMARKER_PREBATTLEMARKER_24 = '#ingame_gui:prebattlemarker/prebattlemarker_24'
    PREBATTLEMARKER_PREBATTLEMARKER_25 = '#ingame_gui:prebattlemarker/prebattlemarker_25'
    PREBATTLEMARKER_PREBATTLEMARKER_26 = '#ingame_gui:prebattlemarker/prebattlemarker_26'
    PREBATTLEMARKER_PREBATTLEMARKER_27 = '#ingame_gui:prebattlemarker/prebattlemarker_27'
    PREBATTLEMARKER_PREBATTLEMARKER_28 = '#ingame_gui:prebattlemarker/prebattlemarker_28'
    PREBATTLEMARKER_PREBATTLEMARKER_29 = '#ingame_gui:prebattlemarker/prebattlemarker_29'
    PREBATTLEMARKER_PREBATTLEMARKER_30 = '#ingame_gui:prebattlemarker/prebattlemarker_30'
    PREBATTLEMARKER_PREBATTLEMARKER_31 = '#ingame_gui:prebattlemarker/prebattlemarker_31'
    PREBATTLEMARKER_PREBATTLEMARKER_32 = '#ingame_gui:prebattlemarker/prebattlemarker_32'
    PREBATTLEMARKER_PREBATTLEMARKER_33 = '#ingame_gui:prebattlemarker/prebattlemarker_33'
    PREBATTLEMARKER_PREBATTLEMARKER_34 = '#ingame_gui:prebattlemarker/prebattlemarker_34'
    PREBATTLEMARKER_PREBATTLEMARKER_35 = '#ingame_gui:prebattlemarker/prebattlemarker_35'
    PREBATTLEMARKER_PREBATTLEMARKER_36 = '#ingame_gui:prebattlemarker/prebattlemarker_36'
    PREBATTLEMARKER_PREBATTLEMARKER_37 = '#ingame_gui:prebattlemarker/prebattlemarker_37'
    PREBATTLEMARKER_PREBATTLEMARKER_38 = '#ingame_gui:prebattlemarker/prebattlemarker_38'
    PREBATTLEMARKER_PREBATTLEMARKER_39 = '#ingame_gui:prebattlemarker/prebattlemarker_39'
    PREBATTLEMARKER_PREBATTLEMARKER_40 = '#ingame_gui:prebattlemarker/prebattlemarker_40'
    PREBATTLEMARKER_PREBATTLEMARKER_41 = '#ingame_gui:prebattlemarker/prebattlemarker_41'
    PREBATTLEMARKER_PREBATTLEMARKER_42 = '#ingame_gui:prebattlemarker/prebattlemarker_42'
    PREBATTLEMARKER_PREBATTLEMARKER_43 = '#ingame_gui:prebattlemarker/prebattlemarker_43'
    PREBATTLEMARKER_PREBATTLEMARKER_44 = '#ingame_gui:prebattlemarker/prebattlemarker_44'
    PREBATTLEMARKER_PREBATTLEMARKER_45 = '#ingame_gui:prebattlemarker/prebattlemarker_45'
    PREBATTLEMARKER_PREBATTLEMARKER_46 = '#ingame_gui:prebattlemarker/prebattlemarker_46'
    PREBATTLEMARKER_PREBATTLEMARKER_47 = '#ingame_gui:prebattlemarker/prebattlemarker_47'
    PREBATTLEMARKER_PREBATTLEMARKER_48 = '#ingame_gui:prebattlemarker/prebattlemarker_48'
    PREBATTLEMARKER_PREBATTLEMARKER_49 = '#ingame_gui:prebattlemarker/prebattlemarker_49'
    PREBATTLEMARKER_PREBATTLEMARKER_50 = '#ingame_gui:prebattlemarker/prebattlemarker_50'
    PREBATTLEMARKER_PREBATTLEMARKER_51 = '#ingame_gui:prebattlemarker/prebattlemarker_51'
    OPTDEVICERESURRECTION_ENGINE = '#ingame_gui:optDeviceResurrection/engine'
    OPTDEVICERESURRECTION_FUELTANK = '#ingame_gui:optDeviceResurrection/fuelTank'
    OPTDEVICERESURRECTION_AMMOBAY = '#ingame_gui:optDeviceResurrection/ammoBay'
    LEVELPROGRESS_MAXLEVEL = '#ingame_gui:levelProgress/maxLevel'
    PREBATTLEAMMUNITIONPANEL_HEADER = '#ingame_gui:prebattleAmmunitionPanel/header'
    PREBATTLEAMMUNITIONPANEL_FOOTER = '#ingame_gui:prebattleAmmunitionPanel/footer'
    PREBATTLEAMMUNITIONPANEL_WAITINFORPLAYERS = '#ingame_gui:prebattleAmmunitionPanel/waitinForPlayers'
    PREBATTLEAMMUNITIONPANEL_LOADINGTIMER = '#ingame_gui:prebattleAmmunitionPanel/loadingTimer'
    PREBATTLEAMMUNITIONPANEL_CURRENTSETUP = '#ingame_gui:prebattleAmmunitionPanel/currentSetup'
    PERSONAL_RESERVES_HINT_PRESS = '#ingame_gui:personal_reserves/hint/press'
    PERSONAL_RESERVES_HINT_DESCRIPTION = '#ingame_gui:personal_reserves/hint/description'
    HINT_NOBINDINGKEY = '#ingame_gui:hint/noBindingKey'
    DESTROYTIMER_LIFTOVER = '#ingame_gui:destroyTimer/liftOver'
    DANGER_ZONE_INDICATOR = '#ingame_gui:danger_zone/indicator'
    WARNING_ZONE_INDICATOR = '#ingame_gui:warning_zone/indicator'
    STATUSNOTIFICATIONTIMERS_STATICDEATHZONE = '#ingame_gui:statusNotificationTimers/staticDeathZone'
    DEVMAPS_HINT_PRESS = '#ingame_gui:devMaps/hint/press'
    DEVMAPS_HINT_DESCRIPTION = '#ingame_gui:devMaps/hint/description'
    DEVMAPS_MAPINFO_TEXT = '#ingame_gui:devMaps/mapInfo/text'
    DEVMAPS_MAPINFO_INFO = '#ingame_gui:devMaps/mapInfo/info'
    CHAT_SHORTCUTS_ENUM = (CHAT_SHORTCUTS_ATTENTION_TO_POSITION_GRIDINFO,
     CHAT_SHORTCUTS_ATTENTION_TO_POSITION,
     CHAT_SHORTCUTS_GOING_THERE_GRIDINFO,
     CHAT_SHORTCUTS_GOING_THERE,
     CHAT_SHORTCUTS_HELP_ME,
     CHAT_SHORTCUTS_RELOADING_GUN,
     CHAT_SHORTCUTS_RELOADING_CASSETTE,
     CHAT_SHORTCUTS_RELOADING_READY,
     CHAT_SHORTCUTS_RELOADING_READY_CASSETTE,
     CHAT_SHORTCUTS_RELOADING_UNAVAILABLE,
     CHAT_SHORTCUTS_SPG_AIM_AREA_GRIDINFO,
     CHAT_SHORTCUTS_SPG_AIM_AREA,
     CHAT_SHORTCUTS_SPG_AIM_AREA_RELOADING_GRIDINFO,
     CHAT_SHORTCUTS_SPG_AIM_AREA_RELOADING,
     CHAT_SHORTCUTS_SPG_AIM_AREA_EMPTY_GRIDINFO,
     CHAT_SHORTCUTS_ATTACK_ENEMY,
     CHAT_SHORTCUTS_ATTACKING_ENEMY,
     CHAT_SHORTCUTS_ATTACK_ENEMY_WITH_SPG,
     CHAT_SHORTCUTS_ATTACK_ENEMY_WITH_SPG_EMPTY,
     CHAT_SHORTCUTS_ATTACK_ENEMY_WITH_SPG_RELOADING,
     CHAT_SHORTCUTS_ATTENTION_TO_BASE_ATK,
     CHAT_SHORTCUTS_ATTENTION_TO_BASE_ATK_NUMBERED,
     CHAT_SHORTCUTS_ATTACKING_BASE,
     CHAT_SHORTCUTS_ATTACKING_BASE_NUMBERED,
     CHAT_SHORTCUTS_ATTENTION_TO_OBJECTIVE_ATK,
     CHAT_SHORTCUTS_ATTENTION_TO_OBJECTIVE_ATK_AUTOCOMMIT,
     CHAT_SHORTCUTS_ATTENTION_TO_BASE_DEF,
     CHAT_SHORTCUTS_ATTENTION_TO_BASE_DEF_NUMBERED,
     CHAT_SHORTCUTS_DEFENDING_BASE,
     CHAT_SHORTCUTS_DEFENDING_BASE_NUMBERED,
     CHAT_SHORTCUTS_ATTENTION_TO_OBJECTIVE_DEF,
     CHAT_SHORTCUTS_ATTENTION_TO_OBJECTIVE_DEF_AUTOCOMMIT,
     CHAT_SHORTCUTS_HELP_ME_EX,
     CHAT_SHORTCUTS_SUPPORTING_ALLY,
     CHAT_SHORTCUTS_TURN_BACK,
     CHAT_SHORTCUTS_THANKS,
     CHAT_SHORTCUTS_POSITIVE,
     CHAT_SHORTCUTS_AFFIRMATIVE,
     CHAT_SHORTCUTS_NEGATIVE,
     CHAT_SHORTCUTS_ATTENTION_TO_CELL,
     CHAT_SHORTCUTS_GLOBAL_MSG_ATK_SAVE_TANKS,
     CHAT_SHORTCUTS_GLOBAL_MSG_DEF_SAVE_TANKS,
     CHAT_SHORTCUTS_GLOBAL_MSG_ATK_TIME,
     CHAT_SHORTCUTS_GLOBAL_MSG_DEF_TIME,
     CHAT_SHORTCUTS_GLOBAL_MSG_LANE_WEST,
     CHAT_SHORTCUTS_GLOBAL_MSG_LANE_CENTER,
     CHAT_SHORTCUTS_GLOBAL_MSG_LANE_EAST,
     CHAT_SHORTCUTS_GLOBAL_MSG_ATK_FOCUS_HQ,
     CHAT_SHORTCUTS_GLOBAL_MSG_DEF_FOCUS_HQ)
    CHAT_EXAMPLE_ENUM = (CHAT_EXAMPLE_ATTENTION_TO_BASE_DEF,
     CHAT_EXAMPLE_ATTENTION_TO_BASE_ATK,
     CHAT_EXAMPLE_GOING_THERE,
     CHAT_EXAMPLE_GLOBAL_MSG_DEF_SAVE_TANKS,
     CHAT_EXAMPLE_GLOBAL_MSG_ATK_SAVE_TANKS,
     CHAT_EXAMPLE_GLOBAL_MSG_ATK_TIME,
     CHAT_EXAMPLE_GLOBAL_MSG_DEF_TIME,
     CHAT_EXAMPLE_GLOBAL_MSG_LANE_WEST,
     CHAT_EXAMPLE_GLOBAL_MSG_LANE_CENTER,
     CHAT_EXAMPLE_GLOBAL_MSG_LANE_EAST,
     CHAT_EXAMPLE_GLOBAL_MSG_ATK_FOCUS_HQ,
     CHAT_EXAMPLE_GLOBAL_MSG_DEF_FOCUS_HQ,
     CHAT_EXAMPLE_ATTACK_ENEMY,
     CHAT_EXAMPLE_RELOADING_GUN,
     CHAT_EXAMPLE_RELOADING_CASSETTE,
     CHAT_EXAMPLE_RELOADING_READY,
     CHAT_EXAMPLE_TURN_BACK,
     CHAT_EXAMPLE_RELOADING_READY_CASSETTE,
     CHAT_EXAMPLE_RELOADING_UNAVAILABLE,
     CHAT_EXAMPLE_HELP_ME,
     CHAT_EXAMPLE_HELP_ME_EX,
     CHAT_EXAMPLE_POSITIVE,
     CHAT_EXAMPLE_AFFIRMATIVE,
     CHAT_EXAMPLE_NEGATIVE,
     CHAT_EXAMPLE_THANKS,
     CHAT_EXAMPLE_ATTENTION_TO_CELL,
     CHAT_EXAMPLE_ATTACK_ENEMY_WITH_SPG,
     CHAT_EXAMPLE_SPG_AIM_AREA,
     CHAT_EXAMPLE_ATTENTION_TO_POSITION,
     CHAT_EXAMPLE_SUPPORTING_ALLY)
    EFFICIENCYRIBBONS_ENUM = (EFFICIENCYRIBBONS_ARMOR,
     EFFICIENCYRIBBONS_CAPTURE,
     EFFICIENCYRIBBONS_DAMAGE,
     EFFICIENCYRIBBONS_RAM,
     EFFICIENCYRIBBONS_BURN,
     EFFICIENCYRIBBONS_DEFENCE,
     EFFICIENCYRIBBONS_KILL,
     EFFICIENCYRIBBONS_SPOTTED,
     EFFICIENCYRIBBONS_ASSISTTRACK,
     EFFICIENCYRIBBONS_ASSISTSPOT,
     EFFICIENCYRIBBONS_CRITS,
     EFFICIENCYRIBBONS_WORLDCOLLISION,
     EFFICIENCYRIBBONS_RECEIVEDCRITS,
     EFFICIENCYRIBBONS_RECEIVEDDAMAGE,
     EFFICIENCYRIBBONS_RECEIVEDBURN,
     EFFICIENCYRIBBONS_BERSERKER,
     EFFICIENCYRIBBONS_SPAWNEDBOTDMG,
     EFFICIENCYRIBBONS_RECEIVEDDMGBYSPAWNEDBOT,
     EFFICIENCYRIBBONS_DAMAGEBYMINEFIELD,
     EFFICIENCYRIBBONS_RECEIVEDBYMINEFIELD,
     EFFICIENCYRIBBONS_RECEIVEDBYSMOKE,
     EFFICIENCYRIBBONS_DEALTDAMAGEBYCORRODINGSHOT,
     EFFICIENCYRIBBONS_RECEIVEDBYCORRODINGSHOT,
     EFFICIENCYRIBBONS_DEALTDAMAGEBYFIRECIRCLE,
     EFFICIENCYRIBBONS_RECEIVEDBYFIRECIRCLE,
     EFFICIENCYRIBBONS_DEALTDAMAGEBYCLINGBRANDER,
     EFFICIENCYRIBBONS_RECEIVEDBYCLINGBRANDER,
     EFFICIENCYRIBBONS_DEALTDAMAGEBYTHUNDERSTRIKE,
     EFFICIENCYRIBBONS_RECEIVEDBYTHUNDERSTRIKE,
     EFFICIENCYRIBBONS_RECEIVEDRAM,
     EFFICIENCYRIBBONS_RECEIVEDWORLDCOLLISION,
     EFFICIENCYRIBBONS_VEHICLERECOVERY,
     EFFICIENCYRIBBONS_BONUSRIBBON,
     EFFICIENCYRIBBONS_STUN,
     EFFICIENCYRIBBONS_ASSISTSTUN,
     EFFICIENCYRIBBONS_DEATHZONE,
     EFFICIENCYRIBBONS_STATICDEATHZONE,
     EFFICIENCYRIBBONS_CANNONDMG,
     EFFICIENCYRIBBONS_AIRSTRIKEDMG,
     EFFICIENCYRIBBONS_ARTILLERYDMG,
     EFFICIENCYRIBBONS_ENEMYSECTORCAPTURED,
     EFFICIENCYRIBBONS_DESTRUCTIBLEDAMAGED,
     EFFICIENCYRIBBONS_DESTRUCTIBLEDESTROYED,
     EFFICIENCYRIBBONS_DESTRUCTIBLESDEFENDED,
     EFFICIENCYRIBBONS_DEFENDERBONUS,
     EFFICIENCYRIBBONS_ASSISTBYABILITY)
    SIEGEMODE_HINT_FORMODE_ENUM = (SIEGEMODE_HINT_FORMODE_0,
     SIEGEMODE_HINT_FORMODE_1,
     SIEGEMODE_HINT_FORMODE_2,
     SIEGEMODE_HINT_FORMODE_3)
    REWARDWINDOW_ALL_HEADERTEXT_ENUM = (REWARDWINDOW_BASE_HEADERTEXT,
     REWARDWINDOW_WGCQ_CLAN_REWARD_HEADERTEXT,
     REWARDWINDOW_WGCQ_PLAYER_REWARD_HEADERTEXT,
     REWARDWINDOW_TWITCH0_HEADERTEXT,
     REWARDWINDOW_TWITCH1_HEADERTEXT,
     REWARDWINDOW_TWITCH2_HEADERTEXT,
     REWARDWINDOW_TWITCH3_HEADERTEXT,
     REWARDWINDOW_TWITCH4_HEADERTEXT,
     REWARDWINDOW_TWITCH5_HEADERTEXT,
     REWARDWINDOW_TWITCH6_HEADERTEXT,
     REWARDWINDOW_TWITCH7_HEADERTEXT,
     REWARDWINDOW_TWITCH8_HEADERTEXT,
     REWARDWINDOW_TWITCH9_HEADERTEXT,
     REWARDWINDOW_TWITCH10_HEADERTEXT,
     REWARDWINDOW_TWITCH11_HEADERTEXT,
     REWARDWINDOW_TWITCH12_HEADERTEXT,
     REWARDWINDOW_TWITCH13_HEADERTEXT,
     REWARDWINDOW_TWITCH14_HEADERTEXT,
     REWARDWINDOW_TWITCH15_HEADERTEXT,
     REWARDWINDOW_TWITCH16_HEADERTEXT,
     REWARDWINDOW_TWITCH17_HEADERTEXT,
     REWARDWINDOW_TWITCH18_HEADERTEXT,
     REWARDWINDOW_TWITCH19_HEADERTEXT,
     REWARDWINDOW_TWITCH20_HEADERTEXT,
     REWARDWINDOW_TWITCH21_HEADERTEXT,
     REWARDWINDOW_TWITCH22_HEADERTEXT,
     REWARDWINDOW_TWITCH23_HEADERTEXT,
     REWARDWINDOW_TWITCH24_HEADERTEXT,
     REWARDWINDOW_TWITCH25_HEADERTEXT,
     REWARDWINDOW_TWITCH26_HEADERTEXT,
     REWARDWINDOW_TWITCH27_HEADERTEXT,
     REWARDWINDOW_TWITCH28_HEADERTEXT,
     REWARDWINDOW_TWITCH29_HEADERTEXT,
     REWARDWINDOW_TWITCH30_HEADERTEXT,
     REWARDWINDOW_TWITCH31_HEADERTEXT,
     REWARDWINDOW_TWITCH32_HEADERTEXT,
     REWARDWINDOW_TWITCH33_HEADERTEXT,
     REWARDWINDOW_TWITCH34_HEADERTEXT,
     REWARDWINDOW_TWITCH35_HEADERTEXT,
     REWARDWINDOW_TWITCH36_HEADERTEXT,
     REWARDWINDOW_TWITCH37_HEADERTEXT,
     REWARDWINDOW_ANNIVERSARY_GA_HEADERTEXT,
     REWARDWINDOW_PIGGYBANK_HEADERTEXT,
     REWARDWINDOW_COMMANDER_MARINA_HEADERTEXT,
     REWARDWINDOW_COMMANDER_PATRICK_HEADERTEXT)
    REWARDWINDOW_ALL_SUBHEADERTEXT_ENUM = (REWARDWINDOW_BASE_SUBHEADERTEXT,
     REWARDWINDOW_WGCQ_CLAN_REWARD_SUBHEADERTEXT,
     REWARDWINDOW_WGCQ_PLAYER_REWARD_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH0_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH1_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH2_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH3_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH4_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH5_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH6_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH7_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH8_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH9_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH10_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH11_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH12_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH13_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH14_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH15_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH16_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH17_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH18_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH19_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH20_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH21_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH22_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH23_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH24_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH25_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH26_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH27_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH28_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH29_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH30_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH31_SUBHEADERTEXT,
     REWARDWINDOW_TWITCH32_SUBHEADERTEXT,
     REWARDWINDOW_ANNIVERSARY_GA_SUBHEADERTEXT,
     REWARDWINDOW_PIGGYBANK_SUBHEADERTEXT,
     REWARDWINDOW_COMMANDER_MARINA_SUBHEADERTEXT,
     REWARDWINDOW_COMMANDER_PATRICK_SUBHEADERTEXT)
    REWARDWINDOW_ALL_BTNLABEL_ENUM = (REWARDWINDOW_BASE_BTNLABEL,
     REWARDWINDOW_WGCQ_CLAN_REWARD_BTNLABEL,
     REWARDWINDOW_WGCQ_PLAYER_REWARD_BTNLABEL,
     REWARDWINDOW_TWITCH0_BTNLABEL,
     REWARDWINDOW_TWITCH1_BTNLABEL,
     REWARDWINDOW_TWITCH2_BTNLABEL,
     REWARDWINDOW_TWITCH3_BTNLABEL,
     REWARDWINDOW_TWITCH4_BTNLABEL,
     REWARDWINDOW_TWITCH5_BTNLABEL,
     REWARDWINDOW_TWITCH6_BTNLABEL,
     REWARDWINDOW_TWITCH7_BTNLABEL,
     REWARDWINDOW_TWITCH8_BTNLABEL,
     REWARDWINDOW_TWITCH9_BTNLABEL,
     REWARDWINDOW_TWITCH10_BTNLABEL,
     REWARDWINDOW_TWITCH11_BTNLABEL,
     REWARDWINDOW_TWITCH12_BTNLABEL,
     REWARDWINDOW_TWITCH13_BTNLABEL,
     REWARDWINDOW_TWITCH14_BTNLABEL,
     REWARDWINDOW_TWITCH15_BTNLABEL,
     REWARDWINDOW_TWITCH16_BTNLABEL,
     REWARDWINDOW_TWITCH17_BTNLABEL,
     REWARDWINDOW_TWITCH18_BTNLABEL,
     REWARDWINDOW_TWITCH19_BTNLABEL,
     REWARDWINDOW_TWITCH20_BTNLABEL,
     REWARDWINDOW_TWITCH21_BTNLABEL,
     REWARDWINDOW_TWITCH22_BTNLABEL,
     REWARDWINDOW_TWITCH23_BTNLABEL,
     REWARDWINDOW_TWITCH24_BTNLABEL,
     REWARDWINDOW_TWITCH25_BTNLABEL,
     REWARDWINDOW_TWITCH26_BTNLABEL,
     REWARDWINDOW_TWITCH27_BTNLABEL,
     REWARDWINDOW_TWITCH28_BTNLABEL,
     REWARDWINDOW_TWITCH29_BTNLABEL,
     REWARDWINDOW_TWITCH30_BTNLABEL,
     REWARDWINDOW_TWITCH31_BTNLABEL,
     REWARDWINDOW_TWITCH32_BTNLABEL,
     REWARDWINDOW_TWITCH37_BTNLABEL,
     REWARDWINDOW_ANNIVERSARY_GA_BTNLABEL,
     REWARDWINDOW_PIGGYBANK_BTNLABEL,
     REWARDWINDOW_COMMANDER_MARINA_BTNLABEL,
     REWARDWINDOW_COMMANDER_PATRICK_BTNLABEL)
    REWARDWINDOW_ALL_DESCTEXT_ENUM = (REWARDWINDOW_BASE_DESCTEXT,
     REWARDWINDOW_WGCQ_CLAN_REWARD_DESCTEXT,
     REWARDWINDOW_WGCQ_PLAYER_REWARD_DESCTEXT,
     REWARDWINDOW_TWITCH0_DESCTEXT,
     REWARDWINDOW_TWITCH1_DESCTEXT,
     REWARDWINDOW_TWITCH2_DESCTEXT,
     REWARDWINDOW_TWITCH3_DESCTEXT,
     REWARDWINDOW_TWITCH4_DESCTEXT,
     REWARDWINDOW_TWITCH5_DESCTEXT,
     REWARDWINDOW_TWITCH6_DESCTEXT,
     REWARDWINDOW_TWITCH7_DESCTEXT,
     REWARDWINDOW_TWITCH8_DESCTEXT,
     REWARDWINDOW_TWITCH9_DESCTEXT,
     REWARDWINDOW_TWITCH10_DESCTEXT,
     REWARDWINDOW_TWITCH11_DESCTEXT,
     REWARDWINDOW_TWITCH12_DESCTEXT,
     REWARDWINDOW_TWITCH13_DESCTEXT,
     REWARDWINDOW_TWITCH14_DESCTEXT,
     REWARDWINDOW_TWITCH15_DESCTEXT,
     REWARDWINDOW_TWITCH16_DESCTEXT,
     REWARDWINDOW_TWITCH17_DESCTEXT,
     REWARDWINDOW_TWITCH18_DESCTEXT,
     REWARDWINDOW_TWITCH19_DESCTEXT,
     REWARDWINDOW_TWITCH20_DESCTEXT,
     REWARDWINDOW_TWITCH21_DESCTEXT,
     REWARDWINDOW_TWITCH22_DESCTEXT,
     REWARDWINDOW_TWITCH23_DESCTEXT,
     REWARDWINDOW_TWITCH24_DESCTEXT,
     REWARDWINDOW_TWITCH25_DESCTEXT,
     REWARDWINDOW_TWITCH26_DESCTEXT,
     REWARDWINDOW_TWITCH27_DESCTEXT,
     REWARDWINDOW_TWITCH28_DESCTEXT,
     REWARDWINDOW_TWITCH29_DESCTEXT,
     REWARDWINDOW_TWITCH30_DESCTEXT,
     REWARDWINDOW_TWITCH31_DESCTEXT,
     REWARDWINDOW_TWITCH32_DESCTEXT,
     REWARDWINDOW_TWITCH33_DESCTEXT,
     REWARDWINDOW_TWITCH34_DESCTEXT,
     REWARDWINDOW_TWITCH35_DESCTEXT,
     REWARDWINDOW_TWITCH36_DESCTEXT,
     REWARDWINDOW_TWITCH37_DESCTEXT,
     REWARDWINDOW_ANNIVERSARY_GA_DESCTEXT,
     REWARDWINDOW_PIGGYBANK_DESCTEXT,
     REWARDWINDOW_COMMANDER_MARINA_DESCTEXT,
     REWARDWINDOW_COMMANDER_PATRICK_DESCTEXT)

    @classmethod
    def chat_shortcuts(cls, key0):
        outcome = '#ingame_gui:chat_shortcuts/{}'.format(key0)
        if outcome not in cls.CHAT_SHORTCUTS_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def chat_example(cls, key0):
        outcome = '#ingame_gui:chat_example/{}'.format(key0)
        if outcome not in cls.CHAT_EXAMPLE_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def efficiencyribbons(cls, key0):
        outcome = '#ingame_gui:efficiencyRibbons/{}'.format(key0)
        if outcome not in cls.EFFICIENCYRIBBONS_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def siegeModeHint(cls, mode):
        outcome = '#ingame_gui:siegeMode/hint/forMode/{}'.format(mode)
        if outcome not in cls.SIEGEMODE_HINT_FORMODE_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def getRewardWindowHeader(cls, eventName):
        outcome = '#ingame_gui:rewardWindow/{}/headerText'.format(eventName)
        if outcome not in cls.REWARDWINDOW_ALL_HEADERTEXT_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def getRewardWindowSubHeader(cls, eventName):
        outcome = '#ingame_gui:rewardWindow/{}/subHeaderText'.format(eventName)
        if outcome not in cls.REWARDWINDOW_ALL_SUBHEADERTEXT_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def getRewardWindowBtnLabel(cls, eventName):
        outcome = '#ingame_gui:rewardWindow/{}/btnLabel'.format(eventName)
        if outcome not in cls.REWARDWINDOW_ALL_BTNLABEL_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def getRewardWindowDescText(cls, eventName):
        outcome = '#ingame_gui:rewardWindow/{}/descText'.format(eventName)
        if outcome not in cls.REWARDWINDOW_ALL_DESCTEXT_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome
