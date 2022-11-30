# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/ny_sidebar_component.py
import typing
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_sidebar_model import NySidebarModel
from gui.impl.lobby.new_year.ny_history_presenter import NyHistoryPresenter
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates, NewYearSoundsManager
from gui.impl.new_year.views.tabs_controller import GladeTabsController, ChallengeTabsController, MarketplaceTabsController, FriendGladeTabsController
from gui.shared.event_dispatcher import NYTabCtx
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from items.components.ny_constants import CustomizationObjects
from new_year.ny_constants import SyncDataKeys, NyWidgetTopMenu, AdditionalCameraObject, Collections, CHALLENGE_TAB_TO_CAMERA_OBJ
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.new_year import ICelebritySceneController, ICelebrityController
from uilogging.ny.loggers import NySideBarFlowLogger, NyResourcesLogger
if typing.TYPE_CHECKING:
    from gui.impl.new_year.views.tabs_controller import NyTabsController
_GLADE_SOUNDS_MAP = {NewYearSoundConfigKeys.ENTRANCE_EVENT: {CustomizationObjects.FIR: NewYearSoundEvents.TREE,
                                         CustomizationObjects.FAIR: NewYearSoundEvents.FAIR,
                                         CustomizationObjects.INSTALLATION: NewYearSoundEvents.SNOWTANK,
                                         AdditionalCameraObject.RESOURCES: NewYearSoundEvents.RESOURCES,
                                         AdditionalCameraObject.UNDER_SPACE: NewYearSoundEvents.UNDER_SPACE},
 NewYearSoundConfigKeys.EXIT_EVENT: {CustomizationObjects.FIR: NewYearSoundEvents.TREE_EXIT,
                                     CustomizationObjects.FAIR: NewYearSoundEvents.FAIR_EXIT,
                                     CustomizationObjects.INSTALLATION: NewYearSoundEvents.SNOWTANK_EXIT,
                                     AdditionalCameraObject.RESOURCES: NewYearSoundEvents.RESOURCES_EXIT,
                                     AdditionalCameraObject.UNDER_SPACE: NewYearSoundEvents.UNDER_SPACE_EXIT},
 NewYearSoundConfigKeys.STATE_VALUE: {CustomizationObjects.FIR: NewYearSoundStates.TREE,
                                      CustomizationObjects.FAIR: NewYearSoundStates.FAIR,
                                      CustomizationObjects.INSTALLATION: NewYearSoundStates.SNOWTANK,
                                      AdditionalCameraObject.CELEBRITY: NewYearSoundStates.CELEBRITY,
                                      AdditionalCameraObject.RESOURCES: NewYearSoundStates.RESOURCES,
                                      AdditionalCameraObject.UNDER_SPACE: NewYearSoundStates.UNDER_SPACE}}
_MARKETPLACE_SOUNDS_MAP = {NewYearSoundConfigKeys.ENTRANCE_EVENT: {Collections.NewYear18: NewYearSoundEvents.ALBUM_SELECT_2019,
                                         Collections.NewYear19: NewYearSoundEvents.ALBUM_SELECT_2020,
                                         Collections.NewYear20: NewYearSoundEvents.ALBUM_SELECT_2021,
                                         Collections.NewYear21: NewYearSoundEvents.ALBUM_SELECT_2022,
                                         Collections.NewYear22: NewYearSoundEvents.ALBUM_SELECT_2023},
 NewYearSoundConfigKeys.EXIT_EVENT: {Collections.NewYear18: NewYearSoundEvents.ALBUM_SELECT_2019_EXIT,
                                     Collections.NewYear19: NewYearSoundEvents.ALBUM_SELECT_2020_EXIT,
                                     Collections.NewYear20: NewYearSoundEvents.ALBUM_SELECT_2021_EXIT,
                                     Collections.NewYear21: NewYearSoundEvents.ALBUM_SELECT_2022_EXIT,
                                     Collections.NewYear22: NewYearSoundEvents.ALBUM_SELECT_2023_EXIT}}
_GUESTS_SOUNDS_MAP = {NewYearSoundConfigKeys.ENTRANCE_EVENT: {AdditionalCameraObject.CHALLENGE: NewYearSoundEvents.CHALLENGE,
                                         AdditionalCameraObject.CELEBRITY_A: NewYearSoundEvents.CELEBRITY_A,
                                         AdditionalCameraObject.CELEBRITY_M: NewYearSoundEvents.CELEBRITY_M,
                                         AdditionalCameraObject.CELEBRITY_CAT: NewYearSoundEvents.CELEBRITY_CAT,
                                         AdditionalCameraObject.CELEBRITY_D: NewYearSoundEvents.CELEBRITY_D,
                                         AdditionalCameraObject.CELEBRITY: NewYearSoundEvents.CELEBRITY_HQ},
 NewYearSoundConfigKeys.EXIT_EVENT: {AdditionalCameraObject.CHALLENGE: NewYearSoundEvents.CHALLENGE_EXIT,
                                     AdditionalCameraObject.CELEBRITY_A: NewYearSoundEvents.CELEBRITY_A_EXIT,
                                     AdditionalCameraObject.CELEBRITY_M: NewYearSoundEvents.CELEBRITY_M_EXIT,
                                     AdditionalCameraObject.CELEBRITY_CAT: NewYearSoundEvents.CELEBRITY_CAT_EXIT,
                                     AdditionalCameraObject.CELEBRITY_D: NewYearSoundEvents.CELEBRITY_D_EXIT,
                                     AdditionalCameraObject.CELEBRITY: NewYearSoundEvents.CELEBRITY_HQ_EXIT},
 NewYearSoundConfigKeys.STATE_GROUP: NewYearSoundStates.STATE_CELEBRITY,
 NewYearSoundConfigKeys.STATE_VALUE: {AdditionalCameraObject.CHALLENGE: NewYearSoundStates.CHALLENGE,
                                      AdditionalCameraObject.CELEBRITY_A: NewYearSoundStates.CELEBRITY_A,
                                      AdditionalCameraObject.CELEBRITY_M: NewYearSoundStates.CELEBRITY_M,
                                      AdditionalCameraObject.CELEBRITY_CAT: NewYearSoundStates.CELEBRITY_CAT,
                                      AdditionalCameraObject.CELEBRITY_D: NewYearSoundStates.CELEBRITY_D,
                                      AdditionalCameraObject.CELEBRITY: NewYearSoundStates.CELEBRITY_HQ}}

class NYSidebar(NyHistoryPresenter):
    __slots__ = ('__tabsController', '__controllers', '__currentTab', '__currentViewName', '__soundsManager')
    __celebrityController = dependency.descriptor(ICelebrityController)
    __celebritySceneController = dependency.descriptor(ICelebritySceneController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __flowUILogger = NySideBarFlowLogger()

    def __init__(self, viewModel, parentView, *args, **kwargs):
        super(NYSidebar, self).__init__(viewModel, parentView)
        self.__tabsController = None
        self.__controllers = {}
        self.__currentTab = None
        self.__currentViewName = None
        self.__soundsManager = None
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, ctx=None, *args, **kwargs):
        super(NYSidebar, self).initialize(*args, **kwargs)
        self.viewModel.onChangeTab += self.__onChangeTab
        self._nyController.onDataUpdated += self.__onDataUpdated
        self.__celebritySceneController.onQuestsUpdated += self.__onQuestUpdated
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.__celebrityController.onCelebCompletedTokensUpdated += self.__onCelebCompletedTokensUpdated
        g_clientUpdateManager.addCallbacks({'inventory': self.__onInventoryUpdate})
        soundConfig = {NewYearSoundConfigKeys.ENTRANCE_EVENT: self.__getEntranceSoundEvent,
         NewYearSoundConfigKeys.EXIT_EVENT: self.__getExitSoundEvent,
         NewYearSoundConfigKeys.STATE_VALUE: self.__getSoundStateValue,
         NewYearSoundConfigKeys.STATE_GROUP: self.__getSoundStateGroup}
        self.__soundsManager = NewYearSoundsManager(soundConfig)
        self.__controllers = {NyWidgetTopMenu.GLADE: GladeTabsController(),
         NyWidgetTopMenu.FRIEND_GLADE: FriendGladeTabsController(),
         NyWidgetTopMenu.MARKETPLACE: MarketplaceTabsController(),
         NyWidgetTopMenu.CHALLENGE: ChallengeTabsController()}
        NewYearNavigation.onSwitchView += self.__onSwitchView
        NewYearNavigation.selectSidebarTabOutside += self.__onSelectTabOutside
        if ctx is not None:
            self.__onSwitchView(ctx)
        return

    def finalize(self):
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self.__celebritySceneController.onQuestsUpdated -= self.__onQuestUpdated
        self.__celebrityController.onCelebCompletedTokensUpdated -= self.__onCelebCompletedTokensUpdated
        self.viewModel.onChangeTab -= self.__onChangeTab
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        NewYearNavigation.onSwitchView -= self.__onSwitchView
        NewYearNavigation.selectSidebarTabOutside -= self.__onSelectTabOutside
        self.__tabsController = None
        self.__controllers.clear()
        self.__soundsManager.onExitView()
        self.__soundsManager.clear()
        self.__soundsManager = None
        self.__currentViewName = None
        super(NYSidebar, self).finalize()
        return

    def __onSwitchView(self, ctx):
        menuName = ctx.menuName
        selectedTab = None
        self.viewModel.setViewName(menuName)
        self.__tabsController = self.__controllers.get(menuName)
        if self.__tabsController is not None:
            self.__updateTabs(ctx.tabName, menuName)
            selectedTab = self.__tabsController.getSelectedName(self.viewModel.getItemsTabBar())
        else:
            self.__clearTabs()
        if self.__currentViewName != menuName or self.__currentTab != selectedTab:
            self.__soundsManager.onExitView()
            self.__currentViewName = menuName
            self.__currentTab = selectedTab
            self.__soundsManager.onEnterView()
        return

    def __onSelectTabOutside(self, menuName, tabName):
        if self.__currentViewName != menuName or self.__tabsController is None or self.__currentTab == tabName:
            return
        else:
            self.__soundsManager.onExitView()
            self.__currentTab = tabName
            self.__tabsController.selectTab(tabName)
            self.viewModel.setStartIndex(self.__tabsController.getSelectedTabIdx())
            self.__soundsManager.onEnterView()
            return

    def __updateTabs(self, tabName, menuName):
        if tabName is not None:
            if self.__tabsController.getCurrentTabName() != tabName:
                self.__tabsController.selectTab(tabName)
        self.__fillTabs()
        return

    def __fillTabs(self):
        with self.viewModel.transaction() as model:
            tabsArray = model.getItemsTabBar()
            self.__tabsController.createTabModels(tabsArray)
            tabIdx = self.__tabsController.getSelectedTabIdx()
            model.setStartIndex(tabIdx)

    def __validateTabs(self):
        self.__tabsController.updateTabModels(self.viewModel.getItemsTabBar())
        if self.__currentTab != self.__tabsController.getCurrentTabName():
            self.__onChangeTab({'tabName': self.__tabsController.getDefaultTab()})

    def __clearTabs(self):
        with self.viewModel.transaction() as model:
            tabsArray = model.getItemsTabBar()
            tabsArray.clear()
            tabsArray.invalidate()
            model.setStartIndex(0)

    def __onDataUpdated(self, keys, _):
        if self.__tabsController is None:
            return
        else:
            checkKeys = {SyncDataKeys.INVENTORY_TOYS,
             SyncDataKeys.SLOTS,
             SyncDataKeys.TOY_COLLECTION,
             SyncDataKeys.RESOURCE_COLLECTING}
            if set(keys) & checkKeys:
                self.__validateTabs()
            return

    def __onQuestUpdated(self):
        if self.__tabsController is None:
            return
        else:
            self.__validateTabs()
            return

    def __onCelebCompletedTokensUpdated(self):
        if self.__tabsController is None:
            return
        else:
            if self.__currentViewName == NyWidgetTopMenu.CHALLENGE:
                self.__validateTabs()
            return

    def __onInventoryUpdate(self, invDiff):
        if GUI_ITEM_TYPE.CUSTOMIZATION in invDiff and self.__currentViewName == NyWidgetTopMenu.MARKETPLACE:
            self.__validateTabs()

    def __onSettingsChanged(self, diff):
        if self.__tabsController is None:
            return
        else:
            tabSettingKeys = self.__tabsController.getSettingKeysForUpdate()
            if tabSettingKeys.intersection(set(diff.keys())):
                self.__updateTabs(self.__currentTab, self.__currentViewName)
            else:
                customTabs = self.__tabsController.getCustomTabsKeyUpdate()
                intersect = set(diff.keys()).intersection(customTabs.keys())
                if intersect:
                    tabsToUpdate = [ data for key, data in customTabs.iteritems() if key in intersect ]
                    self.__tabsController.updateTabsModel(tabsToUpdate, self.viewModel.getItemsTabBar())
            return

    def __onChangeTab(self, args):
        tabName = str(args['tabName'])
        self.__soundsManager.playEvent(NewYearSoundEvents.SIDE_BAR_CLICK)
        self.__flowUILogger.logTabSelect(view=self.__currentViewName, currentTab=self.__tabsController.getCurrentTabName(), targetTab=tabName)
        self.__selectTab(tabName)

    def __selectTab(self, tabName):
        self.__soundsManager.onExitView()
        self.__currentTab = tabName
        self.__tabsController.selectTab(tabName)
        with self.viewModel.transaction() as model:
            model.setStartIndex(self.__tabsController.getSelectedTabIdx())
        NewYearNavigation.onSidebarSelected(ctx=NYTabCtx(tabName=tabName, menuName=self.viewModel.getViewName()))
        self.__soundsManager.onEnterView()
        if tabName == 'Resources':
            NyResourcesLogger().logMenuClick('tab')

    def __getEntranceSoundEvent(self):
        return self.__getSoundEvent(NewYearSoundConfigKeys.ENTRANCE_EVENT)

    def __getExitSoundEvent(self):
        return self.__getSoundEvent(NewYearSoundConfigKeys.EXIT_EVENT)

    def __getSoundEvent(self, eventType):
        if self.__currentViewName in (NyWidgetTopMenu.GLADE, NyWidgetTopMenu.FRIEND_GLADE):
            return _GLADE_SOUNDS_MAP.get(eventType, {}).get(self.__currentTab)
        elif self.__currentViewName == NyWidgetTopMenu.MARKETPLACE:
            return _MARKETPLACE_SOUNDS_MAP.get(eventType, {}).get(self.__currentTab)
        elif self.__currentViewName in (NyWidgetTopMenu.CHALLENGE, NyWidgetTopMenu.FRIEND_CHALLENGE):
            camObj = CHALLENGE_TAB_TO_CAMERA_OBJ.get(self.__currentTab)
            return _GUESTS_SOUNDS_MAP.get(eventType, {}).get(camObj)
        else:
            return None

    def __getSoundStateValue(self):
        if self.__currentViewName is NyWidgetTopMenu.GLADE:
            selectedTabName = self.__tabsController.getCurrentTabName()
            return _GLADE_SOUNDS_MAP.get(NewYearSoundConfigKeys.STATE_VALUE, {}).get(selectedTabName)
        elif self.__currentViewName is NyWidgetTopMenu.CHALLENGE:
            camObj = CHALLENGE_TAB_TO_CAMERA_OBJ.get(self.__currentTab)
            return _GUESTS_SOUNDS_MAP.get(NewYearSoundConfigKeys.STATE_VALUE, {}).get(camObj)
        else:
            return None

    def __getSoundStateGroup(self):
        return _GUESTS_SOUNDS_MAP.get(NewYearSoundConfigKeys.STATE_GROUP) if self.__currentViewName == NyWidgetTopMenu.CHALLENGE else None
