# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/popovers/ny_loot_box_popover.py
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_loot_box_popover_model import NyLootBoxPopoverModel
from gui.impl.pub import PopOverViewImpl
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.game_control import IFestivityController, IGuiLootBoxesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.impl.lobby.new_year.tooltips.ny_shop_unavailable_tooltip import NyShopUnavailableTooltip
from helpers.server_settings import GUI_LOOT_BOXES_CONFIG
from account_helpers.AccountSettings import LOOT_BOXES_VIEWED_COUNT

def _getDefaultReturnPlace():
    from gui_lootboxes.gui.storage_context.context import ReturnPlaces
    return ReturnPlaces.TO_HANGAR


class NyLootBoxPopoverView(PopOverViewImpl):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _festivityController = dependency.descriptor(IFestivityController)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)

    def __init__(self, returnPlace=None):
        super(NyLootBoxPopoverView, self).__init__(ViewSettings(R.views.lobby.new_year.popovers.NyLootBoxPopover(), ViewFlags.VIEW, NyLootBoxPopoverModel()))
        self.__lastCount = 0
        self.__isEnabled = True
        self.__returnPlace = returnPlace if returnPlace is not None else _getDefaultReturnPlace()
        return

    @property
    def viewModel(self):
        return super(NyLootBoxPopoverView, self).getViewModel()

    def createToolTipContent(self, event, ctID):
        return NyShopUnavailableTooltip() if ctID == R.views.lobby.new_year.tooltips.NyShopUnavailableTooltip() else None

    def _initialize(self, *args, **kwargs):
        super(NyLootBoxPopoverView, self)._initialize()
        self.__isBuyAvailable = self.__guiLootBoxes.isBuyAvailable()
        with self.viewModel.transaction():
            self.viewModel.setIsBuyAvailable(self.__isBuyAvailable)
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
        super(NyLootBoxPopoverView, self)._finalize()

    def __onBuyBtnClick(self):
        self.__guiLootBoxes.openShop()
        self.destroyWindow()

    def __onEventBtnClick(self):
        from gui_lootboxes.gui.shared.event_dispatcher import showStorageView
        self.__guiLootBoxes.setSetting(LOOT_BOXES_VIEWED_COUNT, self.__guiLootBoxes.getBoxesCount())
        showStorageView(self.__returnPlace)
        self.destroyWindow()

    def __onCacheResync(self, *_):
        if self.__lastCount != self.itemsCache.items.tokens.getLootBoxesTotalCount():
            self.destroyWindow()

    def __onServerSettingChanged(self, diff):
        if not self.__guiLootBoxes.isEnabled():
            self.destroyWindow()
        if 'lootBoxes_config' in diff:
            self.destroyWindow()
            return
        if GUI_LOOT_BOXES_CONFIG in diff:
            available = self.__guiLootBoxes.isBuyAvailable()
            if available != self.__isBuyAvailable:
                self.destroyWindow()

    def __onStateChange(self):
        if not self._festivityController.isEnabled():
            self.destroyWindow()

    def __onEntryVideoLoaded(self, _=None):
        self.destroyWindow()
