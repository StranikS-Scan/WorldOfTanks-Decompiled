# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/rewards_info/ny_rewards_info_view.py
from collections import namedtuple
import typing
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.ny_rewards_info_view_model import NyRewardsInfoViewModel
from new_year.gui.impl.lobby.new_year.rewards_info.ny_levels_rewards_presenter import NyLevelsRewardsPresenter
from new_year.gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from new_year.gui.shared.event_dispatcher import showVehicleDiscountOverlay
from new_year.gui.shared.events import NewYearEvent
from new_year.gui.shared.ny_level_helper import NewYearAtmospherePresenter
from new_year.gui.shared.shop_helpers import newYearOldCollectionRewardUrl
from new_year.helpers.server_settings import getNewYearGeneralConfig
from new_year.ny_constants import NyTabBarRewardsView, NyWidgetTopMenu, ViewAliases
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shop import showIngameShop
if typing.TYPE_CHECKING:
    from new_year.gui.shared.event_dispatcher import NYTabCtx
    from new_year.gui.impl.lobby.new_year.rewards_info.rewards_sub_model_presenter import RewardsSubModelPresenter
_TabSwitchInfo = namedtuple('_TabSwitchInfo', 'presenter kwargs')

class NyRewardsInfoView(HistorySubModelPresenter):
    _navigationAlias = ViewAliases.REWARDS_VIEW
    __slots__ = ('__currentTab', '__tabPresentersMap', '__ctx', '__generalConfig')

    def __init__(self, viewModel, parentView, *args, **kwargs):
        super(NyRewardsInfoView, self).__init__(viewModel, parentView, *args, **kwargs)
        self.__ctx = None
        self.__currentTab = NyTabBarRewardsView.FOR_LEVELS
        levelsPresenter = NyLevelsRewardsPresenter(viewModel.levelsRewards, self)
        self.__tabPresentersMap = {NyTabBarRewardsView.FOR_LEVELS: _TabSwitchInfo(levelsPresenter, {})}
        self.__generalConfig = getNewYearGeneralConfig()
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def currentSubModelPresenter(self):
        return self.__tabPresentersMap[self.__currentTab].presenter

    @property
    def currentTab(self):
        return self.__currentTab

    def createToolTip(self, event):
        return self.currentSubModelPresenter.createToolTip(event)

    def createToolTipContent(self, event, ctID):
        return self.currentSubModelPresenter.createToolTipContent(event, ctID)

    def initialize(self, tabName=None, *args, **kwargs):
        super(NyRewardsInfoView, self).initialize(*args, **kwargs)
        self.viewModel.onFadeInDone += self.__onFadeInDone
        self.viewModel.onGotoStore += self.__onGoToStore
        self.viewModel.onSelectVehicleDiscount += self.__onSelectVehicleDiscount
        g_eventBus.addListener(NewYearEvent.ON_SIDEBAR_SELECTED, self.__onSideBarSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        tabName = tabName or self._tabCache.getRewardsTab() or NyTabBarRewardsView.FOR_LEVELS
        self.__changeTab(tabName, **kwargs)

    def finalize(self):
        self.viewModel.onFadeInDone -= self.__onFadeInDone
        self.viewModel.onGotoStore -= self.__onGoToStore
        self.viewModel.onSelectVehicleDiscount -= self.__onSelectVehicleDiscount
        g_eventBus.removeListener(NewYearEvent.ON_SIDEBAR_SELECTED, self.__onSideBarSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        for tabInfo in self.__tabPresentersMap.values():
            if tabInfo.presenter.isLoaded:
                tabInfo.presenter.finalize()

        super(NyRewardsInfoView, self).finalize()

    def clear(self):
        for tabInfo in self.__tabPresentersMap.values():
            tabInfo.presenter.clear()

        self.__tabPresentersMap.clear()
        super(NyRewardsInfoView, self).clear()

    def _getInfoForHistory(self):
        return self.currentSubModelPresenter.getInfoForHistory()

    def __onSideBarSelected(self, event):
        self.__ctx = event.ctx
        if self.__ctx.menuName != NyWidgetTopMenu.REWARDS:
            return
        self.viewModel.setIsFaded(True)

    def __onFadeInDone(self):
        if self.__ctx is not None:
            self.viewModel.setIsFaded(False)
            self.__changeTab(self.__ctx.tabName)
            self.__ctx = None
        return

    def __onGoToStore(self):
        showIngameShop(newYearOldCollectionRewardUrl())

    def __changeTab(self, tabName, **kwargs):
        if tabName not in self.__tabPresentersMap:
            return
        curTabInfo = self.__tabPresentersMap[self.__currentTab]
        newTabInfo = self.__tabPresentersMap[tabName]
        kwargs.update(newTabInfo.kwargs)
        if curTabInfo.presenter.isLoaded:
            if tabName == NyTabBarRewardsView.COLLECTIONS:
                newTabInfo.presenter.update(**kwargs)
            else:
                curTabInfo.presenter.finalize()
                newTabInfo.presenter.initialize(**kwargs)
        else:
            newTabInfo.presenter.initialize(**kwargs)
        self.viewModel.setIsLevelsRewardsOpened(tabName == NyTabBarRewardsView.FOR_LEVELS)
        self.__setLevelInfo()
        self.__currentTab = tabName
        self._tabCache.setRewardsTab(tabName)

    def __setLevelInfo(self):
        with self.viewModel.transaction() as tx:
            tx.setProgressionLevel(NewYearAtmospherePresenter.getLevel())
            tx.setProgressionPoints(NewYearAtmospherePresenter.getTotalAtmospherePoints())
            progressionLevels = tx.getProgressionLevels()
            progressionLevels.clear()
            atmosphereLimits = self.__generalConfig.getAtmosphereLevelLimits()
            for level, bound in enumerate(atmosphereLimits):
                progressionLevelModel = tx.getProgressionLevelsType()()
                progressionLevelModel.setNumber(level)
                progressionLevelModel.setMaxPoints(bound)
                progressionLevels.addViewModel(progressionLevelModel)

            progressionLevels.invalidate()

    def __onSelectVehicleDiscount(self):
        showVehicleDiscountOverlay()
