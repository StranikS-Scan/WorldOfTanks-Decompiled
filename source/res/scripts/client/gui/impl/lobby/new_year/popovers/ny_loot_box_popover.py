# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/popovers/ny_loot_box_popover.py
import typing
from constants import IS_CHINA
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gifts.gifts_common import GiftEventID
from gui.gift_system.constants import HubUpdateReason
from gui.gift_system.mixins import GiftEventHubWatcher
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_loot_box_popover_model import NyLootBoxPopoverModel
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_loot_box_item_popover_model import NyLootBoxItemPopoverModel
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.pub import PopOverViewImpl
from gui.shared import event_dispatcher as shared_events, g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.gui_items.loot_box import GUI_ORDER
from helpers import dependency
from ny_common.settings import NYLootBoxConsts, NY_CONFIG_NAME
from skeletons.gui.game_control import IFestivityController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.ny.loggers import NyLootBoxesPopoverFlowLogger

class NyLootBoxPopoverView(PopOverViewImpl, GiftEventHubWatcher):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _festivityController = dependency.descriptor(IFestivityController)
    __flowLogger = NyLootBoxesPopoverFlowLogger()
    _GIFT_EVENT_ID = GiftEventID.NY_HOLIDAYS

    def __init__(self):
        super(NyLootBoxPopoverView, self).__init__(ViewSettings(R.views.lobby.new_year.popovers.NyLootBoxPopover(), ViewFlags.VIEW, NyLootBoxPopoverModel()))
        self.__lastCount = 0
        self.__isEnabled = True

    @property
    def viewModel(self):
        return super(NyLootBoxPopoverView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.catchGiftEventHub(autoSub=False)
        with self.viewModel.transaction() as tx:
            tx.setIsCnRealm(IS_CHINA)
            self.__updateGiftSystemState()
            self.__initializeLootBoxes()

    def _initialize(self, *args, **kwargs):
        super(NyLootBoxPopoverView, self)._initialize()
        self.catchGiftEventHub()
        self.__isEnabled = self.lobbyContext.getServerSettings().isLootBoxesEnabled()
        self.viewModel.onEventBtnClick += self.__onEventBtnClick
        self.viewModel.onBuyBtnClick += self.__onBuyBtnClick
        self._festivityController.onStateChanged += self.__onStateChange
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self.__lastCount = self.itemsCache.items.tokens.getLootBoxesTotalCount()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        g_eventBus.addListener(events.LootboxesEvent.ON_ENTRY_VIEW_LOADED, self.__onEntryVideoLoaded, scope=EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        self.viewModel.onEventBtnClick -= self.__onEventBtnClick
        self.viewModel.onBuyBtnClick -= self.__onBuyBtnClick
        self._festivityController.onStateChanged -= self.__onStateChange
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        g_eventBus.removeListener(events.LootboxesEvent.ON_ENTRY_VIEW_LOADED, self.__onEntryVideoLoaded, scope=EVENT_BUS_SCOPE.LOBBY)
        self.releaseGiftEventHub()
        super(NyLootBoxPopoverView, self)._finalize()

    def _onGiftHubUpdate(self, reason, _=None):
        if reason == HubUpdateReason.SETTINGS:
            self.__updateGiftSystemState()

    def __onBuyBtnClick(self):
        shared_events.showLootBoxBuyWindow()
        self.__flowLogger.logBuy(currentObject=NewYearNavigation.getCurrentObject())
        self.destroyWindow()

    def __onEventBtnClick(self, args):
        label = args.get('lootBoxType', None)
        shared_events.showLootBoxEntry(label)
        self.__flowLogger.logOpen(currentObject=NewYearNavigation.getCurrentObject())
        self.destroyWindow()
        return

    def __initializeLootBoxes(self):
        boxesList = self.viewModel.getBoxesList()
        for lootBoxType in GUI_ORDER:
            boxesCount = 0
            enabled = False
            for lootBox in self.itemsCache.items.tokens.getLootBoxes().itervalues():
                if lootBox.getType() == lootBoxType:
                    boxesCount += lootBox.getInventoryCount()
                    enabled |= self.lobbyContext.getServerSettings().isLootBoxEnabled(lootBox.getID())

            boxesList.addViewModel(self.__buildLootBoxItem(lootBoxType, boxesCount, enabled))

        boxesList.invalidate()

    def __buildLootBoxItem(self, lootBoxType, lootBoxCount, enabled):
        isExternalBuy = self.lobbyContext.getServerSettings().getLootBoxShop().get(NYLootBoxConsts.SOURCE, NYLootBoxConsts.EXTERNAL) == NYLootBoxConsts.EXTERNAL
        lootBox = NyLootBoxItemPopoverModel()
        lootBox.setCount(lootBoxCount)
        lootBox.setType(lootBoxType)
        lootBox.setIsExternalBuy(isExternalBuy)
        lootBox.setIsEnabled(enabled)
        return lootBox

    def __onCacheResync(self, *_):
        if self.__lastCount != self.itemsCache.items.tokens.getLootBoxesTotalCount():
            self.destroyWindow()

    def __onServerSettingChanged(self, diff):
        if 'lootBoxes_config' in diff or diff.get(NY_CONFIG_NAME, {}).get(NYLootBoxConsts.CONFIG_NAME) is not None:
            self.destroyWindow()
            return
        else:
            if 'isLootBoxesEnabled' in diff:
                enabled = self.lobbyContext.getServerSettings().isLootBoxesEnabled()
                if enabled != self.__isEnabled:
                    self.destroyWindow()
            return

    def __onStateChange(self):
        if not self._festivityController.isEnabled():
            self.destroyWindow()

    def __updateGiftSystemState(self):
        self.viewModel.setIsGiftSystemDisabled(self.isGiftEventDisabled())

    def __onEntryVideoLoaded(self, _=None):
        self.destroyWindow()
