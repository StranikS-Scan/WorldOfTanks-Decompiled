# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/white_tiger_gui_constants.py
from gui.Scaleform.daapi.settings import views
from constants_utils import ConstInjector
from gui.prb_control import settings
from gui.battle_control import battle_constants
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _FET
from white_tiger.gui.impl.gen.view_models.views.lobby.hangar_view_model import WhiteTigerVehicles
from white_tiger.gui.impl.gen.view_models.views.lobby.mode_selector.tooltips.mode_selector_tooltips_constants import ModeSelectorTooltipsConstants
from enum import Enum

class FUNCTIONAL_FLAG(settings.FUNCTIONAL_FLAG, ConstInjector):
    WHITE_TIGER = 8589934592L


class PREBATTLE_ACTION_NAME(settings.PREBATTLE_ACTION_NAME, ConstInjector):
    _const_type = str
    WHITE_TIGER = 'whiteTiger'
    WHITE_TIGER_SQUAD = 'whiteTigerSquad'


class SELECTOR_BATTLE_TYPES(settings.SELECTOR_BATTLE_TYPES, ConstInjector):
    _const_type = str
    WHITE_TIGER = 'whiteTiger'


class VIEW_ALIAS(views.VIEW_ALIAS, ConstInjector):
    _const_type = str
    WHITE_TIGER_BATTLE_PAGE = 'whiteTigerBattlePage'
    WHITE_TIGER_SETTINGS_WINDOW = 'whiteTigerSettingsWindow'


class BATTLE_CTRL_ID(battle_constants.BATTLE_CTRL_ID, ConstInjector):
    WT_BATTLE_GUI_CTRL = 103


class FEEDBACK_EVENT_ID(_FET, ConstInjector):
    WT_GAMEPLAY_ACTION = 103
    WT_VEHICLE_MARKER_HEALTH = 104
    WT_VEHICLE_DISCRETE_DAMAGE_RECEIVED = 105


class MINIMAP_CONTAINER_NAME(object):
    WT_DEPLOY = 'deploymentPoints'


WT_HANGAR_SELECTED_VEHICLE = {'germany:G98_Waffentrager_E100_TLXXL': WhiteTigerVehicles.BT110,
 'germany:G98_Waffentrager_E100_TLXXL_S': WhiteTigerVehicles.BT220,
 'usa:A120_M48A5_hound_TLXXL': WhiteTigerVehicles.THUNDERBOLT,
 'ussr:R97_Object_140_hound_TLXXL': WhiteTigerVehicles.RESISTOR,
 'france:F18_Bat_Chatillon25t_hound_TLXXL': WhiteTigerVehicles.FOUDRE,
 'czech:Cz04_T50_51_Waf_Hound_3DSt': WhiteTigerVehicles.POJISTKA}
OVERTIME_COMPONENT_NAME = 'overtimeComponent'
SOUND_REMAPPING_LABEL = 'white_tiger'

class VehicleCharacteristics(Enum):
    PROS = 'pros'
    CONS = 'cons'


WHITE_TIGER_BATTLES_TICKET = 'whiteTigerBattlesTicket'
WHITE_TIGER_STAMP = 'whiteTigerStamp'
WHITE_TIGER_BATTLES_SET = [WHITE_TIGER_BATTLES_TICKET, WHITE_TIGER_STAMP, ModeSelectorTooltipsConstants.WHITE_TIGER_BATTLES_CALENDAR_TOOLTIP]
WHITE_TIGER_EARNED_CURRENCY = 'whiteTigerEarnedCurrency'
WT_QUEST_PREFIX = 'wtevent'
WT_BATTLE_QUEST_PREFIX = 'wtevent:battle_quest'
WT_QUEST_BOSS_GROUP_ID = 'wt_group_boss'
WT_QUEST_HUNTER_GROUP_ID = 'wt_group_hunter'
MAX_VISIBLE_QUESTS = 3
HUNTER_QUEST_CHAINS = [WT_QUEST_HUNTER_GROUP_ID + '_1', WT_QUEST_HUNTER_GROUP_ID + '_2', WT_QUEST_HUNTER_GROUP_ID + '_3']
TICKET_ICON_FILE_NAME = 'wtevent_ticket'
PROGRESSION_COMPLETE_TOKEN = 'wtevent:completed_progress'
