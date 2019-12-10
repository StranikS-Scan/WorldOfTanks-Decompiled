# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/sounds.py
import WWISE
from shared_utils import CONST_CONTAINER
from items.components.ny_constants import ToySettings
from gui.sounds.filters import STATE_HANGAR_FILTERED
RANDOM_STYLE_BOX = 'random'

class NewYearSoundVars(CONST_CONTAINER):
    RTPC_PIANIST_DISTANCE = 'RTPC_ext_newyear_pianist_distance'
    RTPC_MUSIC_POSITION_CONTROL = 'RTPC_ext_newyear_music_position_control'
    RTPC_LEVEL_ATMOSPHERE = 'RTPC_ext_newyear_level_atmosphere'
    RTPC_LEVEL_TOYS = 'RTPC_ext_newyear_level_toys'
    RTPC_GIFT_AVAILABILITY = 'RTPC_ext_newyear_gift_availability'
    STATE_NEWYEAR_PLACE = 'STATE_ext_hangar_newyear_place'
    SWITCH_STYLES_BOX = 'SWITCH_ext_newyear_style_box'
    SWITCH_STYLES_TALISMAN = 'SWITCH_ext_newyear_style_talisman'


class NewYearStylesBoxSwitches(CONST_CONTAINER):
    TALE = 'SWITCH_ext_newyear_style_box_magic'
    MODERN = 'SWITCH_ext_newyear_style_box_europe'
    SOVIET = 'SWITCH_ext_newyear_style_box_soviet'
    CHINESE = 'SWITCH_ext_newyear_style_box_asian'
    RANDOM = 'SWITCH_ext_newyear_style_box_random'


class NewYearStylesTalismanSwitches(CONST_CONTAINER):
    TALE = 'SWITCH_ext_newyear_style_talisman_magic'
    MODERN = 'SWITCH_ext_newyear_style_talisman_europe'
    SOVIET = 'SWITCH_ext_newyear_style_talisman_soviet'
    CHINESE = 'SWITCH_ext_newyear_style_talisman_asian'


class NewYearSoundStates(CONST_CONTAINER):
    HANGAR = 'STATE_ext_hangar_newyear_place_hangar'
    REWARDS_LEVELS = 'STATE_ext_hangar_newyear_place_rewards_levels'
    REWARDS_COLLECTIONS = 'STATE_ext_hangar_newyear_place_rewards_collections'
    TOYS = 'STATE_ext_hangar_newyear_place_toys'
    DEBRIS = 'STATE_ext_hangar_newyear_place_debris'
    ALBUM_SELECT = 'STATE_ext_hangar_newyear_place_collections'
    INFO = 'STATE_ext_hangar_newyear_place_info'
    TREE = 'STATE_ext_hangar_newyear_place_glade_tree'
    KITCHEN = 'STATE_ext_hangar_newyear_place_glade_kitchen'
    SNOWTANK = 'STATE_ext_hangar_newyear_place_glade_snowtank'
    LIGHTE = 'STATE_ext_hangar_newyear_place_glade_light'
    TALISMAN = 'STATE_ext_hangar_newyear_place_glade_talisman'


class NewYearSoundEvents(CONST_CONTAINER):
    TREE = 'hangar_newyear_tree_enter'
    TREE_EXIT = 'hangar_newyear_tree_exit'
    KITCHEN = 'hangar_newyear_kitchen_enter'
    KITCHEN_EXIT = 'hangar_newyear_kitchen_exit'
    SNOWTANK = 'hangar_newyear_snowtank_enter'
    SNOWTANK_EXIT = 'hangar_newyear_snowtank_exit'
    LIGHTE = 'hangar_newyear_light_enter'
    LIGHTE_EXIT = 'hangar_newyear_light_exit'
    TALISMAN = 'hangar_newyear_talisman_enter'
    TALISMAN_EXIT = 'hangar_newyear_talisman_exit'
    TALISMAN_SELECTION = 'hangar_newyear_talisman_selection_enter'
    TALISMAN_SELECTION_EXIT = 'hangar_newyear_talisman_selection_exit'
    TALISMAN_GIFT = 'hangar_newyear_talisman_gift_enter'
    TALISMAN_GIFT_EXIT = 'hangar_newyear_talisman_gift_exit'
    TANKS_SCREEN = 'hangar_newyear_tanks_screen_enter'
    TANKS_SCREEN_EXIT = 'hangar_newyear_tanks_screen_exit'
    GLADE = 'hangar_newyear_glade_enter'
    GLADE_EXIT = 'hangar_newyear_glade_exit'
    DEBRIS = 'hangar_newyear_debris_enter'
    DEBRIS_EXIT = 'hangar_newyear_debris_exit'
    TOYS = 'hangar_newyear_toys_enter'
    TOYS_EXIT = 'hangar_newyear_toys_exit'
    ALBUM_CLICK = 'hangar_newyear_album_click'
    ALBUM_SELECT = 'hangar_newyear_album_select_enter'
    ALBUM_SELECT_EXIT = 'hangar_newyear_album_select_exit'
    ALBUM_SELECT_2018 = 'hangar_newyear_album_select_2018_enter'
    ALBUM_SELECT_2018_EXIT = 'hangar_newyear_album_select_2018_exit'
    ALBUM_SELECT_2019 = 'hangar_newyear_album_select_2019_enter'
    ALBUM_SELECT_2019_EXIT = 'hangar_newyear_album_select_2019_exit'
    ALBUM_SELECT_2020 = 'hangar_newyear_album_select_2020_enter'
    ALBUM_SELECT_2020_EXIT = 'hangar_newyear_album_select_2020_exit'
    REWARDS_LEVELS = 'hangar_newyear_rewards_atmosphere_enter'
    REWARDS_LEVELS_EXIT = 'hangar_newyear_rewards_atmosphere_exit'
    SANTA_CLAUS_SCREEN = 'hangar_newyear_santa_claus_screen_enter'
    SANTA_CLAUS_SCREEN_EXIT = 'hangar_newyear_santa_claus_screen_exit'
    AWARD_STYLE_SCREEN = 'hangar_newyear_award_style_screen_enter'
    AWARD_STYLE_SCREEN_EXIT = 'hangar_newyear_award_style_screen_exit'
    INFO = 'hangar_newyear_info_enter'
    INFO_EXIT = 'hangar_newyear_info_exit'
    ADD_TOY_TREE = 'hangar_newyear_add_toy_tree'
    ADD_TOY_TREE_DOWN = 'hangar_newyear_add_toy_tree_down'
    ADD_TOY_SNOWTANK = 'hangar_newyear_add_toy_snowtank'
    ADD_TOY_SNOWTANK_LIGHT = 'hangar_newyear_add_toy_snowtank_light'
    ADD_TOY_KITCHEN_TABLE = 'hangar_newyear_add_toy_kitchen_table'
    ADD_TOY_KITCHEN_BBQ = 'hangar_newyear_add_toy_kitchen_BBQ'
    ADD_TOY_LIGHT = 'hangar_newyear_add_toy_light'
    ADD_TOY_LIGHT_DOWN = 'hangar_newyear_add_toy_light_down'
    ADD_TOY_MEGA = 'hangar_newyear_add_toy_mega'
    TRANSITION_TREE = 'hangar_newyear_transition_tree'
    TRANSITION_SNOWTANK = 'hangar_newyear_transition_snowtank'
    TRANSITION_KITCHEN = 'hangar_newyear_transition_kitchen'
    TRANSITION_LIGHT = 'hangar_newyear_transition_light'
    TRANSITION_TALISMAN = 'hangar_newyear_transition_talisman'
    ENTER_CUSTOME = 'hangar_newyear_enter_custome'
    CHOICE_TOYS = 'hangar_newyear_choice_toys'
    COST_TOYS_UP = 'hangar_newyear_cost_toys_up'
    COST_TOYS_DOWN = 'hangar_newyear_cost_toys_down'
    COST_TOYS_NOT_CHANGE = 'hangar_newyear_cost_toys_not_change'
    LEVEL_UP = 'hangar_newyear_up_atmo'
    CHARGE_APPLY = 'hangar_newyear_charge_apply'
    TALISMAN_ACTIVATE = 'hangar_newyear_talisman_activate'
    TALISMAN_SET = 'hangar_newyear_talisman_set'
    TALISMAN_HOVER_ON = 'hangar_newyear_talisman_hover_on'
    TALISMAN_HOVER_OFF = 'hangar_newyear_talisman_hover_off'
    TALISMAN_ZOOM_IN = 'hangar_newyear_talisman_zoom_in'
    TALISMAN_ZOOM_OUT = 'hangar_newyear_talisman_zoom_out'
    TALISMAN_RECEIVING_GIFT = 'hangar_newyear_talisman_receiving_gift'
    TANKS_SET = 'hangar_newyear_tanks_set'
    ALBUM_ITEM_STOP = 'hangar_newyear_album_item_stop'


class NewYearSoundConfigKeys(CONST_CONTAINER):
    ENTRANCE_EVENT = 'entranceEvent'
    EXIT_EVENT = 'exitEvent'
    STATE_VALUE = 'stateValue'


_STYLES_BOX_SWITCHES_MAP = {ToySettings.NEW_YEAR: NewYearStylesBoxSwitches.SOVIET,
 ToySettings.CHRISTMAS: NewYearStylesBoxSwitches.MODERN,
 ToySettings.FAIRYTALE: NewYearStylesBoxSwitches.TALE,
 ToySettings.ORIENTAL: NewYearStylesBoxSwitches.CHINESE,
 ToySettings.SOVIET: NewYearStylesBoxSwitches.SOVIET,
 ToySettings.MODERN_WESTERN: NewYearStylesBoxSwitches.MODERN,
 ToySettings.TRADITIONAL_WESTERN: NewYearStylesBoxSwitches.TALE,
 ToySettings.ASIAN: NewYearStylesBoxSwitches.CHINESE,
 RANDOM_STYLE_BOX: NewYearStylesBoxSwitches.RANDOM}
_STYLES_TALISMAN_SWITCHES_MAP = {ToySettings.FAIRYTALE: NewYearStylesTalismanSwitches.TALE,
 ToySettings.CHRISTMAS: NewYearStylesTalismanSwitches.MODERN,
 ToySettings.NEW_YEAR: NewYearStylesTalismanSwitches.SOVIET,
 ToySettings.ORIENTAL: NewYearStylesTalismanSwitches.CHINESE}

class NewYearSoundsManager(object):

    def __init__(self, viewSoundConfig):
        self.__soundsConfig = viewSoundConfig

    def onEnterView(self):
        self.__playEvent(NewYearSoundConfigKeys.ENTRANCE_EVENT)
        self.setEnterViewState()

    def onExitView(self):
        self.__playEvent(NewYearSoundConfigKeys.EXIT_EVENT)

    def clear(self):
        self.__soundsConfig = {}

    def setEnterViewState(self):
        stateValue = self.__getValueByKey(NewYearSoundConfigKeys.STATE_VALUE)
        if stateValue:
            WWISE.WW_setState(NewYearSoundVars.STATE_NEWYEAR_PLACE, stateValue)

    @staticmethod
    def playEvent(eventName):
        WWISE.WW_eventGlobal(eventName)

    @staticmethod
    def setRTPC(name, value):
        WWISE.WW_setRTCPGlobal(name, value)

    @staticmethod
    def setStylesSwitchBox(toySetting):
        switchValue = _STYLES_BOX_SWITCHES_MAP.get(toySetting)
        if switchValue is not None:
            WWISE.WW_setSwitch(NewYearSoundVars.SWITCH_STYLES_BOX, switchValue)
        return

    @staticmethod
    def setStylesTalismanSwitchBox(talismanType):
        switchValue = _STYLES_TALISMAN_SWITCHES_MAP.get(talismanType)
        if switchValue is not None:
            WWISE.WW_setSwitch(NewYearSoundVars.SWITCH_STYLES_TALISMAN, switchValue)
        return

    @staticmethod
    def setHangarFilteredState(on):
        state = 'on' if on else 'off'
        WWISE.WW_setState(STATE_HANGAR_FILTERED, '{}_{}'.format(STATE_HANGAR_FILTERED, state))

    def __playEvent(self, eventKey):
        eventName = self.__getValueByKey(eventKey)
        if eventName:
            WWISE.WW_eventGlobal(eventName)

    def __getValueByKey(self, keyName):
        value = self.__soundsConfig.get(keyName)
        return value() if callable(value) else value
