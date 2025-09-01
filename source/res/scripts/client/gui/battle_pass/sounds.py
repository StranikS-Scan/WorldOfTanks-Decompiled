# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/sounds.py
import WWISE
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings

class SOUNDS(CONST_CONTAINER):
    DIALOG_BP_STATE = 'STATE_overlay_hangar_general'
    DIALOG_BP_STATE_ON = 'STATE_overlay_hangar_general_on'
    DIALOG_BP_STATE_OFF = 'STATE_overlay_hangar_general_off'
    BATTLE_PASS_SOUND_SPACE = 'tasks'
    BATTLE_PASS_STATE_PLACE = 'STATE_hangar_place'
    BATTLE_PASS_STATE_PLACE_TASKS = 'STATE_hangar_place_tasks'
    BATTLE_PASS_TASKS_ENTER = 'tasks_enter'
    BATTLE_PASS_TASKS_EXIT = 'tasks_exit'
    HOLIDAY_SOUND_SPACE = 'tasks_holiday'
    HOLIDAY_STATE_PLACE = 'STATE_hangar_place'
    HOLIDAY_STATE_PLACE_TASKS = 'STATE_hangar_place_tasks'
    HOLIDAY_TASKS_ENTER = 'tasks_holiday_enter'
    HOLIDAY_TASKS_EXIT = 'tasks_holiday_exit'


BATTLE_PASS_TASKS_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.BATTLE_PASS_SOUND_SPACE, entranceStates={SOUNDS.BATTLE_PASS_STATE_PLACE: SOUNDS.BATTLE_PASS_STATE_PLACE_TASKS}, exitStates={}, enterEvent='', exitEvent='', persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
ACTIVATE_CHAPTER_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.DIALOG_BP_STATE, entranceStates={SOUNDS.DIALOG_BP_STATE: SOUNDS.DIALOG_BP_STATE_ON}, exitStates={SOUNDS.DIALOG_BP_STATE: SOUNDS.DIALOG_BP_STATE_OFF}, enterEvent='', exitEvent='', persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
HOLIDAY_TASKS_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.HOLIDAY_SOUND_SPACE, entranceStates={SOUNDS.HOLIDAY_STATE_PLACE: SOUNDS.HOLIDAY_STATE_PLACE_TASKS}, exitStates={}, enterEvent=SOUNDS.HOLIDAY_TASKS_ENTER, exitEvent=SOUNDS.HOLIDAY_TASKS_EXIT, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)

class BattlePassSounds(CONST_CONTAINER):
    CONFIRM_BUY = 'bp_overlay_pay'
    REWARD_SCREEN = 'bp_reward_screen'
    TANK_POINTS_CAP = 'bp_tank_point_done'
    VIDEO_PAUSE = 'bp_video_pause'
    VIDEO_RESUME = 'bp_video_resume'
    VIDEO_STOP = 'bp_video_stop'
    VOICEOVER_STOP = 'bp_voiceovers_stop'
    REGULAR_VOICEOVER_STOP = 'bp_regular_voiceovers_stop'
    HOLIDAY_VOICEOVER_STOP = 'bp_holiday_voiceovers_stop'
    HOLIDAY_REWARD_SCREEN = 'bp_holiday_reward_screen'
    TASKS_ENTER = 'tasks_enter'
    TASKS_EXIT = 'tasks_exit'
    SPECIAL_TASKS_ENTER = 'tasks_special_enter'
    SPECIAL_TASKS_EXIT = 'tasks_special_exit'


def switchDialogBPSoundFilter(on=True):
    WWISE.WW_setState(SOUNDS.DIALOG_BP_STATE, SOUNDS.DIALOG_BP_STATE_ON if on else SOUNDS.DIALOG_BP_STATE_OFF)
