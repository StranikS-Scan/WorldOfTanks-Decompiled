# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/views/frontline_container_view.py
import SoundGroups
from frameworks.wulf import ViewFlags, ViewSettings
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_container_view_model import FrontlineContainerViewModel
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_container_tab_model import FrontlineContainerTabModel, TabType
from frontline.gui.impl.lobby.views import sub_views
from gui.sounds.epic_sound_constants import EPIC_SOUND
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from frontline.gui.impl.lobby.tooltips.unlock_conditions_tooltip import UnlockConditionsTooltip
from gui.impl.lobby.crew.tooltips.vehicle_params_tooltip_view import FrontlineAdvancedParamsTooltipView
from gui.shared.tooltips.contexts import HangarParamContext
from uilogging.epic_battle.constants import EpicBattleLogKeys, EpicBattleLogTabs, EpicBattleLogActions
from uilogging.epic_battle.loggers import EpicBattleLogger
from gui.shared.event_dispatcher import showHangar, showFrontlineInfoWindow
TABS = [(TabType.SUPPLY,
  R.views.frontline.lobby.SupplyObjectsView(),
  sub_views.SupplyObjectsView,
  (EpicBattleLogKeys.SUPPLY_OBJECTS_VIEW, EpicBattleLogTabs.SUPPLY_OBJECTS_TAB)), (TabType.PROGRESS,
  R.views.frontline.lobby.ProgressView(),
  sub_views.ProgressView,
  (EpicBattleLogKeys.PROGRESS_VIEW, EpicBattleLogTabs.PROGRESS_TAB)), (TabType.REWARDS,
  R.views.frontline.lobby.RewardsView(),
  sub_views.RewardsView,
  (EpicBattleLogKeys.REWARDS_VIEW, EpicBattleLogTabs.REWARDS_TAB))]
DEFAULT_TAB_ID = 0

class FrontlineContainerView(ViewImpl):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __slots__ = ('_activeTab', '_tabTypeToID', '_seasonId', '__uiEpicBattleLogger')

    def __init__(self, layoutId=R.views.frontline.lobby.FrontlineContainerView(), activeTab=TabType.PROGRESS):
        settings = ViewSettings(layoutId, ViewFlags.LOBBY_SUB_VIEW, FrontlineContainerViewModel())
        self.__uiEpicBattleLogger = EpicBattleLogger()
        self._seasonId = self._getSeasonId()
        self._activeTab = activeTab
        self._tabTypeToID = {}
        super(FrontlineContainerView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(FrontlineContainerView, self).getViewModel()

    def updateTabNotifications(self):
        tabNotifications = self._getTabNotifications()
        with self.viewModel.transaction() as vm:
            tabs = vm.getTabs()
            for tab in tabs:
                tab.setIsHighlighted(tabNotifications.get(tab.getType().value, False))

            tabs.invalidate()

    def _getEvents(self):
        return ((self.viewModel.onTabChange, self.__onTabChange), (self.viewModel.onClose, self.__onClose), (self.viewModel.onInfo, self.__onInfo))

    def _createTab(self, tabId, tabType, resId):
        self._tabTypeToID[tabType.value] = tabId
        tabNotifications = self._getTabNotifications()
        with self.viewModel.transaction() as vm:
            tabModel = FrontlineContainerTabModel()
            tabModel.setId(tabId)
            tabModel.setType(tabType)
            tabModel.setIsHighlighted(tabNotifications.get(tabType.value, False))
            tabModel.setResId(resId)
            vm.getTabs().addViewModel(tabModel)
        return tabId

    def _getTabNotifications(self):
        return {TabType.REWARDS.value: self.__epicController.getNotChosenRewardCount() > 0}

    def _getSeasonId(self):
        seasons = (self.__epicController.getCurrentSeason(), self.__epicController.getNextSeason(), self.__epicController.getPreviousSeason())
        for season in seasons:
            if season is not None:
                return season.getSeasonID()

        return

    def _getTabIdByType(self, tabType):
        if tabType.value in self._tabTypeToID:
            return self._tabTypeToID[tabType.value]
        ids = self._tabTypeToID.values()
        return ids[0] if ids else DEFAULT_TAB_ID

    def _getCurrentTabLoggingTypes(self):
        activeTabId = self._getTabIdByType(self._activeTab)
        return TABS[activeTabId][3]

    def _onLoading(self, *args, **kwargs):
        super(FrontlineContainerView, self)._onLoading(*args, **kwargs)
        for tabId, tab in enumerate(TABS):
            params = tab[:-2]
            self._createTab(tabId, *params)

        with self.viewModel.transaction() as vm:
            vm.setCurrentTabId(self._getTabIdByType(self._activeTab))
        self.__startTabLogger()

    def _onLoaded(self, *args, **kwargs):
        super(FrontlineContainerView, self)._onLoaded()
        SoundGroups.g_instance.playSound2D(EPIC_SOUND.EB_AMBIENT_PROGRESS_PAGE_ENTER)
        for tab in TABS:
            resId, lazyView = tab[1:-1]
            self.setChildView(resId, lazyView(parentView=self))

    def createToolTipContent(self, event, contentId):
        if contentId == R.views.lobby.crew.tooltips.VehicleParamsTooltipView():
            paramName = event.getArgument('paramName', '')
            context = HangarParamContext()
            return FrontlineAdvancedParamsTooltipView(paramName=paramName, context=context, supportAdvanced=False)
        if contentId == R.views.frontline.lobby.tooltips.UnlockConditionsTooltip():
            supplyName = event.getArgument('supplyObject', '')
            return UnlockConditionsTooltip(supplyName=supplyName)

    def _finalize(self):
        super(FrontlineContainerView, self)._finalize()
        changeHeaderVisible(True)
        SoundGroups.g_instance.playSound2D(EPIC_SOUND.EB_AMBIENT_PROGRESS_PAGE_EXIT)
        self.__stopTabLogger()
        viewType, _ = self._getCurrentTabLoggingTypes()
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLOSE.value, item=viewType.value, parentScreen=EpicBattleLogKeys.HANGAR.value)

    def __onTabChange(self, args):
        self.__stopTabLogger()
        tabId = int(args.get('tabId', DEFAULT_TAB_ID))
        if tabId != DEFAULT_TAB_ID:
            changeHeaderVisible(True)
        with self.viewModel.transaction() as vm:
            vm.setCurrentTabId(tabId)
            tabs = vm.getTabs()
            tab = tabs[tabId]
            self._activeTab = tab.getType()
        _, tabType = self._getCurrentTabLoggingTypes()
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, item=tabType.value, parentScreen=EpicBattleLogKeys.CONTAINER_VIEW)
        self.__startTabLogger()

    def __startTabLogger(self):
        self.__uiEpicBattleLogger.startAction(EpicBattleLogActions.VIEW_WATCHED.value)

    def __stopTabLogger(self):
        viewType, _ = self._getCurrentTabLoggingTypes()
        self.__uiEpicBattleLogger.stopAction(EpicBattleLogActions.VIEW_WATCHED.value, viewType.value, EpicBattleLogKeys.CONTAINER_VIEW.value, timeLimit=self.__uiEpicBattleLogger.TIME_LIMIT)

    def __onClose(self):
        changeHeaderVisible(True)
        self.destroyWindow()
        showHangar()

    def __onInfo(self):
        showFrontlineInfoWindow()


def changeHeaderVisible(isVisible):
    g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL if isVisible else HeaderMenuVisibilityState.ONLINE_COUNTER}), EVENT_BUS_SCOPE.LOBBY)
