# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/navigation_view.py
import logging
import typing
import adisp
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from functools import partial
from gui import GUI_SETTINGS
from gui.impl.gen.view_models.views.lobby.paragons.navigation_view_model import NavigationViewModel, TabId
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.paragons.presenters.progress_presenter import ProgressPresenter
from gui.impl.lobby.paragons.presenters.rewards_presenter import RewardsPresenter
from gui.impl.lobby.paragons.presenters.chapters_presenter import ChaptersPresenter
from gui.impl.lobby.paragons.presenters.about_presenter import AboutPresenter
from gui.impl.lobby.paragons.tooltips.entry_point_tooltip import EntryPointTooltip
from gui.impl.lobby.paragons.sound_constants import PARAGONS_SOUND_SPACE
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.gen import R
from gui.shared import event_dispatcher
from helpers import dependency
from paragons_common import ParagonsEntitlements, getParagonsEntitlement
from skeletons.gui.game_control import IParagonsController, IParagonsRewardsShopController
from gui.impl.common.browser import Browser, BrowserSettings
from web.web_client_api.promo import PromoWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api import webApiCollection, ui as ui_web_api, sound as sound_web_api
_logger = logging.getLogger(__name__)

def _browserHandlers():
    return webApiCollection(PromoWebApi, RequestWebApi, ui_web_api.OpenWindowWebApi, ui_web_api.CloseWindowWebApi, ui_web_api.OpenTabWebApi, ui_web_api.NotificationWebApi, ui_web_api.ContextMenuWebApi, ui_web_api.UtilWebApi, sound_web_api.SoundWebApi, sound_web_api.HangarSoundWebApi)


class NavigationView(ViewImpl):
    __slots__ = ('__currentTabID', '__tabsToPresenter')
    __paragonsController = dependency.descriptor(IParagonsController)
    __selectableRewardsController = dependency.descriptor(IParagonsRewardsShopController)
    _COMMON_SOUND_SPACE = PARAGONS_SOUND_SPACE

    def __init__(self, layoutID, tabId=TabId.PROGRESS):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = NavigationViewModel()
        super(NavigationView, self).__init__(settings)
        self.__currentTabID = tabId
        self.__tabsToPresenter = {TabId.PROGRESS: ProgressPresenter(self.viewModel.progression, self),
         TabId.REWARDS: RewardsPresenter(self.viewModel.allRewards, self),
         TabId.CHAPTERS: ChaptersPresenter(self.viewModel.allChapters, self),
         TabId.ABOUT: AboutPresenter(self.viewModel.about, self)}

    @property
    def viewModel(self):
        return super(NavigationView, self).getViewModel()

    @property
    def __currentTab(self):
        return self.__tabsToPresenter[self.__currentTabID]

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(NavigationView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        subViewTooltip = self.__tabsToPresenter[self.__currentTabID].createToolTipContent(event, contentID)
        if subViewTooltip:
            return subViewTooltip
        return EntryPointTooltip() if contentID == R.views.lobby.paragons.tooltips.EntryPointTooltip() else super(NavigationView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        return self.__tabsToPresenter[self.__currentTabID].getTooltipData(event)

    @adisp.adisp_process
    def __preloadSelectable(self):
        yield self.__selectableRewardsController.fetchProducts()

    def _onLoading(self, *args, **kwargs):
        super(NavigationView, self)._onLoading(*args, **kwargs)
        self.__switchTab(tabID=self.__currentTabID, *args, **kwargs)
        self.__selectableRewardsController.entitlements.update(True)
        self.__preloadSelectable()
        self.__updateNavigationStatus()
        url = GUI_SETTINGS.lookup('ParagonsInfoPageURL')
        self.setChildView(TabId.ABOUT, Browser(url, BrowserSettings(R.views.common.Browser()), _browserHandlers()))

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onBack, self.__onBackToPrevScreen),
         (self.viewModel.onTabChange, self.__onTabChange),
         (self.viewModel.onToChaptersView, partial(self.__switchTab, TabId.CHAPTERS)),
         (self.__selectableRewardsController.entitlements.onEntitlementsUpdated, self.__updateNavigationStatus),
         (self.__paragonsController.onSelectedRewardTokenReceived, self.__updateNavigationStatus),
         (self.__paragonsController.onSettingsChanged, self.__updateNavigationStatus),
         (self.__paragonsController.onProgressPointsChanged, self.__updateNavigationStatus))

    def _finalize(self):
        self.__closeTabs()
        self.setChildView(TabId.ABOUT, None)
        super(NavigationView, self)._finalize()
        return

    def __updateNavigationStatus(self, *args):
        chapterID = self.__paragonsController.chapterID
        entID = getParagonsEntitlement(ParagonsEntitlements.V_11.value)
        entitlements = self.__selectableRewardsController.entitlements
        hasNewRewards = bool(entitlements.getEntitlementsByID(entID))
        hasNewChapters = chapterID is None and self.__paragonsController.isAnyChapterAvailable
        wasChapterSelected = chapterID or self.__paragonsController.getFirstChapterWithAvailableRewards()
        with self.viewModel.transaction() as tx:
            tx.setHasNewRewards(hasNewRewards)
            tx.setHasNewChapters(hasNewChapters)
            tx.setWasChapterSelected(wasChapterSelected)
            tx.setParagonPoints(self.__paragonsController.progress)
        return

    def __onTabChange(self, event):
        switchTabID = TabId(int(event.get('tabId', 0)))
        if switchTabID == self.__currentTabID:
            return
        self.__switchTab(switchTabID)

    def __switchTab(self, tabID=TabId.PROGRESS, *args, **kwargs):
        if self.__currentTab.isLoaded:
            self.__currentTab.finalize()
        tab = self.__tabsToPresenter[tabID]
        tab.initialize(*args, **kwargs)
        self.__currentTabID = tabID
        self.viewModel.setCurrentTabId(self.__currentTabID)
        self.__updateNavigationStatus()

    def __closeTabs(self):
        for tab in self.__tabsToPresenter.values():
            tab.finalize()

        self.__tabsToPresenter.clear()

    def __onClose(self):
        self.destroyWindow()
        event_dispatcher.showHangar()

    def __onBackToPrevScreen(self):
        self.destroyWindow()
        event_dispatcher.showVehicleTechTreeView()


class NavigationViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, tabId=TabId.PROGRESS, parent=None):
        super(NavigationViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW, layer=WindowLayer.TOP_SUB_VIEW, content=NavigationView(R.views.lobby.paragons.NavigationView(), tabId), parent=parent)
