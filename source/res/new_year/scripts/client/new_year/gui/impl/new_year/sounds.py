# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/new_year/sounds.py
import SoundGroups
from gui.impl.lobby.loot_box.loot_box_sounds import LootBoxVideoStartStopHandler
from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager, SoundManagerStates
from new_year.ny_constants import NewYearLootBoxes, NewYearLootBoxRewards
from shared_utils import CONST_CONTAINER
from new_year_common.items.components.ny_constants import ToySettings, MAX_ATMOSPHERE_LVL
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
    GLADE_SNOWSLIDE = 'STATE_ext_hangar_newyear_place_glade_rink'
    GLADE_TEREM = 'STATE_ext_hangar_newyear_place_terem'
    GLADE_FIREWORKS = 'STATE_ext_hangar_newyear_place_fireworks'
    GLADE_FAIR = 'STATE_ext_hangar_newyear_place_fair'
    GLADE_INSTALLATIONS = 'STATE_ext_hangar_newyear_place_sculpture'
    CITY = 'STATE_ext_hangar_newyear_place_city'
    LEADERS = 'STATE_ext_hangar_newyear_place_lider'
    SURPRISE_MACHINE = 'STATE_ext_hangar_newyear_place_machine'
    REWARDS_LEVELS = 'STATE_ext_hangar_newyear_place_rewards_levels'
    INFO = 'STATE_ext_hangar_newyear_place_info'
    PET = 'STATE_ext_hangar_newyear_place_pet'
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
    GLADE_FIR_ENTER = TREE
    GLADE_FIR_EXIT = TREE_EXIT
    GLADE_SNOWSLIDE_ENTER = 'hangar_newyear_rink_enter'
    GLADE_SNOWSLIDE_EXIT = 'hangar_newyear_rink_exit'
    GLADE_TEREM_ENTER = 'hangar_newyear_terem_enter'
    GLADE_TEREM_EXIT = 'hangar_newyear_terem_exit'
    GLADE_FIREWORKS_ENTER = 'hangar_newyear_fireworks_enter'
    GLADE_FIREWORKS_EXIT = 'hangar_newyear_fireworks_exit'
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
    LEADERS = 'hangar_newyear_lider_enter'
    LEADERS_EXIT = 'hangar_newyear_lider_exit'
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
    ADD_TOY_TEREM = 'hangar_newyear_add_toy_terem'
    ADD_TOY_FIREWORKS = 'hangar_newyear_add_toy_fireworks'
    ADD_TOY_FAIR_SMALL = 'hangar_newyear_add_toy_fair_small'
    ADD_TOY_FAIR_BIG = 'hangar_newyear_add_toy_fair_big'
    ADD_TOY_INSTALLATIONS = 'hangar_newyear_add_toy_sculpture'
    ADD_TOY_SNOWSLIDE = 'hangar_newyear_add_toy_rink'
    TRANSITION_TREE = 'hangar_newyear_transition_tree'
    TRANSITION_TALISMAN = 'hangar_newyear_transition_talisman'
    ENTER_CUSTOME = 'hangar_newyear_enter_custome'
    COST_TOYS_UP = 'hangar_newyear_cost_toys_up'
    COST_TOYS_DOWN = 'hangar_newyear_cost_toys_down'
    COST_TOYS_NOT_CHANGE = 'hangar_newyear_cost_toys_not_change'
    LEVEL_UP = 'hangar_newyear_up_atmo'
    MACHINE_BTN_PRESS = 'hangar_newyear_machine_button_press'
    MACHINE_CHOISE_BTN_PRESS = 'hangar_newyear_machine_button_press_choise'
    TANKS_SET = 'hangar_newyear_tanks_set'
    ALBUM_ITEM_STOP = 'hangar_newyear_album_item_stop'
    VIDEO_DONE = 'gui_lootbox_video_stop'
    VIDEO_PAUSE = 'gui_lootbox_video_pause'
    VIDEO_RESUME = 'gui_lootbox_video_resume'
    OLDMAN_NOTIFICATION_HUNGRY = 'ny_vo_lobby_terentiy_warning_raccoon_hungry'
    OLDMAN_NOTIFICATION_ENERGY = 'ny_vo_lobby_terentiy_warning_raccoon_energy'
    OLDMAN_NOTIFICATION_HYGIENE = 'ny_vo_lobby_terentiy_warning_raccoon_hygiene'
    OLDMAN_NOTIFICATION_GENERAL = 'ny_vo_lobby_terentiy_warning_raccoon_general_condition'
    OLDMAN_ONBOARDING_SKIP = 'ny_vo_terentiy_help_stop'


class NewYearSoundConfigKeys(CONST_CONTAINER):
    ENTRANCE_EVENT = 'entranceEvent'
    CLOSE_EVENT = 'closeEvent'
    STATE_VALUE = 'stateValue'


class EnvSwitcherAnimSounds(CONST_CONTAINER):
    GROUP = 'STATE_hangar_filtered'
    ON = 'STATE_hangar_filtered_on'
    OFF = 'STATE_hangar_filtered_off'
    DAY_CHOICE = 'hangar_newyear_day_choice'
    NIGHT_CHOICE = 'hangar_newyear_night_choice'


class EnvSwitcherSounds(CONST_CONTAINER):
    GROUP = 'STATE_ext_hangar_newyear_spaces'
    DAY = 'STATE_ext_hangar_newyear_day'
    NIGHT = 'STATE_ext_hangar_newyear_night'
    DAY_ENTER = 'hangar_newyear_day_enter'
    DAY_EXIT = 'hangar_newyear_day_exit'
    NIGHT_ENTER = 'hangar_newyear_night_enter'
    NIGHT_EXIT = 'hangar_newyear_night_exit'


class RaccoonStates(CONST_CONTAINER):
    GROUP = 'STATE_ext_hangar_newyear_enot_zone'
    MAIN = 'STATE_ext_hangar_newyear_enot_zone_main'
    CARDS = 'STATE_ext_hangar_newyear_enot_zone_cards'
    HISTORY = 'STATE_ext_hangar_newyear_enot_zone_history'
    ITEMS = 'STATE_ext_hangar_newyear_enot_zone_items'
    LETTER = 'STATE_ext_hangar_newyear_enot_zone_letter'
    SHOP = 'STATE_ext_hangar_newyear_enot_zone_shop'
    HISTORY_SOUND_SPACE = 'raccoon_history'
    PROGRESS_FILL_START = 'hangar_newyear_raccoon_progress_bar_start'
    PROGRESS_FILL_STOP = 'hangar_newyear_raccoon_progress_bar_stop'


RACCOON_HISTORY_SOUND_SPACE = CommonSoundSpaceSettings(name=RaccoonStates.HISTORY_SOUND_SPACE, entranceStates={RaccoonStates.GROUP: RaccoonStates.HISTORY}, exitStates={RaccoonStates.GROUP: RaccoonStates.MAIN}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')

class RaccoonMood(CONST_CONTAINER):
    GROUP = 'STATE_ext_hangar_newyear_pet_mood'
    FUN = 'STATE_ext_hangar_newyear_pet_mood_funny'
    NORMAL = 'STATE_ext_hangar_newyear_pet_mood_normal'
    SAD = 'STATE_ext_hangar_newyear_pet_mood_sad'


class NewYearCelebVoiceOvers(CONST_CONTAINER):
    NY_QUESTS_CELEB_MESSAGES_PREFIX = 'ny_gui_vo_quest_0{}'
    NY_QUESTS_CELEB_STOP_VOICEOVER = 'ny_gui_vo_quest_stop'
    FIRST_LEVEL_UP = 'ny_gui_vo_celeb_atmosphere_level_up'
    LAST_LEVEL_UP = 'ny_gui_vo_celeb_atmosphere_full'
    ENABLE_SOUND_RANGE = [1, MAX_ATMOSPHERE_LVL]
    LEVEL_UP_GROUP = 'STATE_ext_hangar_ny_level_up_window'
    LEVEL_UP_OPEN = 'STATE_ext_hangar_ny_level_up_window_open'
    LEVEL_UP_CLOSE = 'STATE_ext_hangar_ny_level_up_window_close'


class TreeCameraSounds(CONST_CONTAINER):
    GROUP = 'STATE_ext_hangar_newyear_tree_camera'
    FIR = 'STATE_ext_hangar_newyear_tree_camera_A'
    CHRISTMASTREE = FIR
    CHRISTMASTREE_TOP = 'STATE_ext_hangar_newyear_tree_camera_C'
    CHRISTMASTREE_TOY_DOWN = 'STATE_ext_hangar_newyear_tree_camera_B'
    CAMERA_FLY = 'hangar_newyear_tree_camera_fly'


class RewardSoundEvents(CONST_CONTAINER):
    GROUP = 'STATE_overlay_hangar_general'
    ENTER = 'STATE_overlay_hangar_general_on'
    EXIT = 'STATE_overlay_hangar_general_off'
    REWARD_SOUND_SPACE = 'overlay_hangar'


OVERLAY_HANGAR_SOUND_SPACE = CommonSoundSpaceSettings(name=RewardSoundEvents.REWARD_SOUND_SPACE, entranceStates={RewardSoundEvents.GROUP: RewardSoundEvents.ENTER}, exitStates={RewardSoundEvents.GROUP: RewardSoundEvents.EXIT}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
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
        self.__playEvent(NewYearSoundConfigKeys.CLOSE_EVENT)

    def clear(self):
        self.__soundsConfig = {}

    def setEnterViewState(self):
        stateValue = self.__getValueByKey(NewYearSoundConfigKeys.STATE_VALUE)
        if stateValue:
            SoundGroups.g_instance.setState(NewYearSoundVars.STATE_NEWYEAR_PLACE, stateValue)

    @staticmethod
    def playEvent(eventName):
        SoundGroups.g_instance.playSound2D(eventName)

    @staticmethod
    def setRTPC(name, value):
        SoundGroups.g_instance.setRTCPGlobal(name, value)

    @staticmethod
    def setStylesSwitchBox(toySetting):
        switchValue = _STYLES_BOX_SWITCHES_MAP.get(toySetting)
        if switchValue is not None:
            SoundGroups.g_instance.setSwitch(NewYearSoundVars.SWITCH_STYLES_BOX, switchValue)
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
            SoundGroups.g_instance.setSwitch(NewYearSoundVars.SWITCH_STYLES_TALISMAN, switchValue)
        return

    @staticmethod
    def setHangarFilteredState(on):
        state = States.HANGAR_FILTERED_ON if on else States.HANGAR_FILTERED_OFF
        SoundGroups.g_instance.setState(StatesGroup.HANGAR_FILTERED, state)

    @staticmethod
    def setHangarPlaceGarage():
        SoundGroups.g_instance.setState(NewYearSoundStates.STATE_PLACE, NewYearSoundStates.STATE_PLACE_GARAGE)

    @staticmethod
    def setGladeState(currentObject):
        stateName = getattr(NewYearSoundStates, GLADE_PREFIX + currentObject.upper())
        SoundGroups.g_instance.setState(NewYearSoundVars.STATE_NEWYEAR_PLACE, stateName)

    @staticmethod
    def playGladeEvent(objectName, eventType):
        eventName = getattr(NewYearSoundEvents, GLADE_PREFIX + objectName.upper() + eventType)
        SoundGroups.g_instance.playSound2D(eventName)

    @staticmethod
    def setTreeCameraState(currentObject):
        stateName = getattr(TreeCameraSounds, currentObject.upper())
        SoundGroups.g_instance.setState(TreeCameraSounds.GROUP, stateName)

    @staticmethod
    def setCityState():
        SoundGroups.g_instance.setState(NewYearSoundVars.STATE_NEWYEAR_PLACE, NewYearSoundStates.CITY)

    def __playEvent(self, eventKey):
        eventName = self.__getValueByKey(eventKey)
        if eventName:
            SoundGroups.g_instance.playSound2D(eventName)

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


class Videos(CONST_CONTAINER):
    CELEB_SPEECH = 0
    ONBOARDING_DAY = 1
    ONBOARDING_NIGHT = 2
    PET = 3


class VideoEvents(CONST_CONTAINER):
    VIDEO_START = {Videos.ONBOARDING_DAY: 'ny2025_video_intro_day',
     Videos.ONBOARDING_NIGHT: 'ny2025_video_intro_night',
     Videos.CELEB_SPEECH: 'ny_video_celeb_wishes_speech',
     Videos.PET: 'ny_video_enot_help'}


class VideoStartStopHandler(LootBoxVideoStartStopHandler):
    __slots__ = ()

    def getEventName(self, videoId, sourceID=''):
        return VideoEvents.VIDEO_START.get(videoId)
