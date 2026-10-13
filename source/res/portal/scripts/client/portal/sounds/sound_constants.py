# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/sounds/sound_constants.py
import WWISE
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings

class LanguageSwitch(CONST_CONTAINER):
    GROUP = 'SWITCH_ext_ev_halloween_witches_vo_language'
    RU = 'SWITCH_ext_ev_halloween_witches_vo_language_ru'


class CharacterSwitch(CONST_CONTAINER):
    GROUP = 'SWITCH_ext_ev_portal_vo_character'
    TSAREV = 'SWITCH_ext_ev_portal_vo_character_2'
    YAGINSKAYA = 'SWITCH_ext_ev_portal_vo_character_3'
    VASILYEVA = 'SWITCH_ext_ev_portal_vo_character_1'
    KOSCHCEEV = 'SWITCH_ext_ev_portal_vo_character_4'


class CaptureCampsSwitch(CONST_CONTAINER):
    GROUP = 'SWITCH_ext_ev_portal_tower_captured'
    FIRST = 'SWITCH_ext_ev_portal_tower_captured_1'
    SECOND_THIRD = 'SWITCH_ext_ev_portal_tower_captured_2_3'
    FOURTH = 'SWITCH_ext_ev_portal_tower_captured_4'


class ExperienceSwitch(CONST_CONTAINER):
    GROUP = 'SWITCH_ext_ev_portal_player_experience'
    BEGINNER = 'SWITCH_ext_ev_portal_battle_counter_beginner'
    EXPERT = 'SWITCH_ext_ev_portal_battle_counter_expert'


class GameplayVoiceovers(CONST_CONTAINER):
    PLAYER_KILLED = 'vo_ev_portal_gameplay_player_vehicle_destroyed'
    ENEMY_KILLED = 'vo_ev_portal_gameplay_vehicle_destroyed'
    NORMAL_RESPAWN = 'vo_ev_portal_gameplay_vehicle_respawn'
    RESPAWN_ON_FINAL_STAGE = 'vo_ev_portal_gameplay_katrina_vehicle_respawn'
    CAMP_BECAME_CAPTURABLE = 'vo_ev_portal_gameplay_camp_guard_defeated'
    CAMP_CAPTURED = 'vo_ev_portal_gameplay_camp_captured'
    PORTAL_FIRST_DAMAGE = 'vo_ev_portal_gameplay_first_boss_damaged'
    PORTAL_DESTROYED = 'vo_ev_portal_gameplay_first_boss_destroyed'
    BOSS_FIGHT_VEHICLE_DESTROYED = 'vo_ev_portal_gameplay_katrina_vehicle_respawn'
    TWO_MINUTES_LEFT = 'vo_ev_portal_gameplay_time_required'
    RATTE_WIN = 'vo_ev_portal_gameplay_bossfight_victory'
    PORTAL_WIN = 'vo_ev_portal_gameplay_victory'
    DEFEAT = 'vo_ev_portal_gameplay_defeat'
    ANTAGONIST_IDLE = 'vo_ev_portal_gameplay_antagonist_idle'


SWITCH_CHARACTERS_FOR_NATIONS = {'ussr': CharacterSwitch.KOSCHCEEV,
 'france': CharacterSwitch.VASILYEVA,
 'uk': CharacterSwitch.TSAREV,
 'poland': CharacterSwitch.YAGINSKAYA}

class PortalUISound(CONST_CONTAINER):
    EMPTY_SOUND = ''
    PRESSED_SOUND = 'ev_portal_gui_ability_button'
    CANCEL_SOUND = 'ev_portal_gui_ability_button_cancel'
    READY_SOUND = 'ev_portal_gui_ability_button_ready'
    APPLY_SOUND = 'ev_portal_gui_ability_apply'
    NOT_READY_SOUND = 'ev_portal_gui_ability_button_not_ready'
    NOT_APPLY_SOUND = 'ev_portal_gui_ability_not_apply'


class PortalAbilitySound(CONST_CONTAINER):
    SHIELD_START = 'ev_portal_ability_mass_shield_start'
    SHIELD_STOP = 'ev_portal_ability_mass_shield_stop'
    CHANGE_SHOT_ACTIVATION = 'ev_portal_ability_enemy_possession_on'
    CHANGE_SHOT_DEACTIVATION = 'ev_portal_ability_enemy_possession_off'
    CHANGE_SHOT_POSSESSION_START = 'ev_portal_ability_enemy_possession_start'
    CHANGE_SHOT_POSSESSION_STOP = 'ev_portal_ability_enemy_possession_stop'
    RELOAD_AURA_START = 'ev_portal_ability_pc_aura_reload_start'
    RELOAD_AURA_STOP = 'ev_portal_ability_pc_aura_reload_stop'
    GUIDED_MISSILE_START = 'ev_portal_ability_ptur_start'
    GUIDED_MISSILE_FLY = 'ev_portal_ability_ptur_fly_pc'
    GUIDED_MISSILE_DETONATION = 'ev_portal_ability_ptur_detonation'
    TRAP_START = 'ev_portal_ability_trap_start'
    TRAP_STOP = 'ev_portal_ability_trap_stop'
    BERSERK_START = 'ev_portal_ability_berserk_start_pc'
    BERSERK_STOP = 'ev_portal_ability_berserk_stop_pc'


class PortalMusicState(object):
    ENTER = 'ev_portal_music_on'
    EXIT = 'ev_portal_music_off'
    STATE_GROUP = 'STATE_ev_portal_music'
    LOBBY = 'STATE_ev_portal_music_lobby'
    MATCHMAKER = 'STATE_ev_portal_music_match_maker'
    LOADING = 'STATE_ev_portal_music_loading_screen'
    RESPAWN = 'STATE_ev_portal_music_respawn'
    BATTLE = 'STATE_ev_portal_music_battle'
    BOSS_FIGHT = 'STATE_ev_portal_music_bossfight'
    SUPER_BOSS_FIGHT = 'STATE_ev_portal_music_superbossfight'
    AFTER_BATTLE = 'STATE_ev_portal_music_coda'
    RESULT_SCREEN_WIN = 'STATE_ev_portal_music_result_screen_win'
    RESULT_SCREEN_DEFEAT = 'STATE_ev_portal_music_result_screen_defeat'
    PROGRESSION = 'STATE_ev_portal_music_lobby_progression'

    @staticmethod
    def setState(state):
        WWISE.WW_setState(PortalMusicState.STATE_GROUP, state)


class PortalBattleUISound(CONST_CONTAINER):
    POSTMORTEM_ON = 'ev_portal_gameplay_postmortem_on'
    POSTMORTEM_OFF = 'ev_portal_gameplay_postmortem_off'
    GAMEPLAY_ENTER = 'ev_portal_gameplay_enter'
    GAMEPLAY_EXIT = 'ev_portal_gameplay_exit'
    PREBATTLE_TO_BATTLE_TIMER = 2
    PREBATTLE_TO_BATTLE_ON = 'ev_portal_prebattle_tobattle_transition_on'
    PREBATTLE_TO_BATTLE_OFF = 'ev_portal_prebattle_tobattle_transition_off'
    HANGAR_ENTER = 'ev_portal_hangar_enter'
    HANGAR_EXIT = 'ev_portal_hangar_exit'


class PortalBattleSound(CONST_CONTAINER):
    SENTINEL_ON = 'ev_portal_gameplay_guards_on'
    SENTINEL_DAMAGE = 'ev_portal_gameplay_guards_damage_vehicle'
    SENTINEL_OFF = 'ev_portal_gameplay_guards_off'
    TELEPORT_START = 'ev_portal_gui_teleport_charge_start'
    TELEPORT_END = 'ev_portal_gui_teleport_charge_end'
    TELEPORT_LEAVE = 'ev_portal_gui_teleport_charge_leave'
    TELEPORT_PLANE_BLOCK_TO_ON = 'ev_portal_gameplay_teleport_ready'
    TELEPORT_PLANE_ON = 'ev_portal_gameplay_teleport_ready_idle'
    TELEPORT_PLANE_OUT_PC = 'ev_portal_gameplay_teleport_out_PC'
    TELEPORT_PLANE_IN_PC = 'ev_portal_gameplay_teleport_in_PC'
    TELEPORT_PLANE_ON_TO_COOLDOWN = 'ev_portal_gameplay_teleport_ready_to_cooldown'
    TELEPORT_PLANE_IDLE = 'ev_portal_gameplay_teleport_cooldown_idle'
    TELEPORT_PLANE_COOLDOWN_TO_ON = 'ev_portal_gameplay_teleport_cooldown_to_ready'
    INCINERATING_AURA_DAMAGE = 'ev_portal_gui_gameplay_boss_damage_vehicle'


class PortalEndGameUISound(CONST_CONTAINER):
    WIN = 'ev_portal_gui_gameplay_notification_win'
    DEFEAT = 'ev_portal_gui_gameplay_notification_defeat'


class SOUNDS(CONST_CONTAINER):
    OVERLAY_HANGAR_GENERAL = 'STATE_overlay_hangar_general'
    OVERLAY_HANGAR_GENERAL_ON = 'STATE_overlay_hangar_general_on'
    OVERLAY_HANGAR_GENERAL_OFF = 'STATE_overlay_hangar_general_off'


class CampSound(CONST_CONTAINER):
    CAPTURE_START = 'ev_portal_gui_camp_capture_start'
    CAPTURE_COMPLETED = 'ev_portal_gui_camp_capture_completed'
    CAPTURE_LEAVE = 'ev_portal_gui_camp_capture_leave'
    ALL_CAPTURED = 'ev_portal_gameplay_all_camps_captured'


class EntryPointSound(CONST_CONTAINER):
    HOVER_ON = 'ev_portal_hangar_gui_hover_on'
    HOVER_OFF = 'ev_portal_hangar_gui_hover_off'
    CLICK = 'ev_portal_hangar_gui_click'


PORTAL_PROGRESSION_SOUND_SPACE = CommonSoundSpaceSettings(name='PORTAL_PROGRESSION', entranceStates={PortalMusicState.STATE_GROUP: PortalMusicState.PROGRESSION}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='ev_portal_hangar_progression_enter', exitEvent='ev_portal_hangar_progression_exit')
PORTAL_UPGRADE_SOUND_SPACE = CommonSoundSpaceSettings(name='PORTAL_UPGRADE', entranceStates={}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='ev_portal_hangar_upgrade_enter', exitEvent='ev_portal_hangar_upgrade_exit')
PORTAL_COMPLEXITY_UNLOCK_SOUND_SPACE = CommonSoundSpaceSettings(name='PORTAL_COMPLEXITY_UNLOCK', entranceStates={SOUNDS.OVERLAY_HANGAR_GENERAL: SOUNDS.OVERLAY_HANGAR_GENERAL_ON}, exitStates={SOUNDS.OVERLAY_HANGAR_GENERAL: SOUNDS.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
PORTAL_UPGRADE_INFO_SOUND_SPACE = CommonSoundSpaceSettings(name='PORTAL_UPGRADE_INFO', entranceStates={SOUNDS.OVERLAY_HANGAR_GENERAL: SOUNDS.OVERLAY_HANGAR_GENERAL_ON}, exitStates={SOUNDS.OVERLAY_HANGAR_GENERAL: SOUNDS.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
PORTAL_UPGRADE_RESET_SOUND_SPACE = CommonSoundSpaceSettings(name='PORTAL_UPGRADE_RESET', entranceStates={SOUNDS.OVERLAY_HANGAR_GENERAL: SOUNDS.OVERLAY_HANGAR_GENERAL_ON}, exitStates={SOUNDS.OVERLAY_HANGAR_GENERAL: SOUNDS.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
PORTAL_BATTLE_QUEUE_SOUND_SPACE = CommonSoundSpaceSettings(name='PORTAL_BATTLE_QUEUE', entranceStates={PortalMusicState.STATE_GROUP: PortalMusicState.MATCHMAKER}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
PORTAL_BATTLE_RESULT_SOUND_SPACE = CommonSoundSpaceSettings(name='PORTAL_BATTLE_RESULT', entranceStates={}, exitStates={PortalMusicState.STATE_GROUP: PortalMusicState.LOBBY}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
PORTAL_LOBBY_SOUND_SPACE = CommonSoundSpaceSettings(name='PORTAL_LOBBY', entranceStates={}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=PortalBattleUISound.HANGAR_ENTER, exitEvent='')
