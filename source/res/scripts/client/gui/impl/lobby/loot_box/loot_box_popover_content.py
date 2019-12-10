# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_popover_content.py
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.lootboxes.components.loot_box_popover_content_model import LootBoxPopoverContentModel
from gui.impl.gen.view_models.views.lobby.lootboxes.components.loot_box_popover_renderer_model import LootBoxPopoverRendererModel
from gui.impl.pub import PopOverViewImpl
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items.loot_box import NewYearLootBoxes, GUI_ORDER
from helpers import dependency
from ny_common.settings import NYLootBoxConsts, NY_CONFIG_NAME
from skeletons.gui.game_control import IFestivityController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class LootBoxPopoverContent(PopOverViewImpl):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _festivityController = dependency.descriptor(IFestivityController)
    __slots__ = ('__lastCount', '__isEnabled')

    def __init__(self):
        super(LootBoxPopoverContent, self).__init__(ViewSettings(R.views.lobby.loot_box.loot_box_popover_content.LootBoxPopoverContent(), ViewFlags.VIEW, LootBoxPopoverContentModel()))
        self.__lastCount = 0
        self.__isEnabled = True

    @property
    def viewModel(self):
        return super(LootBoxPopoverContent, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(LootBoxPopoverContent, self)._initialize()
        self.__isEnabled = self.lobbyContext.getServerSettings().isLootBoxesEnabled()
        self.__initializeLootBoxes()
        self.viewModel.onEventBtnClick += self.__onEventBtnClick
        self.viewModel.onBuyBtnClick += self.__onBuyBtnClick
        self._festivityController.onStateChanged += self.__onStateChange
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self.__lastCount = self.itemsCache.items.tokens.getLootBoxesTotalCount()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged

    def _finalize(self):
        self.viewModel.onEventBtnClick -= self.__onEventBtnClick
        self._festivityController.onStateChanged -= self.__onStateChange
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(LootBoxPopoverContent, self)._finalize()

    def __onBuyBtnClick(self):
        shared_events.showLootBoxBuyWindow()
        self.destroyWindow()

    def __onEventBtnClick(self, args):
        label = args.get('label', None)
        shared_events.showLootBoxEntry(label)
        return

    def __initializeLootBoxes(self):
        for lootBoxType in GUI_ORDER:
            boxesCount = 0
            for lootBox in self.itemsCache.items.tokens.getLootBoxes().itervalues():
                if lootBox.getType() == lootBoxType:
                    boxesCount += lootBox.getInventoryCount()

            self.__addLootBox(lootBoxType, boxesCount)

    def __addLootBox(self, lootBoxType, lootBoxCount):
        isBrowserIcon = self.lobbyContext.getServerSettings().getLootBoxShop().get(NYLootBoxConsts.SOURCE, NYLootBoxConsts.EXTERNAL) == NYLootBoxConsts.EXTERNAL
        entryList = self.viewModel.getEntryList()
        lootBoxSlot = LootBoxPopoverRendererModel()
        with lootBoxSlot.transaction() as tx:
            tx.setCount(lootBoxCount)
            tx.setLabelStr(lootBoxType)
            tx.setIsOrangeBtn(lootBoxType == NewYearLootBoxes.PREMIUM)
            tx.setIsBrowserIconVisible(isBrowserIcon)
            tx.setIsFestivity(self.__isEnabled)
            tx.setIsEnabled(lootBoxCount > 0)
        entryList.addViewModel(lootBoxSlot)

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
