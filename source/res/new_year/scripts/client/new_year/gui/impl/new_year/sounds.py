# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/new_year/sounds.py
import SoundGroups
import WWISE
from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager, SoundManagerStates
from new_year.ny_constants import NewYearLootBoxes, NewYearLootBoxRewards
from shared_utils import CONST_CONTAINER
from new_year_common.items.components.ny_constants import ToySettings
from gui.sounds.filters import StatesGroup, States
from sound_gui_manager import CommonSoundSpaceSettings
from items.vehicles import getItemByCompactDescr
from shared_utils import first
RANDOM_STYLE_BOX = 'random'
GLADE_PREFIX = 'GLADE_'

class NewYearSoundVars(CONST_CONTAINER):
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
    REWARDS_COLLECTIONS = 'STATE_ext_hangar_newyear_place_rewards_collections'
    DEBRIS = 'STATE_ext_hangar_newyear_place_debris'
    ALBUM_SELECT = 'STATE_ext_hangar_newyear_place_collections'
    GLADE_FIR = 'STATE_ext_hangar_newyear_place_glade_tree'
    GLADE_SKATING = 'STATE_ext_hangar_newyear_place_glade_rink'
    GLADE_LIGHTS = 'STATE_ext_hangar_newyear_place_glade_light'
    GLADE_ATTRACTIONS = 'STATE_ext_hangar_newyear_place_glade_attraction'
    GLADE_FAIR = 'STATE_ext_hangar_newyear_place_glade_kitchen'
    GLADE_INSTALLATIONS = 'STATE_ext_hangar_newyear_place_glade_snowtank'
    CITY = 'STATE_ext_hangar_newyear_place_city'
    QUEST = 'STATE_ext_hangar_newyear_place_quest'
    TOYS = 'STATE_ext_hangar_newyear_place_toys'
    REWARDS_LEVELS = 'STATE_ext_hangar_newyear_place_rewards_levels'
    INFO = 'STATE_ext_hangar_newyear_place_info'
    CELEB = 'STATE_ext_hangar_newyear_place_celeb'
    VEHICLES = 'STATE_ext_hangar_newyear_place_tanks'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_GARAGE = 'STATE_hangar_place_garage'


class NewYearSoundEvents(CONST_CONTAINER):
    HANGAR = 'hangar_newyear_place_hangar_enter'
    HANGAR_EXIT = 'hangar_newyear_place_hangar_exit'
    SIDE_BAR_CLICK = 'hangar_newyear_hud_side_click'
    TREE = 'hangar_newyear_tree_enter'
    TREE_EXIT = 'hangar_newyear_tree_exit'
    TANKS_SCREEN = 'hangar_newyear_tanks_screen_enter'
    TANKS_SCREEN_EXIT = 'hangar_newyear_tanks_screen_exit'
    GLADE = 'hangar_newyear_glade_enter'
    GLADE_EXIT = 'hangar_newyear_glade_exit'
    DEBRIS = 'hangar_newyear_debris_enter'
    DEBRIS_EXIT = 'hangar_newyear_debris_exit'
    TOYS = 'hangar_newyear_toys_enter'
    TOYS_EXIT = 'hangar_newyear_toys_exit'
    GLADE_FIR_ENTER = 'hangar_newyear_tree_enter'
    GLADE_FIR_EXIT = 'hangar_newyear_tree_exit'
    GLADE_SKATING_ENTER = 'hangar_newyear_rink_enter'
    GLADE_SKATING_EXIT = 'hangar_newyear_rink_exit'
    GLADE_LIGHTS_ENTER = 'hangar_newyear_illumination_enter'
    GLADE_LIGHTS_EXIT = 'hangar_newyear_illumination_exit'
    GLADE_ATTRACTIONS_ENTER = 'hangar_newyear_attraction_enter'
    GLADE_ATTRACTIONS_EXIT = 'hangar_newyear_attraction_exit'
    GLADE_FAIR_ENTER = 'hangar_newyear_fair_enter'
    GLADE_FAIR_EXIT = 'hangar_newyear_fair_exit'
    GLADE_INSTALLATIONS_ENTER = 'hangar_newyear_sculpture_enter'
    GLADE_INSTALLATIONS_EXIT = 'hangar_newyear_sculpture_exit'
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
    SANTA_CLAUS_SCREEN = 'hangar_newyear_santa_claus_screen_enter'
    SANTA_CLAUS_SCREEN_EXIT = 'hangar_newyear_santa_claus_screen_exit'
    AWARD_STYLE_SCREEN = 'hangar_newyear_award_style_screen_enter'
    AWARD_STYLE_SCREEN_EXIT = 'hangar_newyear_award_style_screen_exit'
    CITY = 'hangar_newyear_city_enter'
    CITY_EXIT = 'hangar_newyear_city_exit'
    QUESTS = 'hangar_newyear_quests_enter'
    QUESTS_EXIT = 'hangar_newyear_quests_exit'
    SURPRISE_MACHINE = 'hangar_newyear_machine_enter'
    SURPRISE_MACHINE_EXIT = 'hangar_newyear_machine_exit'
    REWARDS_LEVELS = 'hangar_newyear_rewards_atmosphere_enter'
    REWARDS_LEVELS_EXIT = 'hangar_newyear_rewards_atmosphere_exit'
    PET = 'hangar_newyear_pet_enter'
    PET_EXIT = 'hangar_newyear_pet_exit'
    INFO = 'hangar_newyear_info_enter'
    INFO_EXIT = 'hangar_newyear_info_exit'
    CUSTOMIZATION_SLOT_CLICK = 'highlight_red_butt'
    ADD_TOY_TREE = 'hangar_newyear_add_toy_tree'
    ADD_TOY_TREE_DOWN = 'hangar_newyear_add_toy_tree_down'
    ADD_TOY_ILLUMINATION = 'hangar_newyear_add_toy_illumination'
    ADD_TOY_ATTRACTION = 'hangar_newyear_add_toy_attraction'
    ADD_TOY_FAIR_SMALL = 'hangar_newyear_add_toy_fair_small'
    ADD_TOY_FAIR_BIG = 'hangar_newyear_add_toy_fair_big'
    ADD_TOY_INSTALLATIONS = 'hangar_newyear_add_toy_sculpture'
    ADD_TOY_SKATING = 'hangar_newyear_add_toy_rink'
    TRANSITION_TREE = 'hangar_newyear_transition_tree'
    TRANSITION_TALISMAN = 'hangar_newyear_transition_talisman'
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
    MACHINE_BTN_PRESS = 'hangar_newyear_machine_button_press'
    TANKS_SET = 'hangar_newyear_tanks_set'
    ALBUM_ITEM_STOP = 'hangar_newyear_album_item_stop'
    CRAFT_MONITOR_PRINING_START = 'hangar_newyear_toys_print_text_start'
    CRAFT_MONITOR_PRINTING_STOP = 'hangar_newyear_toys_print_text_stop'
    VIDEO_DONE = 'gui_lootbox_video_stop'
    VIDEO_PAUSE = 'gui_lootbox_video_pause'
    VIDEO_RESUME = 'gui_lootbox_video_resume'


class NewYearSoundConfigKeys(CONST_CONTAINER):
    ENTRANCE_EVENT = 'entranceEvent'
    EXIT_EVENT = 'exitEvent'
    STATE_VALUE = 'stateValue'


NY_MAIN_VIEW_SOUND_SPACE = CommonSoundSpaceSettings(name='new_year_main_view', entranceStates={StatesGroup.HANGAR_PLACE: States.HANGAR_PLACE_GARAGE,
 StatesGroup.HANGAR_FILTERED: States.HANGAR_FILTERED_OFF}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
NY_REWARD_VIDEO_SOUND_SPACE = CommonSoundSpaceSettings(name='new_year_video_reward', entranceStates={StatesGroup.VIDEO_OVERLAY: States.VIDEO_OVERLAY_ON}, exitStates={StatesGroup.VIDEO_OVERLAY: States.VIDEO_OVERLAY_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
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
_ENTRY_VIEW_RTPC_VALUES = {lType:100 for lType in NewYearLootBoxes.PREMIUM}
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

    @staticmethod
    def setGladeState(currentObject):
        stateName = getattr(NewYearSoundStates, GLADE_PREFIX + currentObject.upper())
        WWISE.WW_setState(NewYearSoundVars.STATE_NEWYEAR_PLACE, stateName)

    @staticmethod
    def playGladeEvent(objectName, eventType):
        eventName = getattr(NewYearSoundEvents, GLADE_PREFIX + objectName.upper() + eventType)
        WWISE.WW_eventGlobal(eventName)

    def __playEvent(self, eventKey):
        eventName = self.__getValueByKey(eventKey)
        if eventName:
            WWISE.WW_eventGlobal(eventName)

    def __getValueByKey(self, keyName):
        value = self.__soundsConfig.get(keyName)
        return value() if callable(value) else value


class VideoRewardsSoundControl(IVideoSoundManager):
    __slots__ = ('__bonusName', '__state')
    _SOUND_EVENT_TEMPLATE = 'gui_video_ny_lootbox_{}'

    def __init__(self, bonusName):
        self.__bonusName = bonusName
        self.__state = None
        return

    def setBonusName(self, bonusName):
        self.__bonusName = bonusName

    def start(self):
        if self.__bonusName.startswith('customizations'):
            styleDescr = getItemByCompactDescr(int(self.__bonusName.split('_')[1]))
            vehicleItem = getItemByCompactDescr(first(first(styleDescr.filter.include).vehicles))
            self.setBonusName(vehicleItem.name.split(':')[1])
        sound = self._SOUND_EVENT_TEMPLATE.format(NewYearLootBoxRewards.ALL.get(self.__bonusName, 'tank_default'))
        SoundGroups.g_instance.playSound2D(sound)
        self.__state = SoundManagerStates.PLAYING

    def stop(self):
        if self.__state != SoundManagerStates.STOPPED:
            SoundGroups.g_instance.playSound2D(NewYearSoundEvents.VIDEO_DONE)
            self.__state = SoundManagerStates.STOPPED

    def pause(self):
        SoundGroups.g_instance.playSound2D(NewYearSoundEvents.VIDEO_PAUSE)
        self.__state = SoundManagerStates.PAUSE

    def unpause(self):
        SoundGroups.g_instance.playSound2D(NewYearSoundEvents.VIDEO_RESUME)
        self.__state = SoundManagerStates.PLAYING
