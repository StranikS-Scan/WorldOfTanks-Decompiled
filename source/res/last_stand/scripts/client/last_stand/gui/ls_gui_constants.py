# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/ls_gui_constants.py
from enum import IntEnum
from constants_utils import ConstInjector
from gui.battle_control.controllers.battle_hints.queues import BattleHintQueueParams
from gui.prb_control import settings
from gui.Scaleform.daapi.settings import views
from last_stand_common.last_stand_constants import DifficultyLevelToken, QUEUE_TYPE, LS_CHAT_CHANNEL
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _FET, BATTLE_CTRL_ID as _BASE_CTRL_ID
from messenger.m_constants import LAZY_CHANNEL as CHANNEL

class PREBATTLE_ACTION_NAME(settings.PREBATTLE_ACTION_NAME, ConstInjector):
    _const_type = str
    LAST_STAND = 'last_stand'
    LAST_STAND_SQUAD = 'last_stand_squad'


class FUNCTIONAL_FLAG(settings.FUNCTIONAL_FLAG, ConstInjector):
    LAST_STAND = 17179869184L


class SELECTOR_BATTLE_TYPES(settings.SELECTOR_BATTLE_TYPES, ConstInjector):
    _const_type = str
    LAST_STAND = 'last_stand'


class VIEW_ALIAS(views.VIEW_ALIAS, ConstInjector):
    _const_type = str
    LAST_STAND_BATTLE_PAGE = 'LastStandBattlePage'
    LS_OVERLAY_WEB_STORE = 'lsOverlayWebStore'


class DifficultyLevel(IntEnum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class AmmoPanelSwitchPreset(object):
    PRESET_1 = 1
    PRESET_2 = 2
    ALL = [PRESET_1, PRESET_2]


QUEUE_TYPE_TO_DIFFICULTY_LEVEL = {QUEUE_TYPE.LAST_STAND: DifficultyLevel.EASY,
 QUEUE_TYPE.LAST_STAND_MEDIUM: DifficultyLevel.MEDIUM,
 QUEUE_TYPE.LAST_STAND_HARD: DifficultyLevel.HARD}
DIFFICULTY_TOKEN_TO_LEVEL = {DifficultyLevelToken.EASY: DifficultyLevel.EASY,
 DifficultyLevelToken.MEDIUM: DifficultyLevel.MEDIUM,
 DifficultyLevelToken.HARD: DifficultyLevel.HARD}
DIFFICULTY_LEVEL_TO_TOKEN = {DifficultyLevel.EASY: DifficultyLevelToken.EASY,
 DifficultyLevel.MEDIUM: DifficultyLevelToken.MEDIUM,
 DifficultyLevel.HARD: DifficultyLevelToken.HARD}

class FEEDBACK_EVENT_ID(_FET, ConstInjector):
    LS_GAMEPLAY_ACTION = 106
    LS_NO_HIT = 107


class BATTLE_CTRL_ID(_BASE_CTRL_ID, ConstInjector):
    LS_BATTLE_GUI_CTRL = 104


LS_RENT_VEHICLE_TOOLTIP = 'lsRentVehicle'
LS_CAROUSEL_VEHICLE_TOOLTIP = 'lsCarouselVehicle'
LS_ABILITY_TOOLTIP = 'lsAbility'
LS_MAIN_SHELL = 'lsMainShell'
LS_TOOLTIP_SET = [LS_RENT_VEHICLE_TOOLTIP,
 LS_ABILITY_TOOLTIP,
 LS_MAIN_SHELL,
 LS_CAROUSEL_VEHICLE_TOOLTIP]
LS_INFO_PAGE_KEY = 'infoPageLastStand'
LS_INTRO_VIDEO_KEY = 'lsIntroVideo'

class LAZY_CHANNEL(CHANNEL, ConstInjector):
    _const_type = str
    LAST_STAND_GLOBAL_CHANNEL = LS_CHAT_CHANNEL


LS_BATTLE_HINTS_QUEUE_ID = BattleHintQueueParams(name='last_stand', withFadeOut=True)
