# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/sounds.py
import WWISE
from shared_utils import CONST_CONTAINER
from items.components.ny_constants import ToySettings
RANDOM_STYLE_BOX = 'random'

class NewYearSoundVars(CONST_CONTAINER):
    RTPC_LEVEL_ATMOSPHERE = 'RTPC_ext_ev_newyear_2019_level_atmosphere'
    RTPC_LEVEL_TOYS = 'RTPC_ext_ev_newyear_2019_level_toys'
    STATE_NEWYEAR_2019 = 'hangar_h21_newyear_2019'
    STATE_STYLES = 'STATE_ext_newyear2019_style'
    SWITCH_STYLES_BOX = 'SWITCH_ext_newyear2019_style_box'


class NewYearStylesStates(CONST_CONTAINER):
    TALE = 'STATE_ext_newyear2019_style_tale'
    MODERN = 'STATE_ext_newyear2019_style_modern'
    SOVIET = 'STATE_ext_newyear2019_style_soviet'
    CHINESE = 'STATE_ext_newyear2019_style_chinese'


class NewYearStylesBoxSwitches(CONST_CONTAINER):
    TALE = 'SWITCH_ext_newyear2019_style_box_tale'
    MODERN = 'SWITCH_ext_newyear2019_style_box_modern'
    SOVIET = 'SWITCH_ext_newyear2019_style_box_soviet'
    CHINESE = 'SWITCH_ext_newyear2019_style_box_chinese'
    RANDOM = 'SWITCH_ext_newyear2019_style_box_random'


class NewYearSoundStates(CONST_CONTAINER):
    HANGAR = 'STATE_newyear_2019_hangar'
    TREE = 'STATE_newyear_2019_tree'
    KITCHEN = 'STATE_newyear_2019_kitchen'
    SNOWTANK = 'STATE_newyear_2019_snowtank'
    LIGHTE = 'STATE_newyear_2019_lighte'
    DEBRIS = 'STATE_newyear_2019_debris'
    TOYS = 'STATE_newyear_2019_toys'
    HERO = 'STATE_newyear_2019_rewards_herotank'
    ALBUM_SELECT = 'STATE_newyear_2019_album_select'
    ALBUM_SELECT_2018 = 'STATE_newyear_2019_album_select_2018'
    ALBUM_SELECT_2019 = 'STATE_newyear_2019_album_select_2019'
    REWARDS_ATMOSPHERE = 'STATE_newyear_2019_rewards_atmosphere'


class NewYearSoundEvents(CONST_CONTAINER):
    MAIN = 'hangar_h21_newyear_2019_main'
    MAIN_EXIT = 'hangar_h21_newyear_2019_main_exit'
    TREE = 'hangar_h21_newyear_2019_tree'
    TREE_EXIT = 'hangar_h21_newyear_2019_tree_exit'
    KITCHEN = 'hangar_h21_newyear_2019_kitchen'
    KITCHEN_EXIT = 'hangar_h21_newyear_2019_kitchen_exit'
    SNOWTANK = 'hangar_h21_newyear_2019_snowtank'
    SNOWTANK_EXIT = 'hangar_h21_newyear_2019_snowtank_exit'
    LIGHTE = 'hangar_h21_newyear_2019_lighte'
    LIGHTE_EXIT = 'hangar_h21_newyear_2019_lighte_exit'
    DEBRIS = 'hangar_h21_newyear_2019_debris'
    DEBRIS_EXIT = 'hangar_h21_newyear_2019_debris_exit'
    TOYS = 'hangar_h21_newyear_2019_toys'
    TOYS_EXIT = 'hangar_h21_newyear_2019_toys_exit'
    ALBUM_SELECT = 'hangar_h21_newyear_2019_album_select'
    ALBUM_SELECT_EXIT = 'hangar_h21_newyear_2019_album_select_exit'
    ALBUM_SELECT_2018 = 'hangar_h21_newyear_2019_album_select_2018'
    ALBUM_SELECT_2018_EXIT = 'hangar_h21_newyear_2019_album_select_2018_exit'
    ALBUM_SELECT_2019 = 'hangar_h21_newyear_2019_album_select_2019'
    ALBUM_SELECT_2019_EXIT = 'hangar_h21_newyear_2019_album_select_2019_exit'
    REWARDS_ATMOSPHERE = 'hangar_h21_newyear_2019_rewards_atmosphere'
    REWARDS_ATMOSPHERE_2019_EXIT = 'hangar_h21_newyear_2019_rewards_atmosphere_2019_exit'
    HERO = 'hangar_h21_newyear_2019_herotank'
    HERO_EXIT = 'hangar_h21_newyear_2019_herotank_exit'
    ADD_TOY_TREE = 'hangar_h21_newyear_2019_add_toy_tree'
    ADD_TOY_TREE_DOWN = 'hangar_h21_newyear_2019_add_toy_tree_down'
    ADD_TOY_SNOWTANK = 'hangar_h21_newyear_2019_add_toy_snowtank'
    ADD_TOY_SNOWTANK_LIGHT = 'hangar_h21_newyear_2019_add_toy_snowtank_light'
    ADD_TOY_KITCHEN_TABLE = 'hangar_h21_newyear_2019_add_toy_kitchen_table'
    ADD_TOY_KITCHEN_BBQ = 'hangar_h21_newyear_2019_add_toy_kitchen_BBQ'
    ADD_TOY_LIGHT = 'hangar_h21_newyear_2019_add_toy_light'
    ADD_TOY_LIGHT_DOWN = 'hangar_h21_newyear_2019_add_toy_light_down'
    TRANSITION_TREE = 'hangar_h21_newyear_2019_transition_tree'
    TRANSITION_SNOWTANK = 'hangar_h21_newyear_2019_transition_snowtank'
    TRANSITION_KITCHEN = 'hangar_h21_newyear_2019_transition_kitchen'
    TRANSITION_LIGHT = 'hangar_h21_newyear_2019_transition_light'
    ENTER_CUSTOME = 'hangar_h21_newyear_2019_enter_custome'
    CHOICE_TOYS = 'hangar_h21_newyear_2019_choice_toys'
    CHOICE_TOYS_STYLE = 'hangar_h21_newyear_2019_choice_toys_style'
    CHOICE_TOYS_SCREEN = 'hangar_h21_newyear_2019_choice_toys_screen'
    COST_TOYS_UP = 'hangar_h21_newyear_2019_cost_toys_up'
    COST_TOYS_DOWN = 'hangar_h21_newyear_2019_cost_toys_down'
    COST_TOYS_NOT_CHANGE = 'hangar_h21_newyear_2019_cost_toys_not_change'
    PIECES_TOYS_ENTER = 'hangar_h21_newyear_2019_pieces_toys_enter'
    MAKE_TOYS = 'hangar_h21_newyear_2019_make_toys'
    MAKE_TOYS_DOWN = 'hangar_h21_newyear_2019_make_toys_down'
    PIECES_TOYS_FX = 'hangar_h21_newyear_2019_pieces_toys_FX'
    ALBUM_CHOICE = 'hangar_h21_newyear_2019_album_choice'
    LEVEL_UP = 'hangar_h21_newyear_2019_up_atmo'


class NewYearSoundConfigKeys(CONST_CONTAINER):
    ENTRANCE_EVENT = 'entranceEvent'
    EXIT_EVENT = 'exitEvent'
    STATE_VALUE = 'stateValue'


_STYLES_STATES_MAP = {ToySettings.NEW_YEAR: NewYearStylesStates.SOVIET,
 ToySettings.CHRISTMAS: NewYearStylesStates.MODERN,
 ToySettings.FAIRYTALE: NewYearStylesStates.TALE,
 ToySettings.ORIENTAL: NewYearStylesStates.CHINESE}
_STYLES_SWITCHES_MAP = {ToySettings.NEW_YEAR: NewYearStylesBoxSwitches.SOVIET,
 ToySettings.CHRISTMAS: NewYearStylesBoxSwitches.MODERN,
 ToySettings.FAIRYTALE: NewYearStylesBoxSwitches.TALE,
 ToySettings.ORIENTAL: NewYearStylesBoxSwitches.CHINESE,
 ToySettings.SOVIET: NewYearStylesBoxSwitches.SOVIET,
 ToySettings.MODERN_WESTERN: NewYearStylesBoxSwitches.MODERN,
 ToySettings.TRADITIONAL_WESTERN: NewYearStylesBoxSwitches.TALE,
 ToySettings.ASIAN: NewYearStylesBoxSwitches.CHINESE,
 RANDOM_STYLE_BOX: NewYearStylesBoxSwitches.RANDOM}

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
            WWISE.WW_setState(NewYearSoundVars.STATE_NEWYEAR_2019, stateValue)

    @staticmethod
    def playEvent(eventName):
        WWISE.WW_eventGlobal(eventName)

    @staticmethod
    def setRTPC(name, value):
        WWISE.WW_setRTCPGlobal(name, value)

    @staticmethod
    def setStylesState(toySetting):
        stateValue = _STYLES_STATES_MAP.get(toySetting)
        if stateValue is not None:
            WWISE.WW_setState(NewYearSoundVars.STATE_STYLES, stateValue)
        return

    @staticmethod
    def setStylesSwitchBox(toySetting):
        switchValue = _STYLES_SWITCHES_MAP.get(toySetting)
        if switchValue is not None:
            WWISE.WW_setSwitch(NewYearSoundVars.SWITCH_STYLES_BOX, switchValue)
        return

    def __playEvent(self, eventKey):
        eventName = self.__getValueByKey(eventKey)
        if eventName:
            WWISE.WW_eventGlobal(eventName)

    def __getValueByKey(self, keyName):
        value = self.__soundsConfig.get(keyName)
        return value() if callable(value) else value
