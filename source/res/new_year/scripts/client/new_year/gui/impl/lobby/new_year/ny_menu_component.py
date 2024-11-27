# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/ny_menu_component.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NEW_YEAR
from gui.impl.gen import R
from gui.shared import EVENT_BUS_SCOPE
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.ny_main_menu_model import NyMainMenuModel
from new_year.gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from new_year.gui.impl.lobby.new_year.tooltips.ny_common_tooltip import NyCommonTooltip, getCommonTooltipArgsFromEvent
from new_year.gui.impl.lobby.new_year.tooltips.ny_main_widget_tooltip import NyMainWidgetTooltip
from new_year.gui.impl.lobby.new_year.tooltips.ny_menu_machine_tooltip import NyMenuMachineTooltip
from new_year.gui.impl.lobby.new_year.widgets.ny_widget_handler import NyWidgetHandler
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates, NewYearSoundsManager
from new_year.gui.impl.new_year.views.tabs_controller import NewYearMainTabsController
from new_year.gui.shared.events import NewYearEvent
from new_year.ny_constants import NyWidgetTopMenu, ViewAliases
if typing.TYPE_CHECKING:
    from new_year.gui.impl.new_year.views.tabs_controller import TabsController
    from new_year.gui.shared.event_dispatcher import NYViewCtx
NAVIGATION_ALIAS_VIEWS = {NyWidgetTopMenu.CITY: ViewAliases.CITY_VIEW,
 NyWidgetTopMenu.QUESTS: ViewAliases.QUESTS_VIEW,
 NyWidgetTopMenu.SURPRISE_MACHINE: ViewAliases.SURPRISE_MACHINE_VIEW,
 NyWidgetTopMenu.REWARDS: ViewAliases.REWARDS_VIEW,
 NyWidgetTopMenu.PET: ViewAliases.PET_VIEW,
 NyWidgetTopMenu.INFO: ViewAliases.INFO_VIEW}
_SOUNDS_MAP = {NewYearSoundConfigKeys.ENTRANCE_EVENT: {NyWidgetTopMenu.CITY: NewYearSoundEvents.CITY,
                                         NyWidgetTopMenu.QUESTS: NewYearSoundEvents.QUESTS,
                                         NyWidgetTopMenu.SURPRISE_MACHINE: NewYearSoundEvents.SURPRISE_MACHINE,
                                         NyWidgetTopMenu.REWARDS: NewYearSoundEvents.REWARDS_LEVELS,
                                         NyWidgetTopMenu.PET: NewYearSoundEvents.PET,
                                         NyWidgetTopMenu.INFO: NewYearSoundEvents.INFO},
 NewYearSoundConfigKeys.EXIT_EVENT: {NyWidgetTopMenu.CITY: NewYearSoundEvents.CITY_EXIT,
                                     NyWidgetTopMenu.QUESTS: NewYearSoundEvents.QUESTS_EXIT,
                                     NyWidgetTopMenu.SURPRISE_MACHINE: NewYearSoundEvents.SURPRISE_MACHINE_EXIT,
                                     NyWidgetTopMenu.REWARDS: NewYearSoundEvents.REWARDS_LEVELS_EXIT,
                                     NyWidgetTopMenu.PET: NewYearSoundEvents.PET_EXIT,
                                     NyWidgetTopMenu.INFO: NewYearSoundEvents.INFO_EXIT},
 NewYearSoundConfigKeys.STATE_VALUE: {NyWidgetTopMenu.CITY: NewYearSoundStates.CITY,
                                      NyWidgetTopMenu.QUESTS: NewYearSoundStates.QUEST,
                                      NyWidgetTopMenu.SURPRISE_MACHINE: NewYearSoundStates.TOYS,
                                      NyWidgetTopMenu.REWARDS: NewYearSoundStates.REWARDS_LEVELS,
                                      NyWidgetTopMenu.PET: NewYearSoundStates.CELEB,
                                      NyWidgetTopMenu.INFO: NewYearSoundStates.INFO}}
_3D_OBJECTS = {ViewAliases.CITY_VIEW, ViewAliases.SURPRISE_MACHINE_VIEW, ViewAliases.PET_VIEW}

class NYMainMenu(HistorySubModelPresenter):

    def __init__(self, viewModel, parentView, *args, **kwargs):
        super(NYMainMenu, self).__init__(viewModel, parentView, *args, **kwargs)
        self.__tabsController = NewYearMainTabsController()
        self.__soundsManager = None
        self.__currentView = None
        self.__wigetHandler = NyWidgetHandler(self.viewModel.widget)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        tooltips = R.views.new_year.lobby.new_year.tooltips
        if contentID == tooltips.CommonTooltip():
            return NyCommonTooltip(*getCommonTooltipArgsFromEvent(event))
        if contentID == tooltips.NyMainWidgetTooltip():
            return NyMainWidgetTooltip()
        return NyMenuMachineTooltip() if contentID == tooltips.MenuMachineTooltip() else super(NYMainMenu, self).createToolTipContent(event, contentID)

    def initialize(self, *args, **kwargs):
        super(NYMainMenu, self).initialize(*args, **kwargs)
        soundConfig = {NewYearSoundConfigKeys.ENTRANCE_EVENT: self.__getEntranceSoundEvent,
         NewYearSoundConfigKeys.EXIT_EVENT: self.__getExitSoundEvent,
         NewYearSoundConfigKeys.STATE_VALUE: self.__getSoundStateValue}
        self.__soundsManager = NewYearSoundsManager(soundConfig)
        self.viewModel.setIsExtendedAnim(True)
        self.__wigetHandler.initialize()

    def finalize(self):
        self.__soundsManager.onExitView()
        self.__soundsManager.clear()
        self.__soundsManager = None
        self.__currentView = None
        self.__wigetHandler.finalize()
        super(NYMainMenu, self).finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onInfoBtnClick, self.__onInfoBtnClick),
         (self.viewModel.onSwitchContent, self.__onMenuItemSelected),
         (self._nyController.onDataUpdated, self.__onDataUpdated),
         (self._nyController.onVariadicDiscountsUpdated, self.__onVariadicDiscountsUpdated),
         (AccountSettings.onSettingsChanging, self.__onAccountDataUpdated),
         (self._bubbleNavigationController.onUpdateBubble, self.__onUpdateBubble),
         (self._nyController.onNySettingsChanged, self.__onNySettingsChanged))

    def _getListeners(self):
        return ((NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchViewEvent, EVENT_BUS_SCOPE.LOBBY),)

    def _getCallbacks(self):
        return (('tokens', self.__onTokensChanged),)

    def __onInfoBtnClick(self):
        NewYearNavigation.showInfoView(showDefaultTabForced=True)

    def __onMenuItemSelected(self, args):
        menuName = args['view']
        viewAlias = NAVIGATION_ALIAS_VIEWS[menuName]
        self._navigationHistory.clear()
        with self.viewModel.transaction() as tx:
            tx.setStartIndexMenu(self.__tabsController.tabOrderKey(menuName))
        instantly = not self.__checkIfShowFlight(viewAlias)
        self._goToByViewAlias(viewAlias, None, instantly, saveHistory=False)
        return

    def __checkIfShowFlight(self, viewAlias):
        prevAlias = NewYearNavigation.getCurrentViewName()
        return viewAlias in _3D_OBJECTS and prevAlias in _3D_OBJECTS

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

    def __onUpdateBubble(self):
        self.__updateMenu()

    def __onDataUpdated(self, *_):
        self.__updateMenu()
        self.__wigetHandler.update()

    def __onVariadicDiscountsUpdated(self):
        self.__updateMenu()

    def __onAccountDataUpdated(self, key, _):
        if key == NEW_YEAR:
            self.__updateMenu()

    def __onTokensChanged(self, tokens):
        pass

    def __onNySettingsChanged(self):
        self.__updateMenu()

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
