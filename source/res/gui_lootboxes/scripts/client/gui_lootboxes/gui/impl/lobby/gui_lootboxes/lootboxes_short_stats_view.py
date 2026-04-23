# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/lootboxes_short_stats_view.py
import logging
from account_helpers.AccountSettings import LOOT_BOXES_SHORT_STAT_STATE
from frameworks.wulf import ViewSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.event_dispatcher import showVehiclePreview, showHangar, selectVehicleInHangar
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootboxes_short_stats_view_model import LootboxesShortStatsViewModel, TabState
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.deadline_tooltip import DeadlineTooltip
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.other_rewards_tooltip import OtherRewardsTooltip
from gui_lootboxes.gui.shared.event_dispatcher import showLootBoxesFullStatsWindow, showStorageView
from gui_lootboxes.gui.shared.gui_helpers import fillStatisticModel
from gui_lootboxes.skeletons.statistic_lootbox_controller import IStatisticLootBoxController
from helpers import dependency
from skeletons.gui.game_control import IGuiLootBoxesController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
TAB_STATES = (TabState.SINGLE, TabState.ALL)

class LootBoxesShortStatsSubview(ViewImpl):
    __slots__ = ('__tooltipData', '__lootbox', '__currentTab', '__singleStatistic', '__allStatistic', '__uiLogger')
    __guiLoader = dependency.descriptor(IGuiLoader)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __statisticCtrl = dependency.descriptor(IStatisticLootBoxController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, uiLogger):
        settings = ViewSettings(R.views.gui_lootboxes.lobby.gui_lootboxes.LootBoxesShortStatsView())
        settings.model = LootboxesShortStatsViewModel()
        self.__tooltipData = {}
        self.__lootbox = None
        self.__currentTab = None
        self.__singleStatistic = None
        self.__allStatistic = None
        self.__uiLogger = uiLogger
        super(LootBoxesShortStatsSubview, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(LootBoxesShortStatsSubview, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.DeadlineTooltip():
            return DeadlineTooltip()
        if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.OtherRewardsTooltip():
            type_ = event.getArgument('type')
            return OtherRewardsTooltip(type_)
        return super(LootBoxesShortStatsSubview, self).createToolTipContent(event, contentID)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(LootBoxesShortStatsSubview, self).createToolTip(event)

    def getTooltipData(self, event):
        index = event.getArgument('tooltipId')
        return self.__tooltipData.get(index, None)

    def _onLoading(self, *args, **kwargs):
        super(LootBoxesShortStatsSubview, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__setInitialTab(model)

    def __setInitialTab(self, model):
        if self.__currentTab is None:
            tabID = self.__guiLootBoxes.getSetting(LOOT_BOXES_SHORT_STAT_STATE)
            for tab in TAB_STATES:
                if tab.value == tabID:
                    self.__currentTab = tab

        model.setCurrentTab(self.__currentTab)
        return

    @replaceNoneKwargsModel
    def updateStatisticModel(self, lootbox, model=None):
        model.setIsLoading(True)
        self.__tooltipData = {}
        self.__lootbox = lootbox
        if lootbox is not None:
            self.__fillCurrentRewardsModel(model)
            model.setLootBoxName(self.__lootbox.getUserName())
        else:
            self.__guiLootBoxes.setSetting(LOOT_BOXES_SHORT_STAT_STATE, TabState.ALL.value)
            model.setCurrentTab(TabState.ALL)
            self.__currentTab = TabState.ALL
            model.getCurrentRewards().clear()
            model.setLootBoxName('')
        self.__fillAllRewardsModel(model)
        hasVisibleLootBoxes = any((lootbox.isVisibleInStorage() for lootbox in self.__guiLootBoxes.getGuiLootBoxes()))
        model.setHasVisibleLootBoxes(hasVisibleLootBoxes)
        model.setIsLoading(False)
        model.setIsOptDeviceRestored(self.__getOptDevicesRestoreState())
        return

    def __fillCurrentRewardsModel(self, model):
        self.__singleStatistic = self.__statisticCtrl.getMergeStatByLootboxIDs((self.__lootbox.getID(),))
        self.__fillRewardsModel(model.getCurrentRewards(), self.__singleStatistic)

    def __fillAllRewardsModel(self, model):
        self.__allStatistic = self.__statisticCtrl.getFullStatistic()
        self.__fillRewardsModel(model.getAllRewards(), self.__allStatistic)

    def __fillRewardsModel(self, rewardsList, statistic):
        rewardsList.clear()
        rewards = []
        for statType, statValue in statistic.items():
            rewards.extend(getNonQuestBonuses(statType, statValue))

        fillStatisticModel(rewards, rewardsList, self.__lootbox, self.__tooltipData)

    def _getEvents(self):
        return ((self.viewModel.onCloseStat, self.__onCloseStat),
         (self.viewModel.onOpenFullStats, self.__onOpenFullStats),
         (self.viewModel.onTabSwitch, self.__onTabSwitch),
         (self.viewModel.onVehiclePreview, self.__onVehiclePreview))

    def __onCloseStat(self):
        self.getParentView().updateStatFlag(False)

    @args2params(str)
    def __onOpenFullStats(self, category):
        if self.__currentTab == TabState.SINGLE and self.__singleStatistic:
            statistic = self.__singleStatistic
            selectedLootBoxes = [self.__lootbox.getID()]
        else:
            statistic = self.__allStatistic
            selectedLootBoxes = [ lootboxId for lootboxId in self.__statisticCtrl.getLootboxesExpireInfo().keys() ]
        showLootBoxesFullStatsWindow(statistic, category, self.__lootbox, selectedLootBoxes, self.getInitialParentWindow())

    @args2params(TabState)
    def __onTabSwitch(self, currentTab):
        with self.viewModel.transaction() as model:
            self.__currentTab = currentTab
            for tab in TAB_STATES:
                if tab == self.__currentTab:
                    self.__guiLootBoxes.setSetting(LOOT_BOXES_SHORT_STAT_STATE, tab.value)

            model.setCurrentTab(self.__currentTab)

    @args2params(int)
    def __onVehiclePreview(self, vehicleCD):
        vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
        self.destroyWindow()
        self.__closeStorageView()
        if vehicle.isInInventory:
            selectVehicleInHangar(vehicle.intCD)
        else:
            showVehiclePreview(vehicle.intCD, backBtnLabel=backport.text(R.strings.gui_lootboxes.window.lootBoxes.preview()), previewBackCb=LootBoxesShortStatsSubview._backToShortStatisticView, previewAlias=VIEW_ALIAS.VEHICLE_PREVIEW)

    @staticmethod
    def _backToShortStatisticView():
        showHangar()
        showStorageView()

    def __closeStorageView(self):
        view = self.__guiLoader.windowsManager.getViewByLayoutID(R.views.gui_lootboxes.lobby.gui_lootboxes.StorageView())
        if view:
            view.destroyWindow()

    def __getOptDevicesRestoreState(self):
        return self.__lobbyContext.getServerSettings().isOptionalDeviceRestoreEnabled()
