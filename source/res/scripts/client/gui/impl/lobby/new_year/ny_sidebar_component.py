# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/ny_sidebar_component.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_OLD_COLLECTIONS_BY_YEAR_VISITED, NY_OLD_REWARDS_BY_YEAR_VISITED
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_sidebar_model import NySidebarModel
from gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from gui.impl.new_year.navigation import NewYearTabCache
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates, NewYearSoundsManager
from gui.impl.new_year.views.tabs_controller import GladeTabsController, AlbumsTabsController, RewardsTabsController
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import NYTabCtx
from helpers import dependency
from items.components.ny_constants import CustomizationObjects
from new_year.ny_constants import SyncDataKeys, NyWidgetTopMenu, Collections
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from gui.shared.event_dispatcher import NYViewCtx
    from gui.impl.new_year.views.tabs_controller import TabsController
_GLADE_SOUNDS_MAP = {NewYearSoundConfigKeys.ENTRANCE_EVENT: {CustomizationObjects.FIR: NewYearSoundEvents.TREE},
 NewYearSoundConfigKeys.EXIT_EVENT: {CustomizationObjects.FIR: NewYearSoundEvents.TREE_EXIT},
 NewYearSoundConfigKeys.STATE_VALUE: {CustomizationObjects.FIR: NewYearSoundStates.TREE}}
_COLLECTIONS_SOUNDS_MAP = {NewYearSoundConfigKeys.ENTRANCE_EVENT: {Collections.NewYear18: NewYearSoundEvents.ALBUM_SELECT_2018,
                                         Collections.NewYear19: NewYearSoundEvents.ALBUM_SELECT_2019,
                                         Collections.NewYear20: NewYearSoundEvents.ALBUM_SELECT_2020,
                                         Collections.NewYear21: NewYearSoundEvents.ALBUM_SELECT_2021,
                                         Collections.NewYear22: NewYearSoundEvents.ALBUM_SELECT_2022},
 NewYearSoundConfigKeys.EXIT_EVENT: {Collections.NewYear18: NewYearSoundEvents.ALBUM_SELECT_2018_EXIT,
                                     Collections.NewYear19: NewYearSoundEvents.ALBUM_SELECT_2019_EXIT,
                                     Collections.NewYear20: NewYearSoundEvents.ALBUM_SELECT_2020_EXIT,
                                     Collections.NewYear21: NewYearSoundEvents.ALBUM_SELECT_2021_EXIT,
                                     Collections.NewYear22: NewYearSoundEvents.ALBUM_SELECT_2022_EXIT}}

class NYSidebar(HistorySubModelPresenter):
    __slots__ = ('__tabsController', '__controllers', '__currentTab', '__currentViewName', '__soundsManager')
    __newYearController = dependency.descriptor(INewYearController)
    __settingsCore = dependency.descriptor(ISettingsCore)

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
        self.viewModel.onSideBarBtnClick += self.__onSideBarBtnClick
        self._nyController.onDataUpdated += self.__onDataUpdated
        AccountSettings.onSettingsChanging += self.__onAccountDataUpdated
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged
        soundConfig = {NewYearSoundConfigKeys.ENTRANCE_EVENT: self.__getEntranceSoundEvent,
         NewYearSoundConfigKeys.EXIT_EVENT: self.__getExitSoundEvent,
         NewYearSoundConfigKeys.STATE_VALUE: self.__getSoundStateValue}
        self.__soundsManager = NewYearSoundsManager(soundConfig)
        self.__controllers = {NyWidgetTopMenu.GLADE: GladeTabsController(),
         NyWidgetTopMenu.COLLECTIONS: AlbumsTabsController(),
         NyWidgetTopMenu.REWARDS: RewardsTabsController()}
        g_eventBus.addListener(events.NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.NewYearEvent.SELECT_SIDEBAR_TAB_OUTSIDE, self.__onSelectTabOutside, scope=EVENT_BUS_SCOPE.LOBBY)
        if ctx is not None:
            self.__onSwitchView(ctx)
        return

    def finalize(self):
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self.viewModel.onSideBarBtnClick -= self.__onSideBarBtnClick
        AccountSettings.onSettingsChanging -= self.__onAccountDataUpdated
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged
        g_eventBus.removeListener(events.NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.NewYearEvent.SELECT_SIDEBAR_TAB_OUTSIDE, self.__onSelectTabOutside, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__tabsController = None
        self.__controllers.clear()
        self.__soundsManager.onExitView()
        self.__soundsManager.clear()
        self.__soundsManager = None
        self.__currentViewName = None
        super(NYSidebar, self).finalize()
        return

    def __onSwitchViewEvent(self, event):
        ctx = event.ctx
        self.__onSwitchView(ctx)

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

    def __onSelectTabOutside(self, event):
        menuName = event.ctx['menuName']
        tabName = event.ctx['tabName']
        if self.__currentViewName != menuName or self.__tabsController is None or self.__currentTab == tabName:
            return
        else:
            needToInvokeSound = self.__currentViewName != NyWidgetTopMenu.COLLECTIONS or self.__newYearController.isMaxAtmosphereLevel()
            if needToInvokeSound:
                self.__soundsManager.onExitView()
            self.__currentTab = tabName
            self.__tabsController.selectTab(tabName)
            self.viewModel.setStartIndex(self.__tabsController.getSelectedTabIdx())
            if needToInvokeSound:
                self.__soundsManager.onEnterView()
            return

    def __updateTabs(self, tabName, menuName):
        if tabName is not None:
            if self.__tabsController.getCurrentTabName() != tabName:
                self.__tabsController.selectTab(tabName)
        if self._tabCache.getIntroScreenState(menuName) == NewYearTabCache.OPENED_INTRO_STATE:
            self.__clearTabs()
        else:
            self.__fillTabs()
        return

    def __fillTabs(self):
        with self.viewModel.transaction() as model:
            tabsArray = model.getItemsTabBar()
            self.__tabsController.createTabModels(tabsArray)
            tabIdx = self.__tabsController.getSelectedTabIdx()
            model.setStartIndex(tabIdx)

    def __validateTabs(self):
        if self._tabCache.getIntroScreenState(self.__currentViewName) == NewYearTabCache.OPENED_INTRO_STATE:
            return
        self.__tabsController.updateTabModels(self.viewModel.getItemsTabBar())

    def __clearTabs(self):
        with self.viewModel.transaction() as model:
            tabsArray = model.getItemsTabBar()
            tabsArray.clear()
            tabsArray.invalidate()
            model.setStartIndex(0)

    def __onDataUpdated(self, keys):
        if self.__tabsController is None:
            return
        else:
            checkKeys = {SyncDataKeys.INVENTORY_TOYS,
             SyncDataKeys.SLOTS,
             SyncDataKeys.TOY_COLLECTION,
             SyncDataKeys.TOY_FRAGMENTS}
            if set(keys) & checkKeys:
                self.__validateTabs()
            return

    def __onQuestUpdated(self):
        if self.__tabsController is None:
            return
        else:
            self.__validateTabs()
            return

    def __onAccountDataUpdated(self, key, value):
        if self.__tabsController is None:
            return
        else:
            if key in (NY_OLD_COLLECTIONS_BY_YEAR_VISITED, NY_OLD_REWARDS_BY_YEAR_VISITED):
                self.__validateTabs()
            return

    def __onSettingsChanged(self, diff):
        if self.__tabsController is None:
            return
        else:
            if NewYearStorageKeys.GLADE_INTRO_VISITED in diff:
                self.__updateTabs(self.__currentTab, self.__currentViewName)
            return

    def __onSideBarBtnClick(self, args):
        tabName = args['tabName']
        self.__soundsManager.playEvent(NewYearSoundEvents.SIDE_BAR_CLICK)
        self.__selectTab(tabName)

    def __selectTab(self, tabName):
        needToInvokeSound = self.__currentViewName != NyWidgetTopMenu.COLLECTIONS or self.__newYearController.isMaxAtmosphereLevel()
        if needToInvokeSound:
            self.__soundsManager.onExitView()
        self.__currentTab = tabName
        self.__tabsController.selectTab(tabName)
        with self.viewModel.transaction() as model:
            model.setStartIndex(self.__tabsController.getSelectedTabIdx())
        g_eventBus.handleEvent(events.NewYearEvent(events.NewYearEvent.ON_SIDEBAR_SELECTED, ctx=NYTabCtx(tabName=tabName, menuName=self.viewModel.getViewName())), scope=EVENT_BUS_SCOPE.LOBBY)
        if needToInvokeSound:
            self.__soundsManager.onEnterView()

    def __getEntranceSoundEvent(self):
        return self.__getSoundEvent(NewYearSoundConfigKeys.ENTRANCE_EVENT)

    def __getExitSoundEvent(self):
        return self.__getSoundEvent(NewYearSoundConfigKeys.EXIT_EVENT)

    def __getSoundEvent(self, eventType):
        if self.__currentViewName == NyWidgetTopMenu.GLADE:
            return _GLADE_SOUNDS_MAP.get(eventType, {}).get(self.__currentTab)
        else:
            if self.__currentViewName == NyWidgetTopMenu.COLLECTIONS:
                isMaxAtmosphereLevel = self.__newYearController.isMaxAtmosphereLevel()
                if self.__currentTab == Collections.NewYear22 or isMaxAtmosphereLevel:
                    return _COLLECTIONS_SOUNDS_MAP.get(eventType, {}).get(self.__currentTab)
                if not isMaxAtmosphereLevel:
                    return _COLLECTIONS_SOUNDS_MAP.get(eventType, {}).get(Collections.NewYear22)
            return None

    def __getSoundStateValue(self):
        if self.__currentViewName == NyWidgetTopMenu.GLADE:
            selectedTabName = self.__tabsController.getCurrentTabName()
            return _GLADE_SOUNDS_MAP.get(NewYearSoundConfigKeys.STATE_VALUE, {}).get(selectedTabName)
        else:
            return None
