# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/sounds.py
import WWISE
from gui.shared.gui_items.loot_box import NewYearLootBoxes
from shared_utils import CONST_CONTAINER
from items.components.ny_constants import ToySettings
from gui.sounds.filters import StatesGroup, States
from sound_gui_manager import CommonSoundSpaceSettings
RANDOM_STYLE_BOX = 'random'

class NewYearSoundVars(CONST_CONTAINER):
    RTPC_JUKEBOX_DISTANCE = 'RTPC_ext_newyear_music_distance'
    RTPC_MUSIC_POSITION_CONTROL = 'RTPC_ext_newyear_music_position_control'
    RTPC_LEVEL_ATMOSPHERE = 'RTPC_ext_newyear_level_atmosphere'
    RTPC_LEVEL_TOYS = 'RTPC_ext_newyear_level_toys'
    RTPC_GIFT_AVAILABILITY = 'RTPC_ext_newyear_gift_availability'
    STATE_NEWYEAR_PLACE = 'STATE_ext_hangar_newyear_place'
    SWITCH_STYLES_BOX = 'SWITCH_ext_newyear_style_box'
    SWITCH_STYLES_TALISMAN = 'SWITCH_ext_newyear_style_talisman'
    RTPC_LOOTBOX_ENTRY_VIEW = 'RTPC_ext_newyear_lootbox_camera'
    RTPC_LOOTBOX_AVAILABILITY = 'RTPC_ext_newyear_lootbox_availability'


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
    FAIR = 'STATE_ext_hangar_newyear_place_glade_kitchen'
    SNOWTANK = 'STATE_ext_hangar_newyear_place_glade_snowtank'
    MEGAZONE = 'STATE_ext_hangar_newyear_place_glade_light'
    CELEBRITY = 'STATE_ext_hangar_newyear_place_celeb'
    VEHICLES = 'STATE_ext_hangar_newyear_place_tanks'
    GIFT_SYSTEM = 'STATE_ext_hangar_newyear_place_gift_system'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_GARAGE = 'STATE_hangar_place_garage'


class NewYearSoundEvents(CONST_CONTAINER):
    TAB_BAR_CLICK = 'hangar_newyear_hud_upper_click'
    SIDE_BAR_CLICK = 'hangar_newyear_hud_side_click'
    TREE = 'hangar_newyear_tree_enter'
    TREE_EXIT = 'hangar_newyear_tree_exit'
    FAIR = 'hangar_newyear_kitchen_enter'
    FAIR_EXIT = 'hangar_newyear_kitchen_exit'
    SNOWTANK = 'hangar_newyear_snowtank_enter'
    SNOWTANK_EXIT = 'hangar_newyear_snowtank_exit'
    MEGAZONE = 'hangar_newyear_light_enter'
    MEGAZONE_EXIT = 'hangar_newyear_light_exit'
    TANKS_SCREEN = 'hangar_newyear_tanks_screen_enter'
    TANKS_SCREEN_EXIT = 'hangar_newyear_tanks_screen_exit'
    GLADE = 'hangar_newyear_glade_enter'
    GLADE_EXIT = 'hangar_newyear_glade_exit'
    DEBRIS = 'hangar_newyear_debris_enter'
    DEBRIS_EXIT = 'hangar_newyear_debris_exit'
    TOYS = 'hangar_newyear_toys_enter'
    TOYS_EXIT = 'hangar_newyear_toys_exit'
    ALBUM_SELECT = 'hangar_newyear_album_select_enter'
    ALBUM_SELECT_EXIT = 'hangar_newyear_album_select_exit'
    ALBUM_SELECT_2018 = 'hangar_newyear_album_select_2018_enter'
    ALBUM_SELECT_2018_EXIT = 'hangar_newyear_album_select_2018_exit'
    ALBUM_SELECT_2019 = 'hangar_newyear_album_select_2019_enter'
    ALBUM_SELECT_2019_EXIT = 'hangar_newyear_album_select_2019_exit'
    ALBUM_SELECT_2020 = 'hangar_newyear_album_select_2020_enter'
    ALBUM_SELECT_2020_EXIT = 'hangar_newyear_album_select_2020_exit'
    ALBUM_SELECT_2021 = 'hangar_newyear_album_select_2021_enter'
    ALBUM_SELECT_2021_EXIT = 'hangar_newyear_album_select_2021_exit'
    ALBUM_SELECT_2022 = 'hangar_newyear_album_select_2022_enter'
    ALBUM_SELECT_2022_EXIT = 'hangar_newyear_album_select_2022_exit'
    REWARDS_LEVELS = 'hangar_newyear_rewards_atmosphere_enter'
    REWARDS_LEVELS_EXIT = 'hangar_newyear_rewards_atmosphere_exit'
    SANTA_CLAUS_SCREEN = 'hangar_newyear_santa_claus_screen_enter'
    SANTA_CLAUS_SCREEN_EXIT = 'hangar_newyear_santa_claus_screen_exit'
    AWARD_STYLE_SCREEN = 'hangar_newyear_award_style_screen_enter'
    AWARD_STYLE_SCREEN_EXIT = 'hangar_newyear_award_style_screen_exit'
    INFO = 'hangar_newyear_info_enter'
    INFO_EXIT = 'hangar_newyear_info_exit'
    CUSTOMIZATION_SLOT_CLICK = 'highlight_red_butt'
    ADD_TOY_TREE = 'hangar_newyear_add_toy_tree'
    ADD_TOY_TREE_DOWN = 'hangar_newyear_add_toy_tree_down'
    ADD_TOY_SNOWTANK = 'hangar_newyear_add_toy_snowtank'
    ADD_TOY_SNOWTANK_LIGHT = 'hangar_newyear_add_toy_snowtank_light'
    ADD_TOY_KITCHEN_TABLE = 'hangar_newyear_add_toy_kitchen_table'
    ADD_TOY_KITCHEN_BBQ = 'hangar_newyear_add_toy_kitchen_BBQ'
    ADD_TOY_KITCHEN_ATTRACTION = 'hangar_newyear_add_toy_kitchen_attraction'
    ADD_TOY_BIG_GARLANDS = 'hangar_newyear_add_toy_kitchen_decor'
    ADD_TOY_LIGHT = 'hangar_newyear_add_toy_light'
    ADD_TOY_LIGHT_DOWN = 'hangar_newyear_add_toy_light_down'
    ADD_TOY_MEGA = 'hangar_newyear_add_toy_mega'
    TRANSITION_TREE = 'hangar_newyear_transition_tree'
    TRANSITION_INSTALLATION = 'hangar_newyear_transition_snowtank'
    TRANSITION_MEGAZONE = 'hangar_newyear_transition_light'
    TRANSITION_FAIR = 'hangar_newyear_transition_kitchen'
    TRANSITION_TALISMAN = 'hangar_newyear_transition_talisman'
    TRANSITION_CELEBRITY = 'hangar_newyear_transition_celeb'
    ENTER_CUSTOME = 'hangar_newyear_enter_custome'
    COST_TOYS_UP = 'hangar_newyear_cost_toys_up'
    COST_TOYS_DOWN = 'hangar_newyear_cost_toys_down'
    COST_TOYS_NOT_CHANGE = 'hangar_newyear_cost_toys_not_change'
    CRAFT_CHANGE_TOYS_SETTING = 'hangar_newyear_choice_toys'
    CRAFT_CHANGE_TOY_TYPE = 'hangar_newyear_choice_toys_style'
    CRAFT_MEGA_MODULE_ON = 'hangar_newyear_mega_module_on'
    CRAFT_MEGA_MODULE_OFF = 'hangar_newyear_mega_module_off'
    CRAFT_MEGA_STARTED = 'hangar_newyear_make_mega_toys'
    LEVEL_UP = 'hangar_newyear_up_atmo'
    TANKS_SET = 'hangar_newyear_tanks_set'
    ALBUM_ITEM_STOP = 'hangar_newyear_album_item_stop'
    CELEBRITY = 'hangar_newyear_celeb_enter'
    CELEBRITY_EXIT = 'hangar_newyear_celeb_exit'
    CELEBRITY_INTRO = 'hangar_newyear_celeb_screen_enter'
    CELEBRITY_INTRO_EXIT = 'hangar_newyear_celeb_screen_exit'
    CELEBRITY_SCREEN_REWARD = 'hangar_newyear_celeb_screen_reward'
    CELEBRITY_CARD_CLICK = 'hangar_newyear_celeb_screen_card_select'
    CRAFT_MONITOR_PRINING_START = 'hangar_newyear_toys_print_text_start'
    CRAFT_MONITOR_PRINTING_STOP = 'hangar_newyear_toys_print_text_stop'
    GIFT_SYSTEM = 'hangar_newyear_gift_system_enter'
    GIFT_SYSTEM_EXIT = 'hangar_newyear_gift_system_exit'


class NewYearSoundConfigKeys(CONST_CONTAINER):
    ENTRANCE_EVENT = 'entranceEvent'
    EXIT_EVENT = 'exitEvent'
    STATE_VALUE = 'stateValue'


NY_MAIN_VIEW_SOUND_SPACE = CommonSoundSpaceSettings(name='new_year_main_view', entranceStates={StatesGroup.HANGAR_PLACE: States.HANGAR_PLACE_GARAGE,
 StatesGroup.HANGAR_FILTERED: States.HANGAR_FILTERED_OFF}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
_STYLES_BOX_SWITCHES_MAP = {ToySettings.NEW_YEAR: NewYearStylesBoxSwitches.SOVIET,
 ToySettings.CHRISTMAS: NewYearStylesBoxSwitches.MODERN,
 ToySettings.FAIRYTALE: NewYearStylesBoxSwitches.TALE,
 ToySettings.ORIENTAL: NewYearStylesBoxSwitches.CHINESE,
 ToySettings.SOVIET: NewYearStylesBoxSwitches.SOVIET,
 ToySettings.MODERN_WESTERN: NewYearStylesBoxSwitches.MODERN,
 ToySettings.TRADITIONAL_WESTERN: NewYearStylesBoxSwitches.TALE,
 ToySettings.ASIAN: NewYearStylesBoxSwitches.CHINESE,
 ToySettings.MEGA_TOYS: NewYearStylesBoxSwitches.RANDOM,
 RANDOM_STYLE_BOX: NewYearStylesBoxSwitches.RANDOM}
_STYLES_TALISMAN_SWITCHES_MAP = {ToySettings.FAIRYTALE: NewYearStylesTalismanSwitches.TALE,
 ToySettings.CHRISTMAS: NewYearStylesTalismanSwitches.MODERN,
 ToySettings.NEW_YEAR: NewYearStylesTalismanSwitches.SOVIET,
 ToySettings.ORIENTAL: NewYearStylesTalismanSwitches.CHINESE}
_ENTRY_VIEW_RTPC_VALUES = {NewYearLootBoxes.PREMIUM: 100}
_HAS_BOX_RTPC_VALUE = 100

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

    @classmethod
    def setRTPCBoxEntryView(cls, boxType):
        cls.setRTPC(NewYearSoundVars.RTPC_LOOTBOX_ENTRY_VIEW, _ENTRY_VIEW_RTPC_VALUES.get(boxType, 0))

    @classmethod
    def setRTPCBoxAvailability(cls, hasBox):
        cls.setRTPC(NewYearSoundVars.RTPC_LOOTBOX_AVAILABILITY, _HAS_BOX_RTPC_VALUE if hasBox else 0)

    @staticmethod
    def setStylesTalismanSwitchBox(talismanType):
        switchValue = _STYLES_TALISMAN_SWITCHES_MAP.get(talismanType)
        if switchValue is not None:
            WWISE.WW_setSwitch(NewYearSoundVars.SWITCH_STYLES_TALISMAN, switchValue)
        return

    @staticmethod
    def setHangarFilteredState(on):
        state = States.HANGAR_FILTERED_ON if on else States.HANGAR_FILTERED_OFF
        WWISE.WW_setState(StatesGroup.HANGAR_FILTERED, state)

    @staticmethod
    def setHangarPlaceGarage():
        WWISE.WW_setState(NewYearSoundStates.STATE_PLACE, NewYearSoundStates.STATE_PLACE_GARAGE)

    def __playEvent(self, eventKey):
        eventName = self.__getValueByKey(eventKey)
        if eventName:
            WWISE.WW_eventGlobal(eventName)

    def __getValueByKey(self, keyName):
        value = self.__soundsConfig.get(keyName)
        return value() if callable(value) else value
