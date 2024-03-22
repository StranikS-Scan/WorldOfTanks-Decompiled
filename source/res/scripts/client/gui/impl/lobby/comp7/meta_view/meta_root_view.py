# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/meta_view/meta_root_view.py
import logging
import typing
from shared_utils import findFirst
from frameworks.wulf import ViewFlags, ViewSettings, ViewStatus, WindowLayer
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.game_control.comp7_shop_controller import ShopControllerStatus
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_tooltip import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.root_view_model import RootViewModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.tab_model import MetaRootViews, TabModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.comp7 import comp7_model_helpers
from gui.impl.lobby.comp7.comp7_lobby_sounds import getComp7MetaSoundSpace, playComp7MetaViewTabSound
from gui.impl.lobby.comp7.meta_view.pages.leaderboard_page import LeaderboardPage
from gui.impl.lobby.comp7.meta_view.pages.progression_page import ProgressionPage
from gui.impl.lobby.comp7.meta_view.pages.rank_rewards_page import RankRewardsPage
from gui.impl.lobby.comp7.meta_view.pages.shop_page import ShopPage
from gui.impl.lobby.comp7.meta_view.pages.weekly_quests_page import WeeklyQuestsPage
from gui.impl.lobby.comp7.meta_view.pages.yearly_rewards_page import YearlyRewardsPage
from gui.impl.lobby.comp7.meta_view.pages.yearly_statistics_page import YearlyStatisticsPage
from gui.impl.lobby.comp7.meta_view.products_helper import hasUnseenProduct
from gui.impl.lobby.mode_selector.items.base_item import getInfoPageKey
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.shared.event_dispatcher import showBrowserOverlayView, showHangar, showComp7WhatsNewScreen
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller, IComp7ShopController
from skeletons.gui.impl import IGuiLoader
if typing.TYPE_CHECKING:
    from gui.impl.lobby.comp7.meta_view.pages import PageSubModelPresenter
_logger = logging.getLogger(__name__)

class MetaRootView(ViewImpl, IGlobalListener):
    __slots__ = ('__pages', '__tabId', '__products')
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __comp7ShopController = dependency.descriptor(IComp7ShopController)
    __guiLoader = dependency.descriptor(IGuiLoader)
    _COMMON_SOUND_SPACE = getComp7MetaSoundSpace()

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = RootViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(MetaRootView, self).__init__(settings)
        self.__pages = {}
        self.__tabId = MetaRootViews.PROGRESSION
        self.__products = None
        return

    @property
    def viewModel(self):
        return super(MetaRootView, self).getViewModel()

    @property
    def tabId(self):
        return self.__tabId

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TOOLTIPS_CONSTANTS.COMP7_CALENDAR_DAY_INFO:
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
        if self.__currentPage.isLoaded:
            window = self.__currentPage.createContextMenu(event)
            if window is not None:
                return window
        return super(MetaRootView, self).createContextMenu(event)

    def onPrbEntitySwitched(self):
        if not self.__comp7Controller.isComp7PrbActive():
            showHangar()

    def switchPage(self, tabId, *args, **kwargs):
        if self.__currentPage.isLoaded:
            self.__currentPage.finalize()
        page = self.__pages[tabId]
        page.initialize(*args, **kwargs)
        self.viewModel.setPageViewId(page.pageId)
        playComp7MetaViewTabSound(tabId, self.__tabId)
        self.__tabId = tabId
        g_eventDispatcher.updateUI()

    def updateTabNotifications(self):
        shopTab = findFirst(lambda tab: tab.getId() == MetaRootViews.SHOP, self.viewModel.sidebar.getItems())
        if self.__products:
            shopTab.setHasNotification(hasUnseenProduct(self.__products))
        else:
            shopTab.setHasNotification(False)

    def _finalize(self):
        self.__removeListeners()
        self.__clearPages()
        self.__products = None
        return

    def _onLoading(self, *args, **kwargs):
        tabId = kwargs.pop('tabId', None)
        if tabId is not None:
            if tabId in tuple(MetaRootViews):
                self.__tabId = tabId
            else:
                _logger.error('Wrong tabId: %s', tabId)
        self.__initPages()
        self.__updateTabs()
        self.__products = self.__comp7ShopController.getProducts()
        self.updateTabNotifications()
        page = self.__pages[self.__tabId]
        page.initialize(*args, **kwargs)
        self.viewModel.setPageViewId(page.pageId)
        comp7_model_helpers.setScheduleInfo(model=self.viewModel.scheduleInfo)
        self.__addListeners()
        return

    def _onLoaded(self, *args, **kwargs):
        playComp7MetaViewTabSound(self.__tabId)

    @property
    def __currentPage(self):
        return self.__pages[self.__tabId]

    def __addListeners(self):
        self.viewModel.onClose += self.__onClose
        self.viewModel.onInfoPageOpen += self.__onInfoPageOpen
        self.viewModel.onWhatsNewScreenOpen += self.__onWhatsNewScreenOpen
        self.viewModel.sidebar.onSideBarTabChange += self.__onSideBarTabChanged
        self.viewModel.scheduleInfo.season.pollServerTime += self.__onScheduleUpdated
        self.__comp7Controller.onComp7ConfigChanged += self.__onScheduleUpdated
        self.__comp7Controller.onStatusUpdated += self.__onStatusUpdated
        self.__comp7Controller.onOfflineStatusUpdated += self.__onOfflineStatusUpdated
        self.__comp7ShopController.onShopStateChanged += self.__onShopStateChanged
        self.__comp7ShopController.onDataUpdated += self.__onShopDataUpdated
        if self.__guiLoader.windowsManager is not None:
            self.__guiLoader.windowsManager.onViewStatusChanged += self.__onViewStatusChanged
        self.startGlobalListening()
        return

    def __removeListeners(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onInfoPageOpen -= self.__onInfoPageOpen
        self.viewModel.onWhatsNewScreenOpen -= self.__onWhatsNewScreenOpen
        self.viewModel.sidebar.onSideBarTabChange -= self.__onSideBarTabChanged
        self.viewModel.scheduleInfo.season.pollServerTime -= self.__onScheduleUpdated
        self.__comp7Controller.onComp7ConfigChanged -= self.__onScheduleUpdated
        self.__comp7Controller.onStatusUpdated -= self.__onStatusUpdated
        self.__comp7Controller.onOfflineStatusUpdated -= self.__onOfflineStatusUpdated
        self.__comp7ShopController.onShopStateChanged -= self.__onShopStateChanged
        self.__comp7ShopController.onDataUpdated -= self.__onShopDataUpdated
        if self.__guiLoader.windowsManager is not None:
            self.__guiLoader.windowsManager.onViewStatusChanged -= self.__onViewStatusChanged
        self.stopGlobalListening()
        return

    def __onShopDataUpdated(self, status):
        if status == ShopControllerStatus.DATA_READY:
            self.__products = self.__comp7ShopController.getProducts()
            self.updateTabNotifications()

    def __onShopStateChanged(self):
        self.__products = self.__comp7ShopController.getProducts()
        self.updateTabNotifications()

    def __onScheduleUpdated(self):
        comp7_model_helpers.setScheduleInfo(model=self.viewModel.scheduleInfo)

    def __onStatusUpdated(self, _):
        if not self.__comp7Controller.isEnabled() or self.__comp7Controller.isFrozen():
            showHangar()
        else:
            comp7_model_helpers.setScheduleInfo(model=self.viewModel.scheduleInfo)

    def __onOfflineStatusUpdated(self):
        if self.__comp7Controller.isOffline:
            showHangar()

    def __initPages(self):
        pages = (ProgressionPage(self.viewModel.progressionModel, self),
         RankRewardsPage(self.viewModel.rankRewardsModel, self),
         YearlyRewardsPage(self.viewModel.yearlyRewardsModel, self),
         WeeklyQuestsPage(self.viewModel.weeklyQuestsModel, self),
         LeaderboardPage(self.viewModel.leaderboardModel, self),
         ShopPage(self.viewModel.shopModel, self),
         YearlyStatisticsPage(self.viewModel.yearlyStatisticsModel, self))
        self.__pages = {p.pageId:p for p in pages}

    def __clearPages(self):
        if self.__currentPage.isLoaded:
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
        if view and view.layoutID == R.views.lobby.comp7.dialogs.PurchaseDialog():
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
        self.switchPage(tabId)

    @staticmethod
    def __onInfoPageOpen():
        url = GUI_SETTINGS.lookup(getInfoPageKey(SELECTOR_BATTLE_TYPES.COMP7))
        showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))

    @staticmethod
    def __onWhatsNewScreenOpen():
        showComp7WhatsNewScreen()
