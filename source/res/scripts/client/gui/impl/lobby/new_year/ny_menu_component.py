# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/ny_menu_component.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_CELEBRITY_DAY_QUESTS_VISITED_MASK, NY_OLD_COLLECTIONS_BY_YEAR_VISITED, NY_OLD_REWARDS_BY_YEAR_VISITED, NY_GIFT_MACHINE_BUY_TOKEN_VISITED, NY_DOG_PAGE_VISITED, NY_NARKET_PLACE_PAGE_VISITED, NY_CAT_PAGE_VISITED
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resources_balance_model import CollectState
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_resource_collector_tooltip_model import CollectorTooltipType
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_main_menu_model import NyMainMenuModel
from gui.impl.lobby.new_year.ny_history_presenter import NyHistoryPresenter
from gui.impl.lobby.new_year.popovers.ny_resources_convert_popover import NyResourcesConvertPopover
from gui.impl.lobby.new_year.tooltips.ny_menu_gift_tooltip import NyMenuGiftTooltip
from gui.impl.lobby.new_year.tooltips.ny_resource_collector_tooltip import NyResourceCollectorTooltip
from gui.impl.lobby.new_year.tooltips.ny_resource_tooltip import NyResourceTooltip
from gui.impl.lobby.new_year.widgets.ny_main_widget import WidgetLevelProgressHelper, WidgetFriendStatusHelper
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates, NewYearSoundsManager
from gui.impl.new_year.views.tabs_controller import NewYearMainTabsController
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import NyResourcesEvent
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency
from items.components.ny_constants import CelebrityQuestTokenParts, NyCurrency
from new_year.ny_constants import AdditionalCameraObject, NyWidgetTopMenu, RESOURCES_ORDER
from new_year.ny_resource_collecting_helper import getCollectingCooldownTime, isManualCollectingAvailable
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IWalletController
from skeletons.gui.impl import IGuiLoader
from skeletons.new_year import ICelebritySceneController, IFriendServiceController
from uilogging.ny.loggers import NyTopMenuFlowLogger, NyWidgetTopMenuLogger, NyResourcesLogger
if typing.TYPE_CHECKING:
    from gui.shared.event_dispatcher import NYViewCtx
_NAVIGATION_ALIAS_VIEWS = {NyWidgetTopMenu.GLADE: ViewAliases.GLADE_VIEW,
 NyWidgetTopMenu.MARKETPLACE: ViewAliases.MARKETPLACE_VIEW,
 NyWidgetTopMenu.REWARDS: ViewAliases.REWARDS_VIEW,
 NyWidgetTopMenu.GIFT_MACHINE: ViewAliases.GIFT_MACHINE,
 NyWidgetTopMenu.FRIENDS: ViewAliases.FRIENDS_VIEW,
 NyWidgetTopMenu.CHALLENGE: ViewAliases.CELEBRITY_VIEW,
 NyWidgetTopMenu.INFO: ViewAliases.INFO_VIEW,
 NyWidgetTopMenu.FRIEND_INFO: ViewAliases.FRIEND_INFO_VIEW,
 NyWidgetTopMenu.FRIEND_GLADE: ViewAliases.FRIEND_GLADE_VIEW,
 NyWidgetTopMenu.FRIEND_CHALLENGE: ViewAliases.FRIEND_CELEBRITY_VIEW}
_SOUNDS_MAP = {NewYearSoundConfigKeys.ENTRANCE_EVENT: {NyWidgetTopMenu.GLADE: NewYearSoundEvents.GLADE,
                                         NyWidgetTopMenu.INFO: NewYearSoundEvents.INFO,
                                         NyWidgetTopMenu.FRIEND_INFO: NewYearSoundEvents.INFO,
                                         NyWidgetTopMenu.REWARDS: NewYearSoundEvents.REWARDS_LEVELS,
                                         NyWidgetTopMenu.GIFT_MACHINE: NewYearSoundEvents.TOYS,
                                         NyWidgetTopMenu.CHALLENGE: NewYearSoundEvents.CELEBRITY,
                                         NyWidgetTopMenu.FRIENDS: NewYearSoundEvents.FRIENDS},
 NewYearSoundConfigKeys.EXIT_EVENT: {NyWidgetTopMenu.GLADE: NewYearSoundEvents.GLADE_EXIT,
                                     NyWidgetTopMenu.MARKETPLACE: NewYearSoundEvents.MARKETPLACE_EXIT,
                                     NyWidgetTopMenu.INFO: NewYearSoundEvents.INFO_EXIT,
                                     NyWidgetTopMenu.FRIEND_INFO: NewYearSoundEvents.INFO_EXIT,
                                     NyWidgetTopMenu.REWARDS: NewYearSoundEvents.REWARDS_LEVELS_EXIT,
                                     NyWidgetTopMenu.GIFT_MACHINE: NewYearSoundEvents.TOYS_EXIT,
                                     NyWidgetTopMenu.CHALLENGE: NewYearSoundEvents.CELEBRITY_EXIT,
                                     NyWidgetTopMenu.FRIENDS: NewYearSoundEvents.FRIENDS_EXIT},
 NewYearSoundConfigKeys.STATE_VALUE: {NyWidgetTopMenu.MARKETPLACE: NewYearSoundStates.MARKETPLACE,
                                      NyWidgetTopMenu.INFO: NewYearSoundStates.INFO,
                                      NyWidgetTopMenu.FRIEND_INFO: NewYearSoundStates.INFO,
                                      NyWidgetTopMenu.GIFT_MACHINE: NewYearSoundStates.TOYS,
                                      NyWidgetTopMenu.FRIENDS: NewYearSoundStates.FRIENDS,
                                      NyWidgetTopMenu.CHALLENGE: NewYearSoundStates.CELEBRITY}}

class NYMainMenu(NyHistoryPresenter):
    __slots__ = ('__tabsController', '__soundsManager', '__currentView', '__widgetHelper', '__widgetFriendHelper', '__lockForCustomAnimation', '__notifier')
    __celebrityController = dependency.descriptor(ICelebritySceneController)
    __friendsService = dependency.descriptor(IFriendServiceController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __guiLoader = dependency.descriptor(IGuiLoader)
    __wallet = dependency.descriptor(IWalletController)
    __topMenuLogger = NyWidgetTopMenuLogger()
    __flowLogger = NyTopMenuFlowLogger()

    def __init__(self, viewModel, parentView, *args, **kwargs):
        super(NYMainMenu, self).__init__(viewModel, parentView, *args, **kwargs)
        self.__tabsController = NewYearMainTabsController()
        self.__soundsManager = None
        self.__currentView = None
        self.__widgetHelper = None
        self.__widgetFriendHelper = None
        self.__lockForCustomAnimation = False
        self.__notifier = None
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        tooltips = R.views.lobby.new_year.tooltips
        if contentID == tooltips.NyMenuGiftTooltip():
            return NyMenuGiftTooltip()
        if contentID == tooltips.NyResourceTooltip():
            resourceType = event.getArgument('type')
            return NyResourceTooltip(resourceType)
        if contentID == R.views.lobby.new_year.tooltips.NyResourceCollectorTooltip():
            collectorTooltipType = CollectorTooltipType(event.getArgument('type'))
            return NyResourceCollectorTooltip(collectorTooltipType)
        if self.__widgetHelper:
            content = self.__widgetHelper.createToolTipContent(event, contentID)
            if content:
                return content
        return super(NYMainMenu, self).createToolTipContent(event, contentID)

    def createPopOverContent(self, event):
        return NyResourcesConvertPopover() if event.contentID == R.views.lobby.new_year.popovers.NyResourcesConvertPopover() else super(NYMainMenu, self).createPopOverContent(event)

    def initialize(self, *args, **kwargs):
        super(NYMainMenu, self).initialize(*args, **kwargs)
        self.__widgetHelper = WidgetLevelProgressHelper(self.viewModel.widgetLevelProgress)
        self.__widgetHelper.initialize()
        self.__widgetFriendHelper = WidgetFriendStatusHelper(self.viewModel.widgetFriendStatus)
        self.__widgetFriendHelper.initialize()
        self.__notifier = SimpleNotifier(getCollectingCooldownTime, self.__updateCollecting)
        soundConfig = {NewYearSoundConfigKeys.ENTRANCE_EVENT: self.__getEntranceSoundEvent,
         NewYearSoundConfigKeys.EXIT_EVENT: self.__getExitSoundEvent,
         NewYearSoundConfigKeys.STATE_VALUE: self.__getSoundStateValue}
        self.__soundsManager = NewYearSoundsManager(soundConfig)

    def finalize(self):
        self.__soundsManager.onExitView()
        self.__soundsManager.clear()
        self.__soundsManager = None
        self.__widgetHelper.clear()
        self.__widgetHelper = None
        self.__widgetFriendHelper.clear()
        self.__widgetFriendHelper = None
        self.__notifier.stopNotification()
        self.__notifier.clear()
        self.__currentView = None
        super(NYMainMenu, self).finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onSwitchContent, self.__onMenuItemSelected),
         (self._nyController.currencies.onBalanceUpdated, self.__onBalanceUpdated),
         (self.viewModel.balance.onCollectResources, self.__onCollectResources),
         (self.viewModel.balance.onConvertResources, self.__onConvertResources),
         (self.viewModel.balance.onGoToResources, self.__onGoToResources),
         (self.viewModel.onGoToFriendsList, self.__onGoToFriendsView),
         (self._nyController.onDataUpdated, self.__onDataUpdated),
         (self._nyController.currencies.onNyCoinsUpdate, self.__onNyCoinsUpdate),
         (self.__celebrityController.onQuestsUpdated, self.__onDataUpdated),
         (self._friendsService.onFriendServiceStateChanged, self.__onDataUpdated),
         (AccountSettings.onSettingsChanging, self.__onAccountDataUpdated),
         (self.__settingsCore.onSettingsChanged, self.__onSettingsChanged),
         (NewYearNavigation.onSwitchView, self.__onSwitchViewEvent),
         (NewYearNavigation.onObjectStateChanged, self.__onObjectStateChanged),
         (self._nyController.resourceCollecting.onCollectingUpdateLock, self.__onCollectingUpdateLock),
         (self._nyController.resourceCollecting.onCollectingUpdateResource, self.__onCollectingUpdateResource))

    def _getCallbacks(self):
        return (('tokens', self.__onTokensChanged),)

    def _getListeners(self):
        return ((NyResourcesEvent.RESOURCE_COLLECTED, self.__onResourceCollected, EVENT_BUS_SCOPE.LOBBY),)

    def __onCollectResources(self):
        if self.__isResourcesTabOpened:
            return
        logger = NyResourcesLogger()
        if self.viewModel.balance.getCollectState() == CollectState.AUTOCOLLECT:
            logger.logAutoCollectMenuClick()
        logger.logMenuClick('button')
        self.__friendsService.leaveFriendHangar()
        NewYearNavigation.switchTo(AdditionalCameraObject.RESOURCES, False, withFade=False)

    def __onConvertResources(self):
        pass

    def __onGoToResources(self):
        self.__onCollectResources()

    def __onMenuItemSelected(self, args):
        menuName = args['view']
        viewAlias = _NAVIGATION_ALIAS_VIEWS[menuName]
        self._historyManager.clear()
        self.__topMenuLogger.logClick(menuName)
        self.__flowLogger.logTabSelect(source=self.__currentView, view=menuName, selectedObject=NewYearNavigation.getCurrentObject(), previousObject=NewYearNavigation.getPreviousObject())
        with self.viewModel.transaction() as tx:
            tx.setStartIndexMenu(self.__tabsController.tabOrderKey(menuName))
        self.__soundsManager.playEvent(NewYearSoundEvents.TAB_BAR_CLICK)
        self._goToByViewAlias(viewAlias, saveHistory=False, doAutoRouting=True)

    def __onGoToFriendsView(self):
        leaveService = self.__currentView in NyWidgetTopMenu.ALL_FRIEND_HANGAR
        self._goToFriendsView(leaveService)

    def __onSwitchViewEvent(self, ctx):
        self.__onSwitchView(ctx)

    def __onSwitchView(self, ctx):
        menuName = ctx.menuName
        if menuName != self.__currentView:
            self.__soundsManager.onExitView()
            wasInFriendHangar = self.__currentView in NyWidgetTopMenu.ALL_FRIEND_HANGAR
            toFriendHangar = menuName in NyWidgetTopMenu.ALL_FRIEND_HANGAR
            if wasInFriendHangar and not toFriendHangar or not wasInFriendHangar and not toFriendHangar and self._friendsService.friendHangarSpaId:
                self._friendsService.leaveFriendHangar()
            self.__currentView = menuName
            self.__soundsManager.onEnterView()
        isHangarSwitch = self.__needHangarSwitch(menuName)
        if isHangarSwitch:
            isFriendHangar = not self.__tabsController.getIsFriendHangar()
            self.__tabsController.updateIsFriendHangar(isFriendHangar)
            self.viewModel.setIsFriendHangar(isFriendHangar)
            self.__recreateMenu()
        elif self.__tabsController.getCurrentTabName() != menuName:
            self.__tabsController.selectTab(menuName)
        self.__updateMenu()

    def __needHangarSwitch(self, menuName):
        return menuName in NyWidgetTopMenu.ALL_PLAYER_HANGAR if self.__tabsController.getIsFriendHangar() else menuName in NyWidgetTopMenu.ALL_FRIEND_HANGAR

    def __onDataUpdated(self, *_):
        self.__updateMenu()

    def __onNyCoinsUpdate(self):
        self.__tryToDestroyTooltip((R.views.lobby.new_year.tooltips.NyMenuGiftTooltip(),))
        self.__updateMenu()

    def __onObjectStateChanged(self):
        if self.viewModel is None:
            return
        else:
            self.viewModel.balance.setIsResourcesTabOpen(NewYearNavigation.getCurrentObject() == AdditionalCameraObject.RESOURCES)
            return

    def __onAccountDataUpdated(self, key, _):
        if key in (NY_CELEBRITY_DAY_QUESTS_VISITED_MASK,
         NY_OLD_COLLECTIONS_BY_YEAR_VISITED,
         NY_OLD_REWARDS_BY_YEAR_VISITED,
         NY_GIFT_MACHINE_BUY_TOKEN_VISITED,
         NY_DOG_PAGE_VISITED,
         NY_NARKET_PLACE_PAGE_VISITED,
         NY_CAT_PAGE_VISITED):
            self.__updateMenu()

    def __onSettingsChanged(self, diff):
        if NewYearStorageKeys.CELEBRITY_SCREEN_VISITED in diff:
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
            balance = model.balance
            balance.setIsResourcesTabOpen(self.__isResourcesTabOpened)
            self.__updateCollecting(model=model)
        self.__updateResources()

    @replaceNoneKwargsModel
    def __updateCollecting(self, model=None):
        isAutoCollectingActivated, _, _ = self._itemsCache.items.festivity.getResourceCollecting()
        isManualAvailable = isManualCollectingAvailable()
        if isAutoCollectingActivated:
            state = CollectState.AUTOCOLLECT
        elif isManualAvailable:
            state = CollectState.AVAILABLE
        else:
            state = CollectState.COLLECTED
        cooldown = getCollectingCooldownTime()
        balance = model.balance
        balance.setCollectState(state)
        balance.setCollectCooldown(cooldown)
        if cooldown > 0:
            self.__notifier.startNotification()
        else:
            self.__notifier.stopNotification()

    def __updateResources(self):
        if self.__lockForCustomAnimation:
            return
        with self.viewModel.transaction() as model:
            model.balance.setIsWalletAvailable(self.__wallet.isAvailable)
            resources = model.balance.getResources()
            resources.clear()
            for resource in RESOURCES_ORDER:
                amount = self._nyController.currencies.getResouceBalance(resource.value)
                resourceModel = NyResourceModel()
                resourceModel.setType(resource.value)
                resourceModel.setValue(amount)
                resources.addViewModel(resourceModel)

            resources.invalidate()

    def __updateResource(self, resourceID):
        if not self.__lockForCustomAnimation or resourceID not in NyCurrency.ALL:
            return
        with self.viewModel.transaction() as model:
            resources = model.balance.getResources()
            for resourceModel in resources:
                if resourceModel.getType() == resourceID:
                    amount = self._nyController.currencies.getResouceBalance(resourceID)
                    resourceModel.setValue(amount)

            resources.invalidate()

    def __onCollectingUpdateResource(self, resourceID):
        self.__updateResource(resourceID)

    def __onCollectingUpdateLock(self, enable):
        self.__lockForCustomAnimation = enable
        if enable is False:
            self.__updateResources()

    def __onResourceCollected(self, event):
        resource = event.ctx.get('resource')
        if resource is None:
            return
        else:
            with self.viewModel.transaction() as model:
                resources = model.balance.getResources()
                resourceModel = findFirst(lambda r: r.getType() == resource.value, resources)
                if resourceModel is not None:
                    amount = self._nyController.currencies.getResouceBalance(resource.value)
                    resourceModel.setValue(amount)
                    resources.invalidate()
            return

    def __getEntranceSoundEvent(self):
        return _SOUNDS_MAP.get(NewYearSoundConfigKeys.ENTRANCE_EVENT, {}).get(self.__currentView)

    def __getExitSoundEvent(self):
        return _SOUNDS_MAP.get(NewYearSoundConfigKeys.EXIT_EVENT, {}).get(self.__currentView)

    def __getSoundStateValue(self):
        return None if self.__friendsService.friendHangarSpaId is not None else _SOUNDS_MAP.get(NewYearSoundConfigKeys.STATE_VALUE, {}).get(self.__currentView)

    def __getTabIdx(self):
        currentView = self.__currentView
        return 0 if currentView not in self.__tabsController.tabs else self.__tabsController.tabOrderKey(currentView)

    @property
    def __isResourcesTabOpened(self):
        return self.__currentView == NyWidgetTopMenu.GLADE and NewYearNavigation.getCurrentObject() == AdditionalCameraObject.RESOURCES

    def __onBalanceUpdated(self):
        self.__updateResources()

    def __tryToDestroyTooltip(self, tooltipIDs):
        for tooltipID in tooltipIDs:
            tooltipView = self.__guiLoader.windowsManager.getViewByLayoutID(tooltipID)
            if tooltipView:
                tooltipView.destroyWindow()
