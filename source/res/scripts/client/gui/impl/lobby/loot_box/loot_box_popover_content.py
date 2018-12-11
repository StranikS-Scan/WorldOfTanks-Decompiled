# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_popover_content.py
from frameworks.wulf.gui_constants import ViewFlags
from gui.impl.gen.view_models.views.loot_box_view.loot_box_popover_content_model import LootBoxPopoverContentModel
from gui.impl.gen.view_models.views.loot_box_view.loot_box_popover_renderer_model import LootBoxPopoverRendererModel
from gui.impl.gen.resources import R
from gui.impl.pub import PopOverViewImpl
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items.loot_box import NewYearLootBoxes, GUI_ORDER
from gui.server_events import events_dispatcher
from helpers import dependency
from skeletons.gui.game_control import IFestivityController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
BUY_SLOT = 'buySlot'
QUEST_SLOT = 'questSlot'

class LootBoxPopoverContent(PopOverViewImpl):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _festivityController = dependency.descriptor(IFestivityController)
    __slots__ = ('__lastCount', '__isEnabled')

    def __init__(self):
        super(LootBoxPopoverContent, self).__init__(R.views.lootBoxPopoverContent, ViewFlags.VIEW, LootBoxPopoverContentModel)
        self.__lastCount = 0
        self.__isEnabled = True

    @property
    def viewModel(self):
        return super(LootBoxPopoverContent, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(LootBoxPopoverContent, self)._initialize()
        self.__isEnabled = self.lobbyContext.getServerSettings().isLootBoxesEnabled()
        self.__initializeLootBoxes()
        self.__addBuySlot()
        self.viewModel.onEventBtnClick += self.__onEventBtnClick
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

    def __onEventBtnClick(self, args):
        label = args.get('label', None)
        if label == BUY_SLOT:
            shared_events.showLootBoxBuyWindow()
            self.destroyWindow()
        elif label == QUEST_SLOT:
            events_dispatcher.showMissionsCategories()
        else:
            shared_events.showLootBoxEntry(label)
        return

    def __initializeLootBoxes(self):
        for lootBoxType in GUI_ORDER:
            boxesCount = 0
            for lootBox in self.itemsCache.items.tokens.getLootBoxes().itervalues():
                if lootBox.getType() == lootBoxType:
                    boxesCount += lootBox.getInventoryCount()

            if boxesCount > 0:
                self.__addLootBox(lootBoxType, boxesCount)
            if boxesCount == 0 and lootBoxType == NewYearLootBoxes.COMMON:
                self.__addQuestSlot()

    def __addBuySlot(self):
        entryList = self.viewModel.getEntryList()
        buySlot = LootBoxPopoverRendererModel()
        with buySlot.transaction() as tx:
            tx.setLabelStr(BUY_SLOT)
            tx.setIsOrangeBtn(True)
            tx.setBtnLabel(R.strings.lootboxes.buttonLabel.buy)
            tx.setIsEnabled(self.__isEnabled)
        entryList.addViewModel(buySlot)

    def __addLootBox(self, lootBoxType, lootBoxCount):
        entryList = self.viewModel.getEntryList()
        lootBoxSlot = LootBoxPopoverRendererModel()
        with lootBoxSlot.transaction() as tx:
            tx.setCount(lootBoxCount)
            tx.setLabelStr(lootBoxType)
            tx.setIsOrangeBtn(False)
            tx.setBtnLabel(R.strings.lootboxes.buttonLabel.open)
            tx.setIsEnabled(self.__isEnabled)
        entryList.addViewModel(lootBoxSlot)

    def __addQuestSlot(self):
        entryList = self.viewModel.getEntryList()
        questSlot = LootBoxPopoverRendererModel()
        with questSlot.transaction() as tx:
            tx.setLabelStr(QUEST_SLOT)
            tx.setIsOrangeBtn(False)
            tx.setBtnLabel(R.strings.lootboxes.buttonLabel.quest)
            tx.setIsEnabled(self.__isEnabled)
        entryList.addViewModel(questSlot)

    def __onCacheResync(self, *_):
        if self.__lastCount != self.itemsCache.items.tokens.getLootBoxesTotalCount():
            self.destroyWindow()

    def __onServerSettingChanged(self, diff):
        if 'lootBoxes_config' in diff:
            self.destroyWindow()
            return
        if 'isLootBoxesEnabled' in diff:
            enabled = self.lobbyContext.getServerSettings().isLootBoxesEnabled()
            if enabled != self.__isEnabled:
                self.destroyWindow()

    def __onStateChange(self):
        if not self._festivityController.isEnabled():
            self.destroyWindow()
