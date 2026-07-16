# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/sounds.py
from __future__ import absolute_import
import logging
import WWISE
from gui.impl import backport
from gui.impl.gen import R
from gui.sounds.filters import StatesGroup, States
from helpers.dependency import replace_none_kwargs
from shared_utils import CONST_CONTAINER
from skeletons.gui.game_control import IBattlePassController
from sound_gui_manager import CommonSoundSpaceSettings
_logger = logging.getLogger(__name__)
BATTLE_PASS_SOUND_SPACE = 'tasks'

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
    HOLIDAY_TASKS_ENTER = 'tasks_holiday_enter'
    HOLIDAY_TASKS_EXIT = 'tasks_holiday_exit'


class BattlePassStates(CONST_CONTAINER):
    DIALOG_STATE = 'STATE_overlay_hangar_general'
    DIALOG_STATE_ON = 'STATE_overlay_hangar_general_on'
    DIALOG_STATE_OFF = 'STATE_overlay_hangar_general_off'
    HANGAR_PLACE_STATE = 'STATE_hangar_place'
    HANGAR_PLACE_STATE_TASKS = 'STATE_hangar_place_tasks'
    BATTLE_PASS_PLACE_STATE = 'STATE_hangar_place_battle_pass'
    BATTLE_PASS_PLACE_STATE_ON = 'STATE_hangar_place_battle_pass_on'
    BATTLE_PASS_PLACE_STATE_OFF = 'STATE_hangar_place_battle_pass_off'


BATTLE_PASS_TASKS_SOUND_SPACE = CommonSoundSpaceSettings(name=BATTLE_PASS_SOUND_SPACE, entranceStates={BattlePassStates.HANGAR_PLACE_STATE: BattlePassStates.HANGAR_PLACE_STATE_TASKS,
 BattlePassStates.BATTLE_PASS_PLACE_STATE: BattlePassStates.BATTLE_PASS_PLACE_STATE_ON}, exitStates={BattlePassStates.BATTLE_PASS_PLACE_STATE: BattlePassStates.BATTLE_PASS_PLACE_STATE_OFF}, enterEvent='', exitEvent='', persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)
ACTIVATE_CHAPTER_SOUND_SPACE = CommonSoundSpaceSettings(name=BattlePassStates.DIALOG_STATE, entranceStates={BattlePassStates.DIALOG_STATE: BattlePassStates.DIALOG_STATE_ON}, exitStates={BattlePassStates.DIALOG_STATE: BattlePassStates.DIALOG_STATE_OFF}, enterEvent='', exitEvent='', persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True)

def switchBattlePassSoundFilter(on=True):
    WWISE.WW_setState(BattlePassStates.BATTLE_PASS_PLACE_STATE, BattlePassStates.BATTLE_PASS_PLACE_STATE_ON if on else BattlePassStates.BATTLE_PASS_PLACE_STATE_OFF)


def switchOverlaySoundFilter(on=True):
    WWISE.WW_setState(StatesGroup.OVERLAY_HANGAR_GENERAL, States.OVERLAY_HANGAR_GENERAL_ON if on else States.OVERLAY_HANGAR_GENERAL_OFF)


@replace_none_kwargs(battlePass=IBattlePassController)
def getBattlePassEnterSound(battlePass=None):
    return _getSound('tasks_{}_enter', battlePass.getSeasonNum(), BattlePassSounds.TASKS_ENTER) if not battlePass.isHoliday() else _getSound('tasks_holiday_{}_enter', battlePass.getSeasonNum(), BattlePassSounds.HOLIDAY_TASKS_ENTER)


@replace_none_kwargs(battlePass=IBattlePassController)
def getBattlePassExitSound(battlePass=None):
    return _getSound('tasks_{}_exit', battlePass.getSeasonNum(), BattlePassSounds.TASKS_EXIT) if not battlePass.isHoliday() else _getSound('tasks_holiday_{}_exit', battlePass.getSeasonNum(), BattlePassSounds.HOLIDAY_TASKS_EXIT)


def getBattlePassExtraEnterSound(chapterID):
    return _getSound('tasks_special_{}_enter', chapterID, BattlePassSounds.SPECIAL_TASKS_ENTER)


def getBattlePassExtraExitSound(chapterID):
    return _getSound('tasks_special_{}_exit', chapterID, BattlePassSounds.SPECIAL_TASKS_EXIT)


def _getSound(soundNameTemplate, soundID, defaultSound):
    soundName = soundNameTemplate.format(soundID)
    soundRes = R.sounds.dyn(soundName)
    if not soundRes.exists():
        _logger.debug('Sound: "%s" not found, using default: "%s"', soundName, defaultSound)
        soundRes = R.sounds.dyn(defaultSound)
        if not soundRes.exists():
            _logger.error('Sound: "%s" not found', defaultSound)
            return ''
    return backport.sound(soundRes())
