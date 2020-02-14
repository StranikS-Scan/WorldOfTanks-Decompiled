# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/epic_sound_constants.py
from gui.Scaleform.genConsts.GAME_MESSAGES_CONSTS import GAME_MESSAGES_CONSTS
from epic_constants import EPIC_BATTLE_TEAM_ID

class EPIC_TIME_WWEVENTS(object):
    EB_BATTLE_END = 'eb_time_over'
    EB_STOP_TICKING = 'time_countdown_stop'
    EB_RESPAWN_COUNT_DOWN_SOUND_ID = {True: 'timer',
     False: 'timer_stop'}


class EPIC_OVERTIME_SOUND_NOTIFICATIONS(object):
    EB_OVERTIME_COUNTDOWN = 'eb_overtime_countdown'
    EB_OVERTIME_COUNTDOWN_STOP = 'eb_overtime_countdown_stop'
    BF_EB_OVERTIME = {True: 'eb_overtime_ATK',
     False: 'eb_overtime_DEF'}
    BF_EB_OVERTIME_START = 'eb_overtime_start'


class EPIC_METAGAME_WWISE_SOUND_EVENTS(object):
    EB_WELCOME_SCREEN_BUTTON_ANIM = 'eb_welcome_01'
    EB_WELCOME_SCREEN_MOVE = 'eb_welcome_02'
    EB_WELCOME_SCREEN_DONE = 'eb_welcome_03'
    EB_ACHIEVED_RANK = 'eb_achieved_rank'
    EB_LEVEL_REACHED = 'eb_level_reached'
    EB_ABILITY_UPGRADE = 'eb_ability_upgrade_02'
    EB_PRESTIGE_RESET = 'eb_prestige_reset'
    EB_PROGRESS_BAR_START = 'gui_progress_bar'
    EB_PROGRESS_BAR_STOP = 'gui_progress_bar_stop'
    EB_LEVEL_REACHED_MAX = 'eb_level_reached_maximum'


class EPIC_SOUND(object):
    EPIC_MSG_SOUNDS_ENABLED = True
    BF_EB_ABILITY_LIST = ()
    BF_EB_ABILITY_DEPLOYING = 'eb_ability_deployed'
    BF_EB_ABILITY_INSPIRE_DEPLOYED = 'eb_ability_inspire_deployed'
    BF_EB_EQUIPMENT_SOUND_LIST = ('INSPIRE', 'ARTILLERY', 'RECON', 'BOMBER')
    BF_EB_ABILITY_USED = {'RECON': BF_EB_ABILITY_DEPLOYING,
     'BOMBER': BF_EB_ABILITY_DEPLOYING,
     'ARTILLERY': BF_EB_ABILITY_DEPLOYING,
     'SMOKE': BF_EB_ABILITY_DEPLOYING,
     'INSPIRE': BF_EB_ABILITY_INSPIRE_DEPLOYED}
    EB_READY_FOR_DEPLOYMENT_ID = {True: 'eb_ready_for_deployment',
     False: 'eb_stop_ready_for_deployment'}
    BF_EB_START_BATTLE = {EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER: 'vo_eb_start_ATK',
     EPIC_BATTLE_TEAM_ID.TEAM_DEFENDER: 'vo_eb_start_DEF'}
    BF_EB_GLOBAL_MESSAGE = 'eb_general_message'
    BF_EB_WPN_ZONE_PROTECTION = 'eb_warships_firing'
    BF_EB_BASE_CAPTURE_SIREN_SOUND = 'eb_zone_capture'
    BF_EB_ENTER_CLOSED_ZONE = 'eb_enter_closed_zone'
    BF_EB_ENTER_PROTECTION_ZONE = 'eb_enter_landing_zone'
    BF_EB_AIR_STRIKE_WARNING = 'eb_airstrike_warning_defender'
    BF_EB_LEFT_CLICK_TO_FOLLOW = 'eb_left_click_to_follow'
    BF_EB_SPECTATOR_MODE_FOLLOW_TANK = 'eb_follow_tank'
    BF_EB_LANDING_ZONE_PROTECTION = 'eb_closed_zone_artillery_fire'
    BF_EB_CLOSED_ZONE_ARTILLERY = 'eb_closed_zone_artillery_fire'
    BF_EB_RECOVERY_REQUESTED = 'eb_recovery_requested'
    BF_EB_RECOVERY_SUCCESSFUL = 'eb_recovery_successful'
    BF_EB_RECOVERY_CANCELED = 'eb_recovery_canceled'
    BF_EB_NEW_OBJECTIVE = 'eb_new_battle_objective'
    BF_EB_SPECIFIC_TIME = 'eb_specific_time'
    BF_EB_GENERAL = 'eb_general'
    BF_EB_RANK_UP = {'show': 'eb_rank_up_show',
     'hide': 'eb_rank_up_hide'}
    BF_EB_RETREAT_SUCCESSFUL = 'eb_retreat_successful'
    BF_EB_ZONE_CONTESTED_ATK = {'A': 'eb_zone_contested_ATK_A',
     'B': 'eb_zone_contested_ATK_B',
     'C': 'eb_zone_contested_ATK_C',
     'D': 'eb_zone_contested_ATK_D',
     'E': 'eb_zone_contested_ATK_E',
     'F': 'eb_zone_contested_ATK_F'}
    BF_EB_ZONE_CONTESTED_DEF = {'A': 'eb_zone_contested_DEF_A',
     'B': 'eb_zone_contested_DEF_B',
     'C': 'eb_zone_contested_DEF_C',
     'D': 'eb_zone_contested_DEF_D',
     'E': 'eb_zone_contested_DEF_E',
     'F': 'eb_zone_contested_DEF_F'}
    BF_EB_ZONE_CAPTURED_ATK = {True: 'eb_own_zone_captured_ATK',
     False: 'eb_other_zone_captured_ATK'}
    BF_EB_ZONE_CAPTURED_DEF = {True: 'eb_own_zone_captured_DEF',
     False: 'eb_other_zone_captured_DEF'}
    BF_EB_AIRSTRIKE_ATK = 'eb_airstrike_ATK'
    BF_EB_AIRSTRIKE_DEF = 'eb_airstrike_DEF'
    BF_EB_AIR_SUPPORT = {GAME_MESSAGES_CONSTS.BASE_CAPTURED_POSITIVE: BF_EB_AIRSTRIKE_ATK,
     GAME_MESSAGES_CONSTS.BASE_CAPTURED: BF_EB_AIRSTRIKE_DEF}
    BF_EB_MAIN_OBJECTIVES_REACHED_ATK = {True: 'eb_main_objectives_reached_ATK',
     False: 'eb_main_objectives_reached_other_ATK'}
    BF_EB_MAIN_OBJECTIVES_REACHED_DEF = {True: 'eb_main_objectives_reached_DEF',
     False: 'eb_main_objectives_reached_other_DEF'}
    BF_EB_OBJECTIVE_UNDER_ATTACK_ATK = {1: 'eb_objective_under_attack_ATK_1',
     2: 'eb_objective_under_attack_ATK_2',
     3: 'eb_objective_under_attack_ATK_3',
     4: 'eb_objective_under_attack_ATK_4',
     5: 'eb_objective_under_attack_ATK_5'}
    BF_EB_OBJECTIVE_UNDER_ATTACK_DEF = {1: 'eb_objective_under_attack_DEF_1',
     2: 'eb_objective_under_attack_DEF_2',
     3: 'eb_objective_under_attack_DEF_3',
     4: 'eb_objective_under_attack_DEF_4',
     5: 'eb_objective_under_attack_DEF_5'}
    BF_EB_MAIN_OBJECTIVES_ONE_DESTROYED = 'eb_objective_destroyed'
    BF_EB_MAIN_OBJECTIVES_ONLY_ONE_LEFT = 'eb_main_objectives_only_one_left'
    BF_EB_MAIN_OBJECTIVES_ALL_DOWN = 'eb_main_objectives_all_down'
    BF_EB_HQ_DESTROYED_ATK_OR_DEF = {GAME_MESSAGES_CONSTS.OBJECTIVE_DESTROYED_POSITIVE: '_ATK',
     GAME_MESSAGES_CONSTS.OBJECTIVE_DESTROYED: '_DEF'}
    BF_EB_REINFORCEMENTS_ARRIVED = 'eb_reinforcements_arrived'
    BF_EB_REINFORCEMENTS_CEASED = 'eb_reinforcements_ceased'
    BF_EB_TIME_OUT = {True: 'eb_time_out_VICTORY',
     False: 'eb_time_out_DEFEAT'}
    BF_EB_ALL_ENEMIES_DESTROYED = {True: 'eb_all_enemies_destroyed_VICTORY',
     False: 'eb_all_enemies_destroyed_DEFEAT'}
    BF_EB_STOP_TICKING = 'time_countdown_stop'
    BF_EB_VO_MESSAGES = {GAME_MESSAGES_CONSTS.BASE_CAPTURED: BF_EB_ZONE_CAPTURED_DEF,
     GAME_MESSAGES_CONSTS.BASE_CAPTURED_POSITIVE: BF_EB_ZONE_CAPTURED_ATK,
     GAME_MESSAGES_CONSTS.OBJECTIVE_DESTROYED: BF_EB_MAIN_OBJECTIVES_ONE_DESTROYED,
     GAME_MESSAGES_CONSTS.OBJECTIVE_DESTROYED_POSITIVE: BF_EB_MAIN_OBJECTIVES_ONE_DESTROYED,
     GAME_MESSAGES_CONSTS.HQ_BATTLE_STARTED: BF_EB_MAIN_OBJECTIVES_REACHED_DEF,
     GAME_MESSAGES_CONSTS.HQ_BATTLE_STARTED_POSITIVE: BF_EB_MAIN_OBJECTIVES_REACHED_ATK,
     GAME_MESSAGES_CONSTS.TIME_REMAINING: BF_EB_SPECIFIC_TIME,
     GAME_MESSAGES_CONSTS.TIME_REMAINING_POSITIVE: BF_EB_SPECIFIC_TIME,
     GAME_MESSAGES_CONSTS.CAPTURE_BASE: BF_EB_NEW_OBJECTIVE,
     GAME_MESSAGES_CONSTS.DEFEND_BASE: BF_EB_NEW_OBJECTIVE,
     GAME_MESSAGES_CONSTS.DESTROY_OBJECTIVE: BF_EB_NEW_OBJECTIVE,
     GAME_MESSAGES_CONSTS.DEFEND_OBJECTIVE: BF_EB_NEW_OBJECTIVE,
     GAME_MESSAGES_CONSTS.OVERTIME: EPIC_OVERTIME_SOUND_NOTIFICATIONS.BF_EB_OVERTIME,
     GAME_MESSAGES_CONSTS.BASE_CONTESTED: BF_EB_ZONE_CONTESTED_DEF,
     GAME_MESSAGES_CONSTS.BASE_CONTESTED_POSITIVE: BF_EB_ZONE_CONTESTED_ATK,
     GAME_MESSAGES_CONSTS.OBJECTIVE_UNDER_ATTACK: BF_EB_OBJECTIVE_UNDER_ATTACK_DEF,
     GAME_MESSAGES_CONSTS.OBJECTIVE_UNDER_ATTACK_POSITIVE: BF_EB_OBJECTIVE_UNDER_ATTACK_ATK,
     GAME_MESSAGES_CONSTS.RETREAT_SUCCESSFUL: BF_EB_RETREAT_SUCCESSFUL,
     GAME_MESSAGES_CONSTS.GENERAL_RANK_REACHED: BF_EB_GENERAL,
     GAME_MESSAGES_CONSTS.RANK_UP: BF_EB_RANK_UP}


class BF_EB_MAIN_OBJECTIVES_SOUND_NOTIFICATIONS(object):
    ONE_DESTROYED = EPIC_SOUND.BF_EB_MAIN_OBJECTIVES_ONE_DESTROYED
    ONLY_ONE_LEFT = EPIC_SOUND.BF_EB_MAIN_OBJECTIVES_ONLY_ONE_LEFT
    ALL_DOWN = EPIC_SOUND.BF_EB_MAIN_OBJECTIVES_ALL_DOWN
