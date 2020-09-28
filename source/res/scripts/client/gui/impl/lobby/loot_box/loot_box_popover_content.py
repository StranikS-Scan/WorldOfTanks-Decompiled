# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_popover_content.py
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.lootboxes.components.loot_box_popover_content_model import LootBoxPopoverContentModel
from gui.impl.gen.view_models.views.lobby.lootboxes.components.loot_box_popover_renderer_model import LootBoxPopoverRendererModel
from gui.impl.lobby.wt_event.tooltips.wt_event_box_tooltip_view import WtEventBoxTooltipView
from gui.impl.pub import PopOverViewImpl
from gui.shared.event_dispatcher import showWtEventStorageBoxesWindow, showWtEventLootboxOpenWindow
from gui.shared.gui_items.loot_box import EventLootBoxes, GUI_ORDER
from gui.shop import showLootBoxBuyWindow
from helpers import dependency
from skeletons.gui.game_control import IGameEventController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class LootBoxPopoverContent(PopOverViewImpl):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    gameEventCtrl = dependency.descriptor(IGameEventController)
    __slots__ = ('__lastCount', '__isEnabled')

    def __init__(self):
        super(LootBoxPopoverContent, self).__init__(ViewSettings(R.views.lobby.loot_box.loot_box_popover_content.LootBoxPopoverContent(), ViewFlags.VIEW, LootBoxPopoverContentModel()))
        self.__lastCount = 0
        self.__isEnabled = True

    @property
    def viewModel(self):
        return super(LootBoxPopoverContent, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return WtEventBoxTooltipView(event.getArgument('type')) if contentID == R.views.lobby.wt_event.tooltips.WtEventBoxTooltipView() else None

    def _initialize(self, *args, **kwargs):
        super(LootBoxPopoverContent, self)._initialize()
        self.__isEnabled = self.lobbyContext.getServerSettings().isLootBoxesEnabled()
        self.__initializeLootBoxes()
        self.viewModel.onEventBtnClick += self.__onEventBtnClick
        self.viewModel.onBuyBtnClick += self.__onBuyBtnClick
        self.viewModel.onAboutBtnClick += self.__onAboutBtnClick
        self.gameEventCtrl.onEventUpdated += self.__onEventUpdated
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self.__lastCount = self.itemsCache.items.tokens.getLootBoxesTotalCount()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged

    def _finalize(self):
        self.viewModel.onEventBtnClick -= self.__onEventBtnClick
        self.viewModel.onBuyBtnClick -= self.__onBuyBtnClick
        self.viewModel.onAboutBtnClick -= self.__onAboutBtnClick
        self.gameEventCtrl.onEventUpdated -= self.__onEventUpdated
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(LootBoxPopoverContent, self)._finalize()

    def __onBuyBtnClick(self):
        showLootBoxBuyWindow()
        self.destroyWindow()

    def __onEventBtnClick(self, args):
        showWtEventLootboxOpenWindow(boxType=args.get('label'))

    def __onAboutBtnClick(self):
        showWtEventStorageBoxesWindow()
        self.destroyWindow()

    def __initializeLootBoxes(self):
        for lootBoxType in GUI_ORDER:
            boxesCount = 0
            for lootBox in self.itemsCache.items.tokens.getLootBoxes().itervalues():
                if lootBox.getType() == lootBoxType:
                    boxesCount += lootBox.getInventoryCount()

            self.__addLootBox(lootBoxType, boxesCount)

    def __addLootBox(self, lootBoxType, lootBoxCount):
        entryList = self.viewModel.getEntryList()
        lootBoxSlot = LootBoxPopoverRendererModel()
        with lootBoxSlot.transaction() as tx:
            tx.setCount(lootBoxCount)
            tx.setLabelStr(lootBoxType)
            tx.setIsOrangeBtn(lootBoxType == EventLootBoxes.WT_SPECIAL)
            tx.setIsBrowserIconVisible(False)
            tx.setIsFestivity(self.__isEnabled)
            tx.setIsEnabled(lootBoxCount > 0)
        entryList.addViewModel(lootBoxSlot)

    def __onCacheResync(self, *_):
        if self.__lastCount != self.itemsCache.items.tokens.getLootBoxesTotalCount():
            self.destroyWindow()

    def __onServerSettingChanged(self, diff):
        if 'isLootBoxesEnabled' in diff:
            enabled = self.lobbyContext.getServerSettings().isLootBoxesEnabled()
            if enabled != self.__isEnabled:
                self.destroyWindow()

    def __onEventUpdated(self):
        if not self.gameEventCtrl.isEnabled():
            self.destroyWindow()
