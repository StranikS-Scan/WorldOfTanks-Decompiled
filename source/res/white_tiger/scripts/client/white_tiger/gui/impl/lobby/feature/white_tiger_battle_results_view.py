# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/feature/white_tiger_battle_results_view.py
import logging
from constants import ARENA_BONUS_TYPE, PremiumConfigs
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from white_tiger.gui.impl.gen.view_models.views.lobby.feature.battle_results.white_tiger_results_view_model import WhiteTigerResultsViewModel, Tab
from white_tiger.gui.impl.lobby.feature import WHITE_TIGER_LOCK_SOURCE_NAME
from gui.ClientUpdateManager import g_clientUpdateManager
from white_tiger.gui.battle_results.base_constants import PresenterUpdateTypes
from gui.battle_results.presenters.wrappers import ifPresenterAvailable
from gui.impl.backport import BackportContextMenuWindow
from gui.impl.gen import R
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from white_tiger.gui.impl.lobby.base_view import BaseView
from gui.impl.pub import WindowImpl
from gui.shared import g_eventBus, events
from gui.shared.lock_overlays import lockNotificationManager
from helpers import dependency, server_settings
from white_tiger.gui.shared.tooltips import TooltipType
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IGameSessionController, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from gui.sounds.ambients import BattleResultsEnv
from gui.impl.gen.view_models.views.lobby.battle_results.team_stats_model import SortingOrder
_logger = logging.getLogger(__name__)

class WhiteTigerBattleResultsWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        self.__background_alpha__ = 1.0
        super(WhiteTigerBattleResultsWindow, self).__init__(content=WhiteTigerBattleResultsView(**kwargs), wndFlags=WindowFlags.WINDOW, layer=layer)


class WhiteTigerBattleResultsView(BaseView):
    __slots__ = ('__arenaUniqueID', '__presenter', '__tooltipData')
    __battleResults = dependency.descriptor(IBattleResultsService)
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __gameSession = dependency.descriptor(IGameSessionController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __wotPlusController = dependency.descriptor(IWotPlusController)
    __sound_env__ = BattleResultsEnv

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.white_tiger.mono.lobby.battle_results_screen())
        settings.flags = ViewFlags.VIEW
        settings.model = WhiteTigerResultsViewModel()
        super(WhiteTigerBattleResultsView, self).__init__(settings)
        arenaUniqueID = kwargs.get('arenaUniqueID', None)
        if not arenaUniqueID:
            _logger.error('[WhiteTigerBattleResultsView] Value of arenaUniqueID is invalid')
        self.__arenaUniqueID = arenaUniqueID
        self.__presenter = self.__battleResults.getPresenter(self.__arenaUniqueID)
        self.__tooltipData = {}
        return

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

    @property
    def viewModel(self):
        return super(WhiteTigerBattleResultsView, self).getViewModel()

    def __onViewLoaded(self):
        g_eventBus.handleEvent(events.ViewReadyEvent(self.layoutID))

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            databaseID = int(event.getArgument('databaseID', default=-1))
            if databaseID == self.__connectionMgr.databaseID:
                return
            vehicleCD = event.getArgument('vehicleCD')
            contextMenuData = self.__presenter.getBackportContextMenuData(databaseID, vehicleCD)
            if contextMenuData is not None:
                window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
                window.load()
                return window
        return super(WhiteTigerBattleResultsView, self).createContextMenu(event)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(WhiteTigerBattleResultsView, self).createToolTip(event)

    @ifPresenterAvailable()
    def createToolTipContent(self, event, contentID):
        from gui.impl.lobby.tooltips.battle_stats_tooltip_view import BattleResultsStatsTooltipView
        from white_tiger.gui.impl.lobby.tooltips.battle_results_economic_tooltip_view import BattleResultsEconomicTooltipView
        if contentID == R.views.white_tiger.mono.lobby.tooltips.battle_results_economic_tooltip():
            rewardType = event.getArgument('rewardType')
            return BattleResultsEconomicTooltipView(self.__arenaUniqueID, rewardType)
        if contentID == R.views.lobby.tooltips.BattleResultsStatsTooltipView():
            paramType = event.getArgument('paramType')
            return BattleResultsStatsTooltipView(self.__arenaUniqueID, paramType, TooltipType.WHITE_TIGER_EFFICIENCY_PARAMETER)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def _initialize(self, *args, **kwargs):
        super(WhiteTigerBattleResultsView, self)._initialize(*args, **kwargs)
        self.suspendLobbyHeader(self.uniqueID)
        results = self.__presenter.getResults()
        if results.reusable.personal.avatar.hasPenalties():
            lockNotificationManager(False, source=WHITE_TIGER_LOCK_SOURCE_NAME, releasePostponed=True)

    def _finalize(self):
        lockNotificationManager(False, source=WHITE_TIGER_LOCK_SOURCE_NAME, releasePostponed=True)
        self.resumeLobbyHeader(self.uniqueID)
        self.__presenter = None
        self.__arenaUniqueID = None
        self.__tooltipData = None
        self.__removeListeners()
        super(WhiteTigerBattleResultsView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.premiumPlus.onPremiumXpBonusApplied, self.__onXpBonusApplied),
         (self.viewModel.teamStats.onStatsSorted, self.__onTeamStatsSorted),
         (self.viewModel.onTabChanged, self.__onTabChanged),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),
         (self.__wotPlusController.onDataChanged, self.__onWotPlusChange),
         (self.__gameSession.onPremiumTypeChanged, self.__onXpBonusStatusChanged))

    def _onLoading(self, *args, **kwargs):
        super(WhiteTigerBattleResultsView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        with self.viewModel.transaction() as model:
            self.__presenter.packModel(model, tooltipData=self.__tooltipData)

    def __addListeners(self):
        g_eventBus.addListener(events.LobbySimpleEvent.PREMIUM_XP_BONUS_CHANGED, self.__onXpBonusApplyStatusChanged)
        g_clientUpdateManager.addCallbacks({'stats.applyAdditionalXPCount': self.__onXpBonusStatusChanged,
         'stats.applyAdditionalWoTPlusXPCount': self.__onXpBonusStatusChanged})

    def __removeListeners(self):
        g_eventBus.removeListener(events.LobbySimpleEvent.PREMIUM_XP_BONUS_CHANGED, self.__onXpBonusApplyStatusChanged)
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onClose(self):
        self.destroyWindow()

    def __onTeamStatsSorted(self, event):
        column = event.get('column')
        sortDirection = event.get('sortDirection')
        with self.viewModel.teamStats.transaction() as model:
            model.setSortingColumn(column)
            model.setSortingOrder(SortingOrder(sortDirection))
        self.__battleResults.saveStatsSorting(ARENA_BONUS_TYPE.WHITE_TIGER, column, sortDirection)

    def __onTabChanged(self, event):
        tabID = event.get('tabId')
        if tabID is not None and int(tabID) == Tab.PERSONAL:
            self.__onXpBonusStatusChanged()
        return

    def __onXpBonusApplied(self):
        self.__battleResults.applyAdditionalBonus(self.__arenaUniqueID)

    def __onXpBonusApplyStatusChanged(self, event):
        with self.viewModel.transaction() as model:
            self.__presenter = self.__battleResults.getPresenter(self.__arenaUniqueID)
            self.__presenter.updateModel(PresenterUpdateTypes.XP_BONUS, model, event.ctx, isFullUpdate=False)

    def __onXpBonusStatusChanged(self, _=None):
        with self.viewModel.transaction() as model:
            self.__presenter.updateModel(PresenterUpdateTypes.XP_BONUS, model, isFullUpdate=False)

    @server_settings.serverSettingsChangeListener(PremiumConfigs.DAILY_BONUS)
    def __onServerSettingsChanged(self, _):
        with self.viewModel.transaction() as model:
            self.__presenter.updateModel(PresenterUpdateTypes.XP_BONUS, model)

    def __onWotPlusChange(self, data):
        if 'isEnabled' not in data:
            return
        with self.viewModel.transaction() as model:
            self.__presenter.updateModel(PresenterUpdateTypes.XP_BONUS, model, isFullUpdate=False)
