# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/halloween_gui_constants.py
from __future__ import absolute_import
from enum import IntEnum
from constants_utils import ConstInjector
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control.controllers.battle_hints.queues import BattleHintQueueParams
from gui.prb_control import settings
from gui.Scaleform.daapi.settings import views
from halloween_common.halloween_constants import QUEUE_TYPE, HALLOWEEN_CHAT_CHANNEL
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _FET, BATTLE_CTRL_ID as _BASE_CTRL_ID
from messenger.m_constants import LAZY_CHANNEL as CHANNEL

class PREBATTLE_ACTION_NAME(settings.PREBATTLE_ACTION_NAME, ConstInjector):
    _const_type = str
    HALLOWEEN = 'halloween'
    HALLOWEEN_SQUAD = 'halloween_squad'


class FUNCTIONAL_FLAG(settings.FUNCTIONAL_FLAG, ConstInjector):
    HALLOWEEN = 4294967296L


class SELECTOR_BATTLE_TYPES(settings.SELECTOR_BATTLE_TYPES, ConstInjector):
    _const_type = str
    HALLOWEEN = 'halloween'


class VIEW_ALIAS(views.VIEW_ALIAS, ConstInjector):
    _const_type = str
    HALLOWEEN_BATTLE_PAGE = 'HalloweenBattlePage'
    HW_OVERLAY_WEB_STORE = 'hwOverlayWebStore'
    HALLOWEEN_BATTLE_RESULTS = 'hwBattleResults'


class DifficultyLevel(IntEnum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class AmmoPanelSwitchPreset(object):
    PRESET_1 = 1
    PRESET_2 = 2
    ALL = [PRESET_1, PRESET_2]


QUEUE_TYPE_TO_DIFFICULTY_LEVEL = {QUEUE_TYPE.HALLOWEEN: DifficultyLevel.EASY,
 QUEUE_TYPE.HALLOWEEN_MEDIUM: DifficultyLevel.MEDIUM,
 QUEUE_TYPE.HALLOWEEN_HARD: DifficultyLevel.HARD}

class FEEDBACK_EVENT_ID(_FET, ConstInjector):
    HW_GAMEPLAY_ACTION = 101
    HW_VEHICLE_MARKER_HEALTH = 102


class SoulsCollectorMarkerStates(IntEnum):
    NOT_ENOUGHT_SOULS = 0
    MOVE_TO_SOULS_COLLECTOR = 1
    NOT_ENOUGHT_SOULS_CAMP_ACTIVE = 2
    MOVE_TO_SOULS_COLLECTOR_CAMP_ACTIVE = 3


class BATTLE_CTRL_ID(_BASE_CTRL_ID, ConstInjector):
    HW_BATTLE_GUI_CTRL = 101


HALLOWEEN_CAROUSEL_VEHICLE_TOOLTIP = 'halloweenCarouselVehicle'
HALLOWEEN_VEHICLE_FEATURE_TOOLTIP = 'halloweenVehicleFeatureTooltip'
HALLOWEEN_ABILITY_TOOLTIP = 'halloweenAbility'
HALLOWEEN_MAIN_SHELL = 'halloweenMainShell'
HALLOWEEN_TOOLTIP_SET = [HALLOWEEN_CAROUSEL_VEHICLE_TOOLTIP,
 HALLOWEEN_VEHICLE_FEATURE_TOOLTIP,
 HALLOWEEN_ABILITY_TOOLTIP,
 HALLOWEEN_MAIN_SHELL]

class LAZY_CHANNEL(CHANNEL, ConstInjector):
    _const_type = str
    HALLOWEEN_GLOBAL_CHANNEL = HALLOWEEN_CHAT_CHANNEL


HALLOWEEN_BATTLE_HINTS_QUEUE_ID = BattleHintQueueParams(name='halloween', withFadeOut=True)
HALLOWEEN_BATTLE_HINTS_SCOPE = 'halloween'
HALLOWEEN_BATTLE_HINTS_OVERLAP_VIEWS = {BATTLE_VIEW_ALIASES.UPGRADE_PANEL}

class HWDailyQuestsDecorations(object):
    ANOMALIES_ICON_KEY = 'anomalies'


HWDailyQuestDecorationMap = {13: HWDailyQuestsDecorations.ANOMALIES_ICON_KEY}
