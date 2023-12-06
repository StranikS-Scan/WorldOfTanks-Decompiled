# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/ny_menu_component.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NEW_YEAR
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_main_menu_model import NyMainMenuModel
from gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from gui.impl.lobby.new_year.tooltips.ny_menu_collections_tooltip import NyMenuCollectionsTooltip
from gui.impl.lobby.new_year.tooltips.ny_menu_shards_tooltip import NyMenuShardsTooltip
from gui.impl.new_year.navigation import ViewAliases, NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates, NewYearSoundsManager
from gui.impl.new_year.views.tabs_controller import NewYearMainTabsController
from gui.shared import EVENT_BUS_SCOPE, events
from new_year.ny_constants import NyWidgetTopMenu
if typing.TYPE_CHECKING:
    from gui.impl.new_year.views.tabs_controller import TabsController
    from gui.shared.event_dispatcher import NYViewCtx
_NAVIGATION_ALIAS_VIEWS = {NyWidgetTopMenu.GLADE: ViewAliases.GLADE_VIEW,
 NyWidgetTopMenu.DECORATIONS: ViewAliases.CRAFT_VIEW,
 NyWidgetTopMenu.COLLECTIONS: ViewAliases.ALBUM_VIEW,
 NyWidgetTopMenu.REWARDS: ViewAliases.REWARDS_VIEW,
 NyWidgetTopMenu.SHARDS: ViewAliases.BREAK_VIEW,
 NyWidgetTopMenu.INFO: ViewAliases.INFO_VIEW}
_SOUNDS_MAP = {NewYearSoundConfigKeys.ENTRANCE_EVENT: {NyWidgetTopMenu.GLADE: NewYearSoundEvents.GLADE,
                                         NyWidgetTopMenu.DECORATIONS: NewYearSoundEvents.TOYS,
                                         NyWidgetTopMenu.COLLECTIONS: NewYearSoundEvents.ALBUM_SELECT,
                                         NyWidgetTopMenu.INFO: NewYearSoundEvents.INFO,
                                         NyWidgetTopMenu.REWARDS: NewYearSoundEvents.REWARDS_LEVELS,
                                         NyWidgetTopMenu.SHARDS: NewYearSoundEvents.DEBRIS},
 NewYearSoundConfigKeys.EXIT_EVENT: {NyWidgetTopMenu.GLADE: NewYearSoundEvents.GLADE_EXIT,
                                     NyWidgetTopMenu.DECORATIONS: NewYearSoundEvents.TOYS_EXIT,
                                     NyWidgetTopMenu.COLLECTIONS: NewYearSoundEvents.ALBUM_SELECT_EXIT,
                                     NyWidgetTopMenu.INFO: NewYearSoundEvents.INFO_EXIT,
                                     NyWidgetTopMenu.REWARDS: NewYearSoundEvents.REWARDS_LEVELS_EXIT,
                                     NyWidgetTopMenu.SHARDS: NewYearSoundEvents.DEBRIS_EXIT},
 NewYearSoundConfigKeys.STATE_VALUE: {NyWidgetTopMenu.DECORATIONS: NewYearSoundStates.TOYS,
                                      NyWidgetTopMenu.COLLECTIONS: NewYearSoundStates.ALBUM_SELECT,
                                      NyWidgetTopMenu.INFO: NewYearSoundStates.INFO,
                                      NyWidgetTopMenu.SHARDS: NewYearSoundStates.DEBRIS}}

class NYMainMenu(HistorySubModelPresenter):

    def __init__(self, viewModel, parentView, *args, **kwargs):
        super(NYMainMenu, self).__init__(viewModel, parentView, *args, **kwargs)
        self.__tabsController = NewYearMainTabsController()
        self.__soundsManager = None
        self.__currentView = None
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        tooltips = R.views.lobby.new_year.tooltips
        if contentID == tooltips.NyMenuShardsTooltip():
            return NyMenuShardsTooltip()
        return NyMenuCollectionsTooltip() if contentID == tooltips.NyMenuCollectionsTooltip() else super(NYMainMenu, self).createToolTipContent(event, contentID)

    def initialize(self, *args, **kwargs):
        super(NYMainMenu, self).initialize(*args, **kwargs)
        soundConfig = {NewYearSoundConfigKeys.ENTRANCE_EVENT: self.__getEntranceSoundEvent,
         NewYearSoundConfigKeys.EXIT_EVENT: self.__getExitSoundEvent,
         NewYearSoundConfigKeys.STATE_VALUE: self.__getSoundStateValue}
        self.__soundsManager = NewYearSoundsManager(soundConfig)
        self.viewModel.setIsExtendedAnim(True)

    def finalize(self):
        self.__soundsManager.onExitView()
        self.__soundsManager.clear()
        self.__soundsManager = None
        self.__currentView = None
        super(NYMainMenu, self).finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onInfoBtnClick, self.__onInfoBtnClick),
         (self.viewModel.onSwitchContent, self.__onMenuItemSelected),
         (self._nyController.onDataUpdated, self.__onDataUpdated),
         (self._nyController.onVariadicDiscountsUpdated, self.__onVariadicDiscountsUpdated),
         (AccountSettings.onSettingsChanging, self.__onAccountDataUpdated))

    def _getListeners(self):
        return ((events.NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchViewEvent, EVENT_BUS_SCOPE.LOBBY),)

    def _getCallbacks(self):
        return (('tokens', self.__onTokensChanged),)

    def __onInfoBtnClick(self):
        NewYearNavigation.showInfoView(showDefaultTabForced=True)

    def __onMenuItemSelected(self, args):
        menuName = args['view']
        viewAlias = _NAVIGATION_ALIAS_VIEWS[menuName]
        self._navigationHistory.clear()
        with self.viewModel.transaction() as tx:
            tx.setStartIndexMenu(self.__tabsController.tabOrderKey(menuName))
        self._goToByViewAlias(viewAlias, saveHistory=False)

    def __onSwitchViewEvent(self, event):
        self.__onSwitchView(event.ctx)

    def __onSwitchView(self, ctx):
        menuName = ctx.menuName
        if menuName != self.__currentView:
            self.__soundsManager.onExitView()
            self.__currentView = menuName
            self.__soundsManager.onEnterView()
        if self.__tabsController.getCurrentTabName() != menuName:
            self.__tabsController.selectTab(menuName)
        self.__updateMenu()

    def __onDataUpdated(self, *_):
        self.__updateMenu()

    def __onVariadicDiscountsUpdated(self):
        self.__updateMenu()

    def __onAccountDataUpdated(self, key, _):
        if key == NEW_YEAR:
            self.__updateMenu()

    def __onTokensChanged(self, tokens):
        pass

    def __recreateMenu(self):
        with self.viewModel.transaction() as model:
            tabIdx = self.__getTabIdx()
            model.setStartIndexMenu(tabIdx)
            self.__tabsController.setSelectedTabIdx(tabIdx)
            self.__tabsController.createTabModels(model.getItemsMenu())

    def __updateMenu(self):
        with self.viewModel.transaction() as model:
            self.__tabsController.updateTabModels(model.getItemsMenu())
            model.setStartIndexMenu(self.__getTabIdx())

    def __getEntranceSoundEvent(self):
        return _SOUNDS_MAP.get(NewYearSoundConfigKeys.ENTRANCE_EVENT, {}).get(self.__currentView)

    def __getExitSoundEvent(self):
        return _SOUNDS_MAP.get(NewYearSoundConfigKeys.EXIT_EVENT, {}).get(self.__currentView)

    def __getSoundStateValue(self):
        return _SOUNDS_MAP.get(NewYearSoundConfigKeys.STATE_VALUE, {}).get(self.__currentView)

    def __getTabIdx(self):
        currentView = self.__currentView
        return 0 if currentView not in self.__tabsController.getEnabledTabsArray() else self.__tabsController.tabOrderKey(currentView)
