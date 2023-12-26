# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/shop_overlay_view.py
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer, ViewFlags
from gui.impl.common.browser import Browser, BrowserSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.shop_overlay_view_model import ShopOverlayViewModel
from gui.impl.lobby.loot_box.loot_box_helper import getLootBoxByTypeAndCategory, setGaranteedRewardData
from gui.impl.new_year.sounds import NewYearSoundsManager
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.new_year.views.tabs_controller import RewardKitsEntryViewTabsController
from gui.impl.lobby.new_year.ny_reward_kit_statistics import NyRewardKitStatistics
from gui.impl.lobby.new_year.tooltips.ny_customizations_statistics_tooltip import NyCustomizationsStatisticsTooltip
from gui.impl.lobby.new_year.tooltips.ny_reward_kit_guest_c_tooltip import NyRewardKitGuestCTooltip
from gui.impl.lobby.new_year.tooltips.ny_vehicles_statistics_tooltip import NyVehiclesStatisticsTooltip
from gui.impl.lobby.new_year.tooltips.ny_equipments_statistics_tooltip import NyEquipmentsStatisticsTooltip
from gui.impl.lobby.new_year.tooltips.ny_resource_tooltip import NyResourceTooltip
from gui.impl.lobby.new_year.tooltips.ny_guaranteed_reward_tooltip import NyGuaranteedRewardTooltip
from gui.impl.lobby.tooltips.loot_box_category_tooltip import LootBoxCategoryTooltipContent
from gui.shared import event_dispatcher, EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.gui_items.loot_box import NewYearCategories, NewYearLootBoxes
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from uilogging.ny.loggers import NyStatisticsPopoverLogger
from web.web_client_api import webApiCollection, ui as ui_web_api, sound as sound_web_api
from web.web_client_api.ny20 import LootBoxOpenTabWebApi, NYLootBoxWebApi
from web.web_client_api.platform import PlatformWebApi
from web.web_client_api.promo import PromoWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api.ui.util import NY_OVERLAY_PAGE_CHANGED_EVENT
from web.web_client_api.uilogging import UILoggingWebApi
_SHOW_HIDE_CONTAINERS = (WindowLayer.VIEW,)
_HIDE_DURATION = _SHOW_DURATION = 0.3

class ShopOverlayView(ViewImpl):
    __slots__ = ('__rewardKitStatistics', '__lastStatisticsResetFailed', '__tabsController', '__url')
    __itemsCache = dependency.descriptor(IItemsCache)
    __popoverLogger = NyStatisticsPopoverLogger()

    def __init__(self, url):
        settings = ViewSettings(R.views.lobby.new_year.ShopOverlayView())
        settings.model = ShopOverlayViewModel()
        settings.flags = ViewFlags.VIEW
        self.__url = url
        self.__tabsController = RewardKitsEntryViewTabsController()
        self.__lastStatisticsResetFailed = False
        self.__rewardKitStatistics = NyRewardKitStatistics()
        super(ShopOverlayView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(ShopOverlayView, self)._onLoading(*args, **kwargs)
        self.__update()
        self.__updateStatistics()
        self.setChildView(ShopOverlayViewModel.SUB_VIEW_ID, Browser(self.__url, BrowserSettings(R.views.common.Browser()), _webHandlers()))

    def _onLoaded(self, *args, **kwargs):
        self.__changeLayersVisibiliy(True)
        NewYearSoundsManager.setOverlayHangarFilteredState(True)

    def _finalize(self):
        self.__rewardKitStatistics = None
        self.__changeLayersVisibiliy(False)
        NewYearSoundsManager.setOverlayHangarFilteredState(False)
        g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_BUY_VIEW_CLOSED), EVENT_BUS_SCOPE.LOBBY)
        super(ShopOverlayView, self)._finalize()
        return

    @property
    def viewModel(self):
        return super(ShopOverlayView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.loot_box_category_tooltip.LootBoxCategoryTooltipContent():
            return LootBoxCategoryTooltipContent(event.getArgument('category', ''))
        if contentID == R.views.lobby.new_year.tooltips.NyGuaranteedRewardTooltip():
            return NyGuaranteedRewardTooltip()
        if contentID == R.views.lobby.new_year.tooltips.NyRewardKitGuestCTooltip():
            return NyRewardKitGuestCTooltip()
        if contentID == R.views.lobby.new_year.tooltips.NyVehiclesStatisticsTooltip():
            return NyVehiclesStatisticsTooltip(self.__tabsController.getSelectedBoxID())
        if contentID == R.views.lobby.new_year.tooltips.NyResourceTooltip():
            return NyResourceTooltip(event.getArgument('type'))
        if contentID == R.views.lobby.new_year.tooltips.NyCustomizationsStatisticsTooltip():
            return NyCustomizationsStatisticsTooltip(self.__tabsController.getSelectedBoxID())
        return NyEquipmentsStatisticsTooltip(self.__tabsController.getSelectedBoxID()) if contentID == R.views.lobby.new_year.tooltips.NyEquipmentsStatisticsTooltip() else super(ShopOverlayView, self).createToolTipContent(event, contentID)

    def __onResetClick(self):
        self.__rewardKitStatistics.resetStatistics(self.__tabsController.getSelectedBoxID())

    def __onCacheResync(self, *_):
        self.__updateStatistics()

    @staticmethod
    def __onGuaranteedRewardsInfo(_=None):
        event_dispatcher.openLootBoxesInfoURL()

    def __onStatisticsReset(self, event):
        self.__lastStatisticsResetFailed = event.ctx['serverError']

    def __onMainPageChanged(self, event):
        self.__updateModel(event.ctx.get('isMainPage'))

    def __onUpdateLastSeen(self):
        self.__rewardKitStatistics.updateLastSeen()

    def __updateModel(self, isMainPage):
        with self.viewModel.transaction() as model:
            model.setIsMainPageVisible(isMainPage)

    def __update(self):
        with self.viewModel.transaction() as model:
            boxType = NewYearLootBoxes.PREMIUM
            boxCategory = NewYearCategories.CHRISTMAS
            lootboxItem = getLootBoxByTypeAndCategory(boxType, boxCategory, isInInventory=False)
            setGaranteedRewardData(model.guaranteedReward, lootboxItem, enabledIfManyAttemptsLeft=True)

    def __updateStatistics(self):
        with self.viewModel.transaction() as model:
            self.__rewardKitStatistics.updateStatistics(model.rewardKitStatistics, self.__tabsController.getSelectedBoxID(), self.__lastStatisticsResetFailed)

    def _getEvents(self):
        return ((self.__itemsCache.onSyncCompleted, self.__onCacheResync),
         (self.viewModel.guaranteedReward.onShowInfo, self.__onGuaranteedRewardsInfo),
         (self.viewModel.rewardKitStatistics.onResetStatistics, self.__onResetClick),
         (self.viewModel.rewardKitStatistics.onUpdateLastSeen, self.__onUpdateLastSeen))

    def _getListeners(self):
        return ((events.LootboxesEvent.ON_STATISTICS_RESET, self.__onStatisticsReset, EVENT_BUS_SCOPE.LOBBY), (NY_OVERLAY_PAGE_CHANGED_EVENT, self.__onMainPageChanged), (events.HideWindowEvent.HIDE_OVERLAY_BROWSER_VIEW, self.__handleBrowserClose, EVENT_BUS_SCOPE.LOBBY))

    def __changeLayersVisibiliy(self, isHide):
        from skeletons.gui.app_loader import IAppLoader
        appLoader = dependency.instance(IAppLoader)
        lobby = appLoader.getDefLobbyApp()
        if lobby:
            if isHide:
                lobby.containerManager.hideContainers(_SHOW_HIDE_CONTAINERS, time=_HIDE_DURATION)
            else:
                lobby.containerManager.showContainers(_SHOW_HIDE_CONTAINERS, time=_SHOW_DURATION)

    def __handleBrowserClose(self, _):
        self.destroyWindow()


def _webHandlers():
    return webApiCollection(PromoWebApi, RequestWebApi, ui_web_api.OpenWindowWebApi, ui_web_api.CloseWindowWebApi, ui_web_api.NotificationWebApi, ui_web_api.ContextMenuWebApi, ui_web_api.UtilWebApi, sound_web_api.SoundWebApi, sound_web_api.HangarSoundWebApi, PlatformWebApi, LootBoxOpenTabWebApi, NYLootBoxWebApi, UILoggingWebApi)


class ShopOverlayViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, url):
        super(ShopOverlayViewWindow, self).__init__(WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=ShopOverlayView(url=url), parent=None, layer=WindowLayer.TOP_WINDOW)
        return
