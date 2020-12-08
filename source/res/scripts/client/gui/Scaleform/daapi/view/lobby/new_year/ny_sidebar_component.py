# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/new_year/ny_sidebar_component.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_CELEBRITY_CHALLENGE_VISITED, NY_CELEBRITY_QUESTS_VISITED_MASK, NY_OLD_COLLECTIONS_VISITED, NY_OLD_COLLECTIONS_BY_YEAR_VISITED
from frameworks.wulf import ViewFlags
from frameworks.wulf import ViewSettings
from gui.Scaleform.daapi.view.lobby.new_year import InjectWithContext
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_sidebar_model import NySidebarModel
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates, NewYearSoundsManager
from gui.impl.new_year.views.tabs_controller import GladeTabsController, AlbumsTabsController, RewardsTabsController
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import NYTabCtx
from helpers import dependency
from items import new_year
from items.components.ny_constants import CustomizationObjects
from new_year.ny_constants import SyncDataKeys, NyWidgetTopMenu, AdditionalCameraObject, Collections
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from gui.shared.event_dispatcher import NYViewCtx
    from gui.impl.new_year.views.tabs_controller import TabsController
_GLADE_SOUNDS_MAP = {NewYearSoundConfigKeys.ENTRANCE_EVENT: {CustomizationObjects.FIR: NewYearSoundEvents.TREE,
                                         CustomizationObjects.TABLEFUL: NewYearSoundEvents.KITCHEN,
                                         CustomizationObjects.INSTALLATION: NewYearSoundEvents.SNOWTANK,
                                         CustomizationObjects.ILLUMINATION: NewYearSoundEvents.LIGHTE,
                                         AdditionalCameraObject.MASCOT: NewYearSoundEvents.TALISMAN,
                                         AdditionalCameraObject.CELEBRITY: NewYearSoundEvents.CELEBRITY},
 NewYearSoundConfigKeys.EXIT_EVENT: {CustomizationObjects.FIR: NewYearSoundEvents.TREE_EXIT,
                                     CustomizationObjects.TABLEFUL: NewYearSoundEvents.KITCHEN_EXIT,
                                     CustomizationObjects.INSTALLATION: NewYearSoundEvents.SNOWTANK_EXIT,
                                     CustomizationObjects.ILLUMINATION: NewYearSoundEvents.LIGHTE_EXIT,
                                     AdditionalCameraObject.MASCOT: NewYearSoundEvents.TALISMAN_EXIT,
                                     AdditionalCameraObject.CELEBRITY: NewYearSoundEvents.CELEBRITY_EXIT},
 NewYearSoundConfigKeys.STATE_VALUE: {CustomizationObjects.FIR: NewYearSoundStates.TREE,
                                      CustomizationObjects.TABLEFUL: NewYearSoundStates.KITCHEN,
                                      CustomizationObjects.INSTALLATION: NewYearSoundStates.SNOWTANK,
                                      CustomizationObjects.ILLUMINATION: NewYearSoundStates.LIGHTE,
                                      AdditionalCameraObject.MASCOT: NewYearSoundStates.TALISMAN,
                                      AdditionalCameraObject.CELEBRITY: NewYearSoundStates.CELEBRITY}}
_COLLECTIONS_SOUNDS_MAP = {NewYearSoundConfigKeys.ENTRANCE_EVENT: {Collections.NewYear18: NewYearSoundEvents.ALBUM_SELECT_2018,
                                         Collections.NewYear19: NewYearSoundEvents.ALBUM_SELECT_2019,
                                         Collections.NewYear20: NewYearSoundEvents.ALBUM_SELECT_2020,
                                         Collections.NewYear21: NewYearSoundEvents.ALBUM_SELECT_2021},
 NewYearSoundConfigKeys.EXIT_EVENT: {Collections.NewYear18: NewYearSoundEvents.ALBUM_SELECT_2018_EXIT,
                                     Collections.NewYear19: NewYearSoundEvents.ALBUM_SELECT_2019_EXIT,
                                     Collections.NewYear20: NewYearSoundEvents.ALBUM_SELECT_2020_EXIT,
                                     Collections.NewYear21: NewYearSoundEvents.ALBUM_SELECT_2021_EXIT}}

class NYSidebar(NewYearHistoryNavigation):
    __slots__ = ('__tabsController', '__controllers', '__currentTab', '__currentView', '__soundsManager')
    _itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.ny_sidebar.NYSidebarUBInject())
        settings.flags = ViewFlags.COMPONENT
        settings.model = NySidebarModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NYSidebar, self).__init__(settings)
        self.__tabsController = None
        self.__controllers = {}
        self.__currentTab = None
        self.__currentView = None
        self.__soundsManager = None
        return

    @property
    def viewModel(self):
        return super(NYSidebar, self).getViewModel()

    def _onLoading(self, ctx=None, *args, **kwargs):
        super(NYSidebar, self)._onLoading(*args, **kwargs)
        self.viewModel.onSideBarBtnClick += self.__onSideBarBtnClick
        self._nyController.onDataUpdated += self.__onDataUpdated
        self._celebrityController.onQuestsUpdated += self.__onQuestUpdated
        AccountSettings.onSettingsChanging += self.__onAccountDataUpdated
        soundConfig = {NewYearSoundConfigKeys.ENTRANCE_EVENT: self.__getEntranceSoundEvent,
         NewYearSoundConfigKeys.EXIT_EVENT: self.__getExitSoundEvent,
         NewYearSoundConfigKeys.STATE_VALUE: self.__getSoundStateValue}
        self.__soundsManager = NewYearSoundsManager(soundConfig)
        self.__controllers = {NyWidgetTopMenu.GLADE: GladeTabsController(),
         NyWidgetTopMenu.COLLECTIONS: AlbumsTabsController(),
         NyWidgetTopMenu.REWARDS: RewardsTabsController()}
        g_eventBus.addListener(events.NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        if ctx is not None:
            self.__onSwitchView(ctx)
        return

    def _finalize(self):
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self._celebrityController.onQuestsUpdated -= self.__onQuestUpdated
        self.viewModel.onSideBarBtnClick -= self.__onSideBarBtnClick
        AccountSettings.onSettingsChanging -= self.__onAccountDataUpdated
        g_eventBus.removeListener(events.NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__tabsController is not None:
            self.__tabsController.closeTabs()
        self.__tabsController = None
        self.__controllers.clear()
        self.__soundsManager.onExitView()
        self.__soundsManager.clear()
        self.__currentView = None
        super(NYSidebar, self)._finalize()
        return

    def __onSwitchViewEvent(self, event):
        ctx = event.ctx
        self.__onSwitchView(ctx)

    def __onSwitchView(self, ctx):
        menuName = ctx.viewParams.menuName
        selectedTab = None
        self.viewModel.setViewName(menuName)
        if self.__currentView != menuName and self.__tabsController is not None:
            self.__tabsController.closeTabs()
        self.__tabsController = self.__controllers.get(menuName)
        if self.__tabsController is not None:
            self.__updateTabs(ctx.tabName, menuName)
            selectedTab = self.__tabsController.getSelectedName(self.viewModel.getItemsTabBar())
        else:
            self.__clearTabs()
        if self.__currentView != menuName or self.__currentTab != selectedTab:
            self.__soundsManager.onExitView()
            self.__currentView, self.__currentTab = menuName, selectedTab
            self.__soundsManager.onEnterView()
        return

    def __updateTabs(self, tabName, menuName):
        if tabName is not None:
            if self.__tabsController.getCurrentTabName() != tabName:
                self.__tabsController.selectTab(tabName)
        elif menuName == NyWidgetTopMenu.COLLECTIONS:
            tabName = self._tabCache.getCurrentYear()
            if self.__tabsController.getCurrentTabName() != tabName:
                self.__tabsController.selectTab(tabName)
        with self.viewModel.transaction() as model:
            tabsArray = model.getItemsTabBar()
            self.__tabsController.createTabModels(tabsArray)
            tabIdx = self.__tabsController.getSelectedTabIdx()
            model.setStartIndex(tabIdx)
        return

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
             SyncDataKeys.TALISMAN_TOY_TAKEN,
             SyncDataKeys.TOY_COLLECTION}
            if set(keys) & checkKeys:
                self.__tabsController.updateTabModels(self.viewModel.getItemsTabBar())
            return

    def __onQuestUpdated(self):
        if self.__tabsController is None:
            return
        else:
            self.__tabsController.updateTabModels(self.viewModel.getItemsTabBar())
            return

    def __onAccountDataUpdated(self, key, value):
        if self.__tabsController is None:
            return
        else:
            if key in (NY_CELEBRITY_CHALLENGE_VISITED,
             NY_CELEBRITY_QUESTS_VISITED_MASK,
             NY_OLD_COLLECTIONS_VISITED,
             NY_OLD_COLLECTIONS_BY_YEAR_VISITED):
                self.__tabsController.updateTabModels(self.viewModel.getItemsTabBar())
            return

    def __onSideBarBtnClick(self, args):
        tabName = args['tabName']
        self.__selectTab(tabName)

    def __selectTab(self, tabName):
        maxLevel = self._itemsCache.items.festivity.getMaxLevel()
        needToInvokeSound = self.__currentView != NyWidgetTopMenu.COLLECTIONS or maxLevel == new_year.CONSTS.MAX_ATMOSPHERE_LVL
        if needToInvokeSound:
            self.__soundsManager.onExitView()
        self.__currentTab = tabName
        self.__tabsController.selectTab(tabName)
        self.viewModel.setStartIndex(self.__tabsController.getSelectedTabIdx())
        g_eventBus.handleEvent(events.NewYearEvent(events.NewYearEvent.ON_SIDEBAR_SELECTED, ctx=NYTabCtx(tabName=tabName, menuName=self.viewModel.getViewName())), scope=EVENT_BUS_SCOPE.LOBBY)
        if needToInvokeSound:
            self.__soundsManager.onEnterView()

    def __getEntranceSoundEvent(self):
        if self.__currentView == NyWidgetTopMenu.GLADE:
            return _GLADE_SOUNDS_MAP.get(NewYearSoundConfigKeys.ENTRANCE_EVENT, {}).get(self.__currentTab)
        else:
            if self.__currentView == NyWidgetTopMenu.COLLECTIONS:
                maxLevel = self._itemsCache.items.festivity.getMaxLevel()
                if self.__currentTab == Collections.NewYear21 or maxLevel == new_year.CONSTS.MAX_ATMOSPHERE_LVL:
                    return _COLLECTIONS_SOUNDS_MAP.get(NewYearSoundConfigKeys.ENTRANCE_EVENT, {}).get(self.__currentTab)
            return None

    def __getExitSoundEvent(self):
        if self.__currentView == NyWidgetTopMenu.GLADE:
            return _GLADE_SOUNDS_MAP.get(NewYearSoundConfigKeys.EXIT_EVENT, {}).get(self.__currentTab)
        else:
            if self.__currentView == NyWidgetTopMenu.COLLECTIONS:
                maxLevel = self._itemsCache.items.festivity.getMaxLevel()
                if self.__currentTab == Collections.NewYear21 or maxLevel == new_year.CONSTS.MAX_ATMOSPHERE_LVL:
                    return _COLLECTIONS_SOUNDS_MAP.get(NewYearSoundConfigKeys.EXIT_EVENT, {}).get(self.__currentTab)
            return None

    def __getSoundStateValue(self):
        return _GLADE_SOUNDS_MAP.get(NewYearSoundConfigKeys.STATE_VALUE, {}).get(self.__currentTab) if self.__currentView == NyWidgetTopMenu.GLADE else None


class NYSidebarUBInject(InjectWithContext):
    __slots__ = ()

    def _getInjectViewClass(self):
        return NYSidebar
