# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/new_year_sounds.py
import WWISE
import SoundGroups
from mappings import AnchorNames
from skeletons.new_year import INYSoundEvents, INewYearController
from helpers import dependency
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.Scaleform.genConsts.NY_CONSTANTS import NY_CONSTANTS
from items.new_year_types import NATIONAL_SETTINGS, INVALID_TOY_ID

class NYSoundEvents(INYSoundEvents):
    ON_TAB_CLICK = 'hangar_h07_newyear_2018_transition'
    ON_CRAFT_CLICK = 'hangar_h07_newyear_2018_create_toy'
    ON_BOX_IS_GOT = 'hangar_h07_newyear_2018_task_box'
    ON_TOY_HANG = {AnchorNames.TREE: 'hangar_h07_newyear_2018_add_toy_tree',
     AnchorNames.SNOWMAN: 'hangar_h07_newyear_2018_add_toy_snowman',
     AnchorNames.HOUSE: 'hangar_h07_newyear_2018_add_toy_home',
     AnchorNames.LIGHT: 'hangar_h07_newyear_2018_add_toy_light'}
    ON_HOUSE_LAMP_SET = 'hangar_h07_newyear_2018_add_toy_home_sparklers'
    ON_OPEN_HANGAR = 'hangar_h07_newyear_2018_main'
    ON_CLOSE_HANGAR = 'hangar_h07_newyear_2018_main_exit'
    ON_OPEN_CUSTOMIZATION = {AnchorNames.TREE: 'hangar_h07_newyear_2018_tree',
     AnchorNames.SNOWMAN: 'hangar_h07_newyear_2018_snowman',
     AnchorNames.HOUSE: 'hangar_h07_newyear_2018_home',
     AnchorNames.LIGHT: 'hangar_h07_newyear_2018_light'}
    ON_OPEN_CRAFT = 'hangar_h07_newyear_2018_toy'
    ON_OPEN_BREAK = 'hangar_h07_newyear_2018_pieces'
    ON_OPEN_REWARDS = 'hangar_h07_newyear_2018_atmosphere'
    ON_OPEN_COLLECTION_GROUPS = 'hangar_h07_newyear_2018_album'
    ON_CLOSE_CUSTOMIZATION = {AnchorNames.TREE: 'hangar_h07_newyear_2018_tree_exit',
     AnchorNames.SNOWMAN: 'hangar_h07_newyear_2018_snowman_exit',
     AnchorNames.HOUSE: 'hangar_h07_newyear_2018_home_exit',
     AnchorNames.LIGHT: 'hangar_h07_newyear_2018_light_exit'}
    ON_CLOSE_CRAFT = 'hangar_h07_newyear_2018_toy_exit'
    ON_CLOSE_BREAK = 'hangar_h07_newyear_2018_pieces_exit'
    ON_CLOSE_REWARDS = 'hangar_h07_newyear_2018_atmosphere_exit'
    ON_CLOSE_COLLECTION_GROUPS = 'hangar_h07_newyear_2018_album_exit'
    STATE_ID = 'STATE_newyear2018'
    STATE_ON_HANGAR = 'STATE_newyear2018_hangar'
    STATE_ON_CUSTOMIZATION = {AnchorNames.TREE: 'STATE_newyear2018_tree',
     AnchorNames.SNOWMAN: 'STATE_newyear2018_snowman',
     AnchorNames.HOUSE: 'STATE_newyear2018_home',
     AnchorNames.LIGHT: 'STATE_newyear2018_light'}
    STATE_ON_CRAFT = 'STATE_newyear2018_toy'
    STATE_ON_BREAK = 'STATE_newyear2018_pieces'
    STATE_ON_REWARDS = 'STATE_newyear2018_atmosphere'
    STATE_ON_COLLECTION_GROUPS = 'STATE_newyear2018_album'
    CRAFT_SELECT_TYPE_OR_LEVEL = 'hangar_h07_newyear_2018_choice_toys'
    CRAFT_SELECT_SETTING = 'hangar_h07_newyear_2018_choice_toys_style'
    CRAFT_MACHINE_ANIMATION = 'hangar_h07_newyear_2018_choice_toys_screen'
    CRAFT_COST_INCREASED = 'hangar_h07_newyear_2018_cost_toys_up'
    CRAFT_COST_DECREASED = 'hangar_h07_newyear_2018_cost_toys_down'
    CRAFT_COST_SAME = 'hangar_h07_newyear_2018_cost_toys_not_change'
    CRAFT_BUTTON_PRESSED_CRAFT = 'hangar_h07_newyear_2018_make_toys'
    CRAFT_TOY_CRAFTED = 'hangar_h07_newyear_2018_make_toys_down'
    CRAFT_TO_BREAK = 'hangar_h07_newyear_2018_pieces_toys_enter'
    ON_TOY_FRAGMENT_CLICK = 'hangar_h07_newyear_2018_pieces_toys_enter_castom'
    BREAK_BUTTON_PRESSED_BREAK = 'hangar_h07_newyear_2018_pieces_toys_FX'
    LOOTBOX_CAMERA_SWITCH = 'hangar_h07_newyear_2018_open_box1_01'
    LOOTBOX_START_FINISH_OPEN = 'hangar_h07_newyear_2018_open_box1_02'
    LOOTBOX_SHOW_UI_CONTENT = 'hangar_h07_newyear_2018_open_box1_03'
    RTPC_DECORATION = 'RTPC_ext_ev_christmas_tree_decorating'
    RTPC_DECORATION_ANCHORS = (AnchorNames.TREE, AnchorNames.SNOWMAN)
    RTPC_ATMOSPHERE = 'RTPC_ext_ev_newyear2018_level_atmosphere'
    RTPC_TOYS = 'RTPC_ext_ev_newyear2018_level_toys'
    BOX_SWITCH_ID = 'SWITCH_ext_newyear2018_style_box'
    BOX_SWITCHES = {NY_CONSTANTS.NY_SETTINGS_TYPE_SOVIET: 'SWITCH_ext_newyear2018_style_box_soviet',
     NY_CONSTANTS.NY_SETTINGS_TYPE_ASIAN: 'SWITCH_ext_newyear2018_style_box_chinese',
     NY_CONSTANTS.NY_SETTINGS_TYPE_TRADITIONAL_WESTERN: 'SWITCH_ext_newyear2018_style_box_traditional',
     NY_CONSTANTS.NY_SETTINGS_TYPE_MODERN_WESTERN: 'SWITCH_ext_newyear2018_style_box_modern'}
    DEFAULT_BOX_SWITCH = 'SWITCH_ext_newyear2018_style_box_random'
    DECOR_STATE_ID = 'STATE_ext_newyear2018_style'
    DECOR_STATES = {NY_CONSTANTS.NY_SETTINGS_TYPE_SOVIET: 'STATE_ext_newyear2018_style_soviet',
     NY_CONSTANTS.NY_SETTINGS_TYPE_ASIAN: 'STATE_ext_newyear2018_style_chinese',
     NY_CONSTANTS.NY_SETTINGS_TYPE_TRADITIONAL_WESTERN: 'STATE_ext_newyear2018_style_traditional',
     NY_CONSTANTS.NY_SETTINGS_TYPE_MODERN_WESTERN: 'STATE_ext_newyear2018_style_modern'}
    DECOR_LOCATION_TO_SLOT = {AnchorNames.SNOWMAN: NY_CONSTANTS.SLOT_SNOWMAN_RIGHT_1_ID,
     AnchorNames.HOUSE: NY_CONSTANTS.SLOT_HOUSE_RIGHT_1_ID,
     AnchorNames.LIGHT: NY_CONSTANTS.SLOT_LIGHT_RIGHT_1_ID}
    DECOR_EXCEPT_STATES = DECOR_LOCATION_TO_SLOT.keys()
    TABS_TO_ANCHORS = {NY_CONSTANTS.SIDE_BAR_TREE_ID: AnchorNames.TREE,
     NY_CONSTANTS.SIDE_BAR_SNOWMAN_ID: AnchorNames.SNOWMAN,
     NY_CONSTANTS.SIDE_BAR_HOUSE_ID: AnchorNames.HOUSE,
     NY_CONSTANTS.SIDE_BAR_LIGHT_ID: AnchorNames.LIGHT}

    @staticmethod
    def playSound(name):
        if name:
            SoundGroups.g_instance.playSound2D(name)

    @staticmethod
    def setState(name):
        if name:
            WWISE.WW_setState(NYSoundEvents.STATE_ID, name)

    @staticmethod
    def setBoxSwitch(nation):
        name = NYSoundEvents.BOX_SWITCHES.get(nation, NYSoundEvents.DEFAULT_BOX_SWITCH)
        WWISE.WW_setSwitch(NYSoundEvents.BOX_SWITCH_ID, name)

    @staticmethod
    def setDecorationsState(name):
        if name:
            WWISE.WW_setState(NYSoundEvents.DECOR_STATE_ID, name)

    @staticmethod
    def setRTPC(name, value):
        WWISE.WW_setRTCPGlobal(name, value)

    @staticmethod
    def playOpenCustomization(state):
        if state in NYSoundEvents.TABS_TO_ANCHORS:
            state = NYSoundEvents.TABS_TO_ANCHORS[state]
        rtpcValue = 1 if state in NYSoundEvents.RTPC_DECORATION_ANCHORS else 0
        NYSoundEvents.setRTPC(NYSoundEvents.RTPC_DECORATION, rtpcValue)
        if state:
            NYSoundEvents.playSound(NYSoundEvents.ON_OPEN_CUSTOMIZATION.get(state, None))
            NYSoundEvents.setState(NYSoundEvents.STATE_ON_CUSTOMIZATION.get(state, None))
        else:
            NYSoundEvents.playSound(NYSoundEvents.ON_OPEN_HANGAR)
            NYSoundEvents.setState(NYSoundEvents.STATE_ON_HANGAR)
        return

    @staticmethod
    def playCloseCustomization(state):
        if state:
            NYSoundEvents.playSound(NYSoundEvents.ON_CLOSE_CUSTOMIZATION.get(state, None))
        return

    def onCustomizationStateChanged(self, newState):
        if self.__customizationState == newState:
            return
        old_state = self.__customizationState
        self.__customizationState = newState
        NYSoundEvents.playCloseCustomization(old_state)
        NYSoundEvents.playOpenCustomization(newState)
        self.__updateDecorationsState()

    newYearController = dependency.descriptor(INewYearController)

    def __init__(self):
        self.__atmosphereLevel = None
        self.__currentTopNation = None
        self.__customizationState = None
        g_hangarSpace.onSpaceCreate += self.__onSpaceCreated
        return

    def __onSpaceCreated(self):
        if not self.newYearController.isAvailable():
            return
        g_hangarSpace.onSpaceDestroy += self.__onSpaceDestroyed
        self.__atmosphereLevel = self.newYearController.getProgress().level
        self.setRTPC(self.RTPC_ATMOSPHERE, self.__atmosphereLevel)
        NYSoundEvents.setRTPC(NYSoundEvents.RTPC_DECORATION, 0)
        NYSoundEvents.playSound(NYSoundEvents.ON_OPEN_HANGAR)
        NYSoundEvents.setState(NYSoundEvents.STATE_ON_HANGAR)
        self.__updateDecorationsState()
        self.newYearController.onProgressChanged += self.__onProgressChanged
        self.newYearController.onInventoryUpdated += self.__updateDecorationsState
        self.newYearController.onToysBreak += NYSoundEvents.__onToysBreak

    def __onSpaceDestroyed(self):
        NYSoundEvents.playSound(NYSoundEvents.ON_CLOSE_HANGAR)
        self.newYearController.onProgressChanged -= self.__onProgressChanged
        self.newYearController.onInventoryUpdated -= self.__updateDecorationsState
        self.newYearController.onToysBreak -= NYSoundEvents.__onToysBreak
        g_hangarSpace.onSpaceDestroy -= self.__onSpaceDestroyed

    @staticmethod
    def __onToysBreak(*args):
        NYSoundEvents.playSound(NYSoundEvents.BREAK_BUTTON_PRESSED_BREAK)

    def __onProgressChanged(self, progress):
        if progress.level != self.__atmosphereLevel:
            self.__atmosphereLevel = progress.level
            self.setRTPC(self.RTPC_ATMOSPHERE, self.__atmosphereLevel)

    def __updateDecorationsState(self):
        nation = None
        if self.__customizationState in NYSoundEvents.DECOR_EXCEPT_STATES:
            nation = self.__getToysNationForLocation(self.__customizationState)
        if nation is None:
            nation = self.__findTopNation()
        if nation != self.__currentTopNation:
            self.__currentTopNation = nation
            self.setDecorationsState(self.DECOR_STATES.get(self.__currentTopNation, None))
        return

    def __findTopNation(self):
        nations_toys = [0] * len(NATIONAL_SETTINGS)
        for slotID in xrange(len(self.newYearController.slotsDescrs)):
            placedToy = self.newYearController.getPlacedToy(slotID)
            if placedToy.id != INVALID_TOY_ID:
                nations_toys[placedToy.settingID] += 1

        topNationId = nations_toys.index(max(nations_toys))
        return NATIONAL_SETTINGS[topNationId]

    def __getToysNationForLocation(self, state):
        slotID = NYSoundEvents.DECOR_LOCATION_TO_SLOT.get(state, None)
        if slotID is None:
            return
        else:
            placedToy = self.newYearController.getPlacedToy(slotID)
            return None if placedToy.id == INVALID_TOY_ID else NATIONAL_SETTINGS[placedToy.settingID]

    def fini(self):
        g_hangarSpace.onSpaceCreate -= self.__onSpaceCreated
        g_hangarSpace.onSpaceDestroy -= self.__onSpaceDestroyed
