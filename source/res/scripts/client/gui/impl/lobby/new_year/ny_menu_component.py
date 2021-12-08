# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/ny_menu_component.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_CELEBRITY_QUESTS_VISITED_MASK, NY_OLD_COLLECTIONS_BY_YEAR_VISITED, NY_OLD_REWARDS_BY_YEAR_VISITED
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from gifts.gifts_common import GiftEventID
from gui.gift_system.constants import HubUpdateReason
from gui.gift_system.mixins import GiftEventHubWatcher
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_main_menu_model import NyMainMenuModel
from gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from gui.impl.lobby.new_year.tooltips.ny_menu_collections_tooltip import NyMenuCollectionsTooltip
from gui.impl.lobby.new_year.tooltips.ny_menu_gift_tooltip import NyMenuGiftTooltip
from gui.impl.lobby.new_year.tooltips.ny_menu_shards_tooltip import NyMenuShardsTooltip
from gui.impl.new_year.navigation import ViewAliases, NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates, NewYearSoundsManager
from gui.impl.new_year.views.tabs_controller import NewYearMainTabsController
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import isMemoryRiskySystem, dependency
from items.components.ny_constants import CelebrityQuestTokenParts
from new_year.ny_constants import NyWidgetTopMenu
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.new_year import ICelebritySceneController
from uilogging.ny.loggers import NyWidgetTopMenuLogger, NyTopMenuFlowLogger
if typing.TYPE_CHECKING:
    from gui.impl.new_year.views.tabs_controller import TabsController
    from gui.shared.event_dispatcher import NYViewCtx
_NAVIGATION_ALIAS_VIEWS = {NyWidgetTopMenu.GLADE: ViewAliases.GLADE_VIEW,
 NyWidgetTopMenu.DECORATIONS: ViewAliases.CRAFT_VIEW,
 NyWidgetTopMenu.COLLECTIONS: ViewAliases.ALBUM_VIEW,
 NyWidgetTopMenu.REWARDS: ViewAliases.REWARDS_VIEW,
 NyWidgetTopMenu.SHARDS: ViewAliases.BREAK_VIEW,
 NyWidgetTopMenu.GIFT_SYSTEM: ViewAliases.GIFT_SYSTEM_VIEW,
 NyWidgetTopMenu.VEHICLES: ViewAliases.VEHICLES_VIEW,
 NyWidgetTopMenu.CHALLENGE: ViewAliases.CELEBRITY_VIEW}
_SOUNDS_MAP = {NewYearSoundConfigKeys.ENTRANCE_EVENT: {NyWidgetTopMenu.GLADE: NewYearSoundEvents.GLADE,
                                         NyWidgetTopMenu.DECORATIONS: NewYearSoundEvents.TOYS,
                                         NyWidgetTopMenu.COLLECTIONS: NewYearSoundEvents.ALBUM_SELECT,
                                         NyWidgetTopMenu.INFO: NewYearSoundEvents.INFO,
                                         NyWidgetTopMenu.REWARDS: NewYearSoundEvents.REWARDS_LEVELS,
                                         NyWidgetTopMenu.SHARDS: NewYearSoundEvents.DEBRIS,
                                         NyWidgetTopMenu.CHALLENGE: NewYearSoundEvents.CELEBRITY,
                                         NyWidgetTopMenu.GIFT_SYSTEM: NewYearSoundEvents.GIFT_SYSTEM},
 NewYearSoundConfigKeys.EXIT_EVENT: {NyWidgetTopMenu.GLADE: NewYearSoundEvents.GLADE_EXIT,
                                     NyWidgetTopMenu.DECORATIONS: NewYearSoundEvents.TOYS_EXIT,
                                     NyWidgetTopMenu.COLLECTIONS: NewYearSoundEvents.ALBUM_SELECT_EXIT,
                                     NyWidgetTopMenu.INFO: NewYearSoundEvents.INFO_EXIT,
                                     NyWidgetTopMenu.REWARDS: NewYearSoundEvents.REWARDS_LEVELS_EXIT,
                                     NyWidgetTopMenu.SHARDS: NewYearSoundEvents.DEBRIS_EXIT,
                                     NyWidgetTopMenu.CHALLENGE: NewYearSoundEvents.CELEBRITY_EXIT,
                                     NyWidgetTopMenu.GIFT_SYSTEM: NewYearSoundEvents.GIFT_SYSTEM_EXIT},
 NewYearSoundConfigKeys.STATE_VALUE: {NyWidgetTopMenu.DECORATIONS: NewYearSoundStates.TOYS,
                                      NyWidgetTopMenu.COLLECTIONS: NewYearSoundStates.ALBUM_SELECT,
                                      NyWidgetTopMenu.INFO: NewYearSoundStates.INFO,
                                      NyWidgetTopMenu.SHARDS: NewYearSoundStates.DEBRIS,
                                      NyWidgetTopMenu.GIFT_SYSTEM: NewYearSoundStates.GIFT_SYSTEM,
                                      NyWidgetTopMenu.VEHICLES: NewYearSoundStates.VEHICLES,
                                      NyWidgetTopMenu.CHALLENGE: NewYearSoundStates.CELEBRITY}}

class NYMainMenu(HistorySubModelPresenter, GiftEventHubWatcher):
    _GIFT_EVENT_ID = GiftEventID.NY_HOLIDAYS
    __celebrityController = dependency.descriptor(ICelebritySceneController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __topMenuLogger = NyWidgetTopMenuLogger()
    __flowLogger = NyTopMenuFlowLogger()

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
        if event.contentID == tooltips.NyMenuGiftTooltip():
            return NyMenuGiftTooltip()
        if contentID == tooltips.NyMenuShardsTooltip():
            return NyMenuShardsTooltip()
        return NyMenuCollectionsTooltip() if contentID == tooltips.NyMenuCollectionsTooltip() else super(NYMainMenu, self).createToolTipContent(event, contentID)

    def initialize(self, *args, **kwargs):
        super(NYMainMenu, self).initialize(*args, **kwargs)
        self.catchGiftEventHub()
        soundConfig = {NewYearSoundConfigKeys.ENTRANCE_EVENT: self.__getEntranceSoundEvent,
         NewYearSoundConfigKeys.EXIT_EVENT: self.__getExitSoundEvent,
         NewYearSoundConfigKeys.STATE_VALUE: self.__getSoundStateValue}
        self.__soundsManager = NewYearSoundsManager(soundConfig)
        self.viewModel.setIsExtendedAnim(not isMemoryRiskySystem())

    def finalize(self):
        self.__soundsManager.onExitView()
        self.__soundsManager.clear()
        self.__soundsManager = None
        self.__currentView = None
        self.releaseGiftEventHub()
        super(NYMainMenu, self).finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onInfoBtnClick, self.__onInfoBtnClick),
         (self.viewModel.onSwitchContent, self.__onMenuItemSelected),
         (self._nyController.onDataUpdated, self.__onDataUpdated),
         (self.__celebrityController.onQuestsUpdated, self.__onDataUpdated),
         (AccountSettings.onSettingsChanging, self.__onAccountDataUpdated),
         (self.__settingsCore.onSettingsChanged, self.__onSettingsChanged))

    def _getListeners(self):
        return ((events.NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchViewEvent, EVENT_BUS_SCOPE.LOBBY),)

    def _getCallbacks(self):
        return (('tokens', self.__onTokensChanged),)

    def _onGiftHubUpdate(self, reason, _=None):
        if reason == HubUpdateReason.SETTINGS:
            self.__recreateMenu()
        elif reason == HubUpdateReason.STAMPER_UPDATE:
            self.__updateMenu()

    def __onInfoBtnClick(self):
        self.__flowLogger.logInfoClick(source=self.__currentView, albumTab=self._tabCache.getCurrentYear(), rewardTab=self._tabCache.getRewardsTab(), selectedObject=NewYearNavigation.getCurrentObject())
        NewYearNavigation.showInfoView(showDefaultTabForced=True)

    def __onMenuItemSelected(self, args):
        menuName = args['view']
        viewAlias = _NAVIGATION_ALIAS_VIEWS[menuName]
        self._navigationHistory.clear()
        self.__topMenuLogger.logClick(menuName)
        self.__flowLogger.logTabSelect(source=self.__currentView, view=menuName, albumTab=self._tabCache.getCurrentYear(), rewardTab=self._tabCache.getRewardsTab(), selectedObject=NewYearNavigation.getCurrentObject(), previousObject=NewYearNavigation.getPreviousObject())
        with self.viewModel.transaction() as tx:
            tx.setStartIndexMenu(self.__tabsController.tabOrderKey(menuName))
        self.__soundsManager.playEvent(NewYearSoundEvents.TAB_BAR_CLICK)
        self._goToByViewAlias(viewAlias, saveHistory=False)

    def __onSwitchViewEvent(self, event):
        self.__onSwitchView(event.ctx)

    def __onSwitchView(self, ctx):
        menuName = ctx.menuName
        if menuName != self.__currentView:
            self.__soundsManager.onExitView()
            self.__currentView = menuName
            self.__soundsManager.onEnterView()
        if menuName != NyWidgetTopMenu.INFO and self.__tabsController.getCurrentTabName() != menuName:
            self.__tabsController.selectTab(menuName)
        self.__updateMenu()

    def __onDataUpdated(self, *_):
        self.__updateMenu()

    def __onAccountDataUpdated(self, key, _):
        if key in (NY_CELEBRITY_QUESTS_VISITED_MASK, NY_OLD_COLLECTIONS_BY_YEAR_VISITED, NY_OLD_REWARDS_BY_YEAR_VISITED):
            self.__updateMenu()

    def __onSettingsChanged(self, diff):
        if NewYearStorageKeys.CELEBRITY_CHALLENGE_VISITED in diff:
            self.__updateMenu()

    def __onTokensChanged(self, tokens):
        if any((token.startswith(CelebrityQuestTokenParts.PREFIX) for token in tokens)):
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
        if currentView == NyWidgetTopMenu.INFO:
            return -1
        return 0 if currentView not in self.__tabsController.getEnabledTabsArray() else self.__tabsController.tabOrderKey(currentView)
