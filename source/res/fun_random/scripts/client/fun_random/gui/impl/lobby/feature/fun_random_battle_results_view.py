# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/feature/fun_random_battle_results_view.py
import logging
from collections import namedtuple
from constants import ARENA_BONUS_TYPE, PremiumConfigs
from frameworks.wulf import ViewFlags, ViewSettings
from fun_random.gui.feature.fun_sounds import FUN_BATTLE_RESULTS_SOUND_SPACE
from fun_random.gui.impl.lobby.common.fun_view_helpers import packBonuses
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_battle_results_view_model import FunBattleResultsViewModel, Tab
from fun_random.gui.impl.lobby.feature import FUN_RANDOM_LOCK_SOURCE_NAME
from fun_random.gui.impl.lobby.tooltips.fun_random_efficiency_parameter_tooltip_view import BattleResultsStatsTooltipView
from fun_random.gui.impl.lobby.tooltips.fun_random_battle_results_economic_tooltip_view import FunRandomBattleResultsEconomicTooltipView
from fun_random.gui.impl.lobby.tooltips.fun_random_loot_box_tooltip_view import FunRandomLootBoxTooltipView
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.battle_results.presenters.base_constants import PresenterUpdateTypes
from gui.battle_results.presenters.wrappers import ifPresenterAvailable
from gui.impl.backport import BackportContextMenuWindow
from gui.impl.gen import R
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus, events
from gui.shared.lock_overlays import lockNotificationManager
from helpers import dependency, server_settings
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IGameSessionController, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)
_RewardsData = namedtuple('_RewardsData', ('tooltips', 'bonuses'))

class FunRandomBattleResultsView(ViewImpl, LobbyHeaderVisibility):
    __slots__ = ('__arenaUniqueID', '__presenter', '__rewardsData')
    _COMMON_SOUND_SPACE = FUN_BATTLE_RESULTS_SOUND_SPACE
    __battleResults = dependency.descriptor(IBattleResultsService)
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __gameSession = dependency.descriptor(IGameSessionController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __wotPlusController = dependency.descriptor(IWotPlusController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.fun_random.lobby.feature.FunRandomBattleResultsView(), flags=ViewFlags.LOBBY_TOP_SUB_VIEW, model=FunBattleResultsViewModel())
        super(FunRandomBattleResultsView, self).__init__(settings)
        arenaUniqueID = kwargs.get('arenaUniqueID', None)
        if not arenaUniqueID:
            _logger.error('[FunRandomBattleResultsView] Value of arenaUniqueID is invalid')
        self.__arenaUniqueID = arenaUniqueID
        self.__presenter = self.__battleResults.getPresenter(self.__arenaUniqueID)
        self.__rewardsData = _RewardsData(tooltips={}, bonuses=[])
        return

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

    @property
    def viewModel(self):
        return super(FunRandomBattleResultsView, self).getViewModel()

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
        return super(FunRandomBattleResultsView, self).createContextMenu(event)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(FunRandomBattleResultsView, self).createToolTip(event)

    @ifPresenterAvailable()
    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.BattleResultsStatsTooltipView():
            paramType = event.getArgument('paramType')
            return BattleResultsStatsTooltipView(self.__arenaUniqueID, paramType)
        elif contentID == R.views.fun_random.lobby.tooltips.FunRandomBattleResultsEconomicTooltipView():
            currencyType = event.getArgument('currencyType')
            return FunRandomBattleResultsEconomicTooltipView(self.__arenaUniqueID, currencyType)
        elif contentID == R.views.fun_random.lobby.tooltips.FunRandomLootBoxTooltipView():
            tooltipData = self.getTooltipData(event)
            lootboxID = tooltipData.specialArgs[0] if tooltipData and tooltipData.specialArgs else None
            if lootboxID:
                return FunRandomLootBoxTooltipView(lootboxID)
            return
        elif contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showCount = max(0, int(event.getArgument('showCount')) - 1)
            bonuses = packBonuses(self.__rewardsData.bonuses, showCount, isSpecial=True)
            if bonuses:
                return AdditionalRewardsTooltip(bonuses)
            return
        else:
            return super(FunRandomBattleResultsView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__rewardsData.tooltips.get(tooltipId)

    def _initialize(self, *args, **kwargs):
        super(FunRandomBattleResultsView, self)._initialize(*args, **kwargs)
        self.suspendLobbyHeader(self.uniqueID)

    def _finalize(self):
        lockNotificationManager(False, source=FUN_RANDOM_LOCK_SOURCE_NAME, releasePostponed=True)
        self.resumeLobbyHeader(self.uniqueID)
        self.__presenter = None
        self.__arenaUniqueID = None
        self.__rewardsData = None
        self.__removeListeners()
        super(FunRandomBattleResultsView, self)._finalize()
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
        super(FunRandomBattleResultsView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        with self.viewModel.transaction() as model:
            self.__presenter.packModel(model, rewardsData=self.__rewardsData)

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
        self.__battleResults.saveStatsSorting(ARENA_BONUS_TYPE.FUN_RANDOM, column, sortDirection)

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
