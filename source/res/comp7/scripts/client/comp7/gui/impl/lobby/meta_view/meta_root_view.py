# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/meta_view/meta_root_view.py
import logging
import typing
from shared_utils import findFirst
from comp7.gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as COMP7_TOOLTIPS
from comp7.gui.game_control.comp7_shop_controller import ShopControllerStatus
from comp7.gui.impl.gen.view_models.views.lobby.enums import MetaRootViews
from comp7.gui.impl.gen.view_models.views.lobby.enums import SeasonName
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.root_view_model import RootViewModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.tab_model import TabModel
from comp7.gui.impl.gen.view_models.views.lobby.season_model import SeasonState
from comp7.gui.impl.gen.view_models.views.lobby.year_model import YearState
from comp7.gui.impl.lobby.comp7_helpers.comp7_lobby_sounds import getComp7MetaSoundSpace, playComp7MetaViewTabSound
from comp7.gui.impl.lobby.meta_view.pages.leaderboard_page import LeaderboardPage
from comp7.gui.impl.lobby.meta_view.pages.progression_page import ProgressionPage
from comp7.gui.impl.lobby.meta_view.pages.rank_rewards_page import RankRewardsPage
from comp7.gui.impl.lobby.meta_view.pages.shop_page import ShopPage
from comp7.gui.impl.lobby.meta_view.pages.weekly_quests_page import WeeklyQuestsPage
from comp7.gui.impl.lobby.meta_view.pages.yearly_rewards_page import YearlyRewardsPage
from comp7.gui.impl.lobby.meta_view.pages.yearly_statistics_page import YearlyStatisticsPage
from comp7.gui.impl.lobby.meta_view.products_helper import hasUnseenProduct
from comp7.gui.selectable_reward.common import Comp7SelectableRewardManager
from comp7.gui.shared.event_dispatcher import showComp7AllRewardsSelectionWindow, showComp7MetaRootTab
from comp7.skeletons.gui.game_control import IComp7ShopController
from comp7_core.gui.impl.lobby.comp7_core_helpers import comp7_core_model_helpers
from frameworks.state_machine import BaseStateObserver, visitor
from frameworks.wulf import ViewFlags, ViewSettings, ViewStatus
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_tooltip import createTooltipData
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.pub import ViewImpl
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.offers import IOffersDataProvider
if typing.TYPE_CHECKING:
    from comp7.gui.impl.lobby.meta_view.pages import PageSubModelPresenter
    from comp7.gui.impl.lobby.hangar.meta_tab_state import IMetaTabState
    from gui.offers import OffersDataProvider
    from gui.shared.events import NavigationEvent
    from frameworks.state_machine import State
_logger = logging.getLogger(__name__)

class MetaRootView(ViewImpl, BaseStateObserver):
    __slots__ = ('__pages', '__tabId', '__products', '__onLoadingParams')
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __comp7ShopController = dependency.descriptor(IComp7ShopController)
    __guiLoader = dependency.descriptor(IGuiLoader)
    __offersProvider = dependency.descriptor(IOffersDataProvider)
    _COMMON_SOUND_SPACE = getComp7MetaSoundSpace()

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = RootViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(MetaRootView, self).__init__(settings)
        self.__pages = {}
        self.__tabId = None
        self.__products = None
        self.__onLoadingParams = None
        self.__initPages()
        return

    @property
    def viewModel(self):
        return super(MetaRootView, self).getViewModel()

    @property
    def tabId(self):
        return self.__tabId

    def getPageById(self, tabId):
        return self.__pages.get(tabId)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == COMP7_TOOLTIPS.COMP7_CALENDAR_DAY_INFO:
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(None,))
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        if self.__currentPage.isLoaded:
            window = self.__currentPage.createToolTip(event)
            if window is not None:
                return window
        return super(MetaRootView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if self.__currentPage.isLoaded:
            content = self.__currentPage.createToolTipContent(event, contentID)
            if content is not None:
                return content
        return super(MetaRootView, self).createToolTipContent(event, contentID)

    def createContextMenu(self, event):
        if self.__currentPage is not None and self.__currentPage.isLoaded:
            window = self.__currentPage.createContextMenu(event)
            if window is not None:
                return window
        return super(MetaRootView, self).createContextMenu(event)

    def switchPage(self, tabId, **params):
        if self.__currentPage is not None and self.__currentPage.isLoaded:
            self.__currentPage.finalize()
        page = self.__pages[tabId]
        page.initialize(**params)
        self.viewModel.setPageViewId(page.pageId)
        playComp7MetaViewTabSound(tabId, self.__tabId)
        self.__tabId = tabId
        g_eventDispatcher.updateUI()
        return

    def updateTabNotifications(self):
        shopTab = findFirst(lambda tab: tab.getId() == MetaRootViews.SHOP, self.viewModel.sidebar.getItems())
        if self.__products:
            shopTab.setHasNotification(hasUnseenProduct(self.__products))
        else:
            shopTab.setHasNotification(False)

    def isObservingState(self, state):
        from comp7.gui.impl.lobby.hangar.states import Comp7MetaState
        lsm = getLobbyStateMachine()
        return visitor.isDescendantOf(state, lsm.getStateByCls(Comp7MetaState)) if lsm is not None else False

    def onEnterState(self, state, event):
        params = self.__onLoadingParams or {}
        if event is not None:
            params.update(event.params)
        self.switchPage(state.tabId, **params)
        self.__onLoadingParams = None
        return

    def _finalize(self):
        lsm = getLobbyStateMachine()
        if lsm is not None:
            lsm.disconnect(self)
        self.__removeListeners()
        self.__clearPages()
        self.__products = None
        self.__onLoadingParams = None
        return

    def _onLoading(self, *args, **kwargs):
        self.__onLoadingParams = kwargs
        lsm = getLobbyStateMachine()
        if lsm is not None:
            lsm.connect(self)
        else:
            _logger.error('Lobby state machine is None when MetaRootView is loading')
        self.__updateTabs()
        self.__products = self.__comp7ShopController.getProducts()
        self.updateTabNotifications()
        comp7_core_model_helpers.setScheduleInfo(self.viewModel.scheduleInfo, self.__comp7Controller, COMP7_TOOLTIPS.COMP7_CALENDAR_DAY_INFO, SeasonState, YearState, SeasonName)
        self.__updateWeeklyQuestsClaimRewardsModel()
        self.__addListeners()
        return

    @property
    def __currentPage(self):
        return self.__pages[self.__tabId] if self.__pages and self.__tabId is not None else None

    def __addListeners(self):
        self.viewModel.onClose += self.__onClose
        self.viewModel.sidebar.onSideBarTabChange += self.__onSideBarTabChanged
        self.viewModel.scheduleInfo.season.pollServerTime += self.__onScheduleUpdated
        self.__comp7Controller.onModeConfigChanged += self.__onScheduleUpdated
        self.__comp7Controller.onStatusUpdated += self.__onStatusUpdated
        self.__comp7Controller.onOfflineStatusUpdated += self.__onOfflineStatusUpdated
        self.__comp7ShopController.onShopStateChanged += self.__onShopStateChanged
        self.__comp7ShopController.onDataUpdated += self.__onShopDataUpdated
        if self.__guiLoader.windowsManager is not None:
            self.__guiLoader.windowsManager.onViewStatusChanged += self.__onViewStatusChanged
        self.__offersProvider.onOffersUpdated += self.__updateWeeklyQuestsClaimRewardsModel
        self.viewModel.claimRewardsModel.onGoToRewardSelection += showComp7AllRewardsSelectionWindow
        return

    def __removeListeners(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.sidebar.onSideBarTabChange -= self.__onSideBarTabChanged
        self.viewModel.scheduleInfo.season.pollServerTime -= self.__onScheduleUpdated
        self.__comp7Controller.onModeConfigChanged -= self.__onScheduleUpdated
        self.__comp7Controller.onStatusUpdated -= self.__onStatusUpdated
        self.__comp7Controller.onOfflineStatusUpdated -= self.__onOfflineStatusUpdated
        self.__comp7ShopController.onShopStateChanged -= self.__onShopStateChanged
        self.__comp7ShopController.onDataUpdated -= self.__onShopDataUpdated
        if self.__guiLoader.windowsManager is not None:
            self.__guiLoader.windowsManager.onViewStatusChanged -= self.__onViewStatusChanged
        self.__offersProvider.onOffersUpdated -= self.__updateWeeklyQuestsClaimRewardsModel
        self.viewModel.claimRewardsModel.onGoToRewardSelection -= showComp7AllRewardsSelectionWindow
        return

    def __onShopDataUpdated(self, status):
        if status == ShopControllerStatus.DATA_READY:
            self.__products = self.__comp7ShopController.getProducts()
            self.updateTabNotifications()

    def __onShopStateChanged(self):
        self.__products = self.__comp7ShopController.getProducts()
        self.updateTabNotifications()

    def __onScheduleUpdated(self):
        comp7_core_model_helpers.setScheduleInfo(self.viewModel.scheduleInfo, self.__comp7Controller, COMP7_TOOLTIPS.COMP7_CALENDAR_DAY_INFO, SeasonState, YearState, SeasonName)

    def __onStatusUpdated(self, _):
        if not self.__comp7Controller.isEnabled() or self.__comp7Controller.isFrozen():
            showHangar()
        else:
            comp7_core_model_helpers.setScheduleInfo(self.viewModel.scheduleInfo, self.__comp7Controller, COMP7_TOOLTIPS.COMP7_CALENDAR_DAY_INFO, SeasonState, YearState, SeasonName)

    def __onOfflineStatusUpdated(self):
        if self.__comp7Controller.isOffline:
            showHangar()

    def __updateWeeklyQuestsClaimRewardsModel(self):
        rewardsCount = Comp7SelectableRewardManager.getRemainedChoicesForFeature()
        self.viewModel.claimRewardsModel.setRewardsCount(rewardsCount)

    def __initPages(self):
        model = self.getViewModel()
        pages = (ProgressionPage(model.progressionModel, self),
         RankRewardsPage(model.rankRewardsModel, self),
         YearlyRewardsPage(model.yearlyRewardsModel, self),
         WeeklyQuestsPage(model.weeklyQuestsModel, self),
         LeaderboardPage(model.leaderboardModel, self),
         ShopPage(model.shopModel, self),
         YearlyStatisticsPage(model.yearlyStatisticsModel, self))
        self.__pages = {p.pageId:p for p in pages}

    def __clearPages(self):
        if not self.__pages:
            return
        if self.__currentPage and self.__currentPage.isLoaded:
            self.__currentPage.finalize()
        self.__pages.clear()

    def __updateTabs(self):
        with self.viewModel.transaction() as tx:
            tabs = tx.sidebar.getItems()
            tabs.clear()
            for tab in tuple(MetaRootViews):
                tabModel = TabModel()
                tabModel.setId(tab)
                tabs.addViewModel(tabModel)

            tabs.invalidate()

    def __onClose(self):
        showHangar()

    def __onViewStatusChanged(self, viewID, status):
        view = self.__guiLoader.windowsManager.getView(viewID)
        if view and view.layoutID == R.views.comp7.mono.lobby.dialogs.purchase_dialog():
            if status == ViewStatus.LOADING:
                if self.__currentPage.isLoaded:
                    self.__currentPage.finalize()
            elif status == ViewStatus.DESTROYING:
                self.__currentPage.initialize()

    @args2params(int)
    def __onSideBarTabChanged(self, tabId):
        if tabId == self.__tabId:
            return
        if tabId not in self.__pages:
            _logger.error('Wrong tabId: %s', tabId)
            return
        showComp7MetaRootTab(tabId)
