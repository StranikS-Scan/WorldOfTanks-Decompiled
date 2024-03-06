# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/mode_selector_data_provider.py
import logging
from collections import defaultdict, OrderedDict
import typing
from Event import SafeEvent
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.epic_mode_selector_item import EpicModeSelectorItem
from gui.impl.lobby.mode_selector.items.mapbox_mode_selector_item import MapboxModeSelectorItem
from gui.impl.lobby.mode_selector.items.random_mode_selector_item import RandomModeSelectorItem
from gui.impl.lobby.mode_selector.items.ranked_mode_selector_item import RankedModeSelectorItem
from gui.impl.lobby.mode_selector.items.spec_mode_selector_item import SpecModeSelectorItem
from gui.impl.lobby.mode_selector.items.battle_royale_mode_selector_item import BattleRoyaleModeSelectorItem
from gui.impl.lobby.mode_selector.items.strongholds_mode_selector_item import StrongholdsModeSelectorItem
from gui.impl.lobby.mode_selector.items.trainings_mode_selector_item import TrainingsModeSelectorItem
from gui.impl.lobby.mode_selector.items.comp7_mode_selector_item import Comp7ModeSelectorItem
from gui.impl.lobby.mode_selector.items.winback_mode_selector_item import WinbackModeSelectorItem
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.system_factory import registerModeSelectorItem, collectModeSelectorItem
if typing.TYPE_CHECKING:
    from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import SelectorItem
    from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorItem
_logger = logging.getLogger(__name__)
registerModeSelectorItem(PREBATTLE_ACTION_NAME.RANDOM, RandomModeSelectorItem)
registerModeSelectorItem(PREBATTLE_ACTION_NAME.RANKED, RankedModeSelectorItem)
registerModeSelectorItem(PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST, StrongholdsModeSelectorItem)
registerModeSelectorItem(PREBATTLE_ACTION_NAME.SPEC_BATTLES_LIST, SpecModeSelectorItem)
registerModeSelectorItem(PREBATTLE_ACTION_NAME.TRAININGS_LIST, TrainingsModeSelectorItem)
registerModeSelectorItem(PREBATTLE_ACTION_NAME.MAPBOX, MapboxModeSelectorItem)
registerModeSelectorItem(PREBATTLE_ACTION_NAME.EPIC, EpicModeSelectorItem)
registerModeSelectorItem(PREBATTLE_ACTION_NAME.BATTLE_ROYALE, BattleRoyaleModeSelectorItem)
registerModeSelectorItem(PREBATTLE_ACTION_NAME.COMP7, Comp7ModeSelectorItem)
registerModeSelectorItem(PREBATTLE_ACTION_NAME.WINBACK, WinbackModeSelectorItem)

class ModeSelectorDataProvider(IGlobalListener):
    __slots__ = ('onListChanged', '_items')
    MAX_COLUMN_SIZE = 6

    def __init__(self):
        super(ModeSelectorDataProvider, self).__init__()
        self.onListChanged = SafeEvent()
        self._items = OrderedDict()
        self._initializeModeSelectorItems()
        self._updateItems()
        self.startGlobalListening()

    @property
    def itemList(self):
        return self._items.values()

    @property
    def isDemonstrator(self):
        return battle_selector_items.getItems().isDemonstrator

    @property
    def hasNewIndicator(self):
        return battle_selector_items.getItems().hasNew()

    @property
    def isDemoButtonEnabled(self):
        return battle_selector_items.getItems().isDemoButtonEnabled

    @staticmethod
    def select(modeName):
        items = battle_selector_items.getItems()
        items.select(modeName)

    def dispose(self):
        self.stopGlobalListening()
        self._clearItems()

    def getItemByIndex(self, index):
        items = self.itemList
        return items[index] if len(items) > index else None

    def forceRefresh(self):
        self._clearItems()
        self.__createItems(self.__getItems())
        self._updateItems()

    def onPrbEntitySwitched(self):
        items = self.__getItems()
        self.__createItems(items)
        for nameItem in self._items:
            if not items.get(nameItem) or not items[nameItem].isVisible():
                self._clearItem(self._items.pop(nameItem))

        self._updateItems()

    def _onCardChangeHandler(self, *args, **kwargs):
        self.forceRefresh()

    def _clearItems(self):
        for key in self._items:
            self._clearItem(self._items.pop(key))

    def _clearItem(self, item):
        item.onCardChange -= self._onCardChangeHandler
        item.dispose()

    def _initializeModeSelectorItems(self):
        self.__createItems(self.__getItems())

    @staticmethod
    def _getModeSelectorLegacyItem(modeName, selectorItem):
        return None if selectorItem is not None and not selectorItem.isVisible() else (collectModeSelectorItem(modeName) or ModeSelectorLegacyItem)(selectorItem)

    def _updateItems(self):
        self._updateItemsPosition()
        self._updateSelection()
        self.onListChanged()

    def _updateSelection(self):
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher:
            state = prbDispatcher.getFunctionalState()
            selected = battle_selector_items.getItems().update(state)
            for idx, item in enumerate(self.itemList):
                item.viewModel.setIndex(idx)
                if item.isSelectable:
                    isSelected = item.modeName == selected.getData() or getattr(item, 'isSelected', lambda : False)()
                    item.viewModel.setIsSelected(isSelected)

    def _updateItemsPosition(self):
        self._items = OrderedDict(sorted(self._items.iteritems(), key=lambda x: x[1].priority, reverse=True))
        for item in self.itemList:
            item.viewModel.hold()

        counts = defaultdict(int)
        for item in self.itemList:
            columnId = item.preferredColumn
            while counts[columnId] >= self.MAX_COLUMN_SIZE and columnId != ModeSelectorColumns.COLUMN_0:
                _logger.warning("Incorrect settings. Can't add item %s to the column %s. Max column size has been reached. Move it to the previous column", item.modeName, columnId)
                columnId = columnId - 1

            item.viewModel.setColumn(columnId)
            counts[columnId] += 1
            item.viewModel.setPriority(item.priority)

        for key, value in counts.iteritems():
            if key == ModeSelectorColumns.COLUMN_0 and value > 1:
                _logger.warning('There must be a sole item in the first column')
            if key != ModeSelectorColumns.COLUMN_0 and value > self.MAX_COLUMN_SIZE:
                _logger.warning('Max column size  %s has been overflown', self.MAX_COLUMN_SIZE)

        for item in self.itemList:
            item.viewModel.commit()

    def __createItems(self, items):
        for modeName in items:
            if modeName not in self._items:
                item = self._getModeSelectorLegacyItem(modeName, items[modeName])
                if item is not None and item.isVisible:
                    self._items[modeName] = item
                    self.__initializeItem(item)

        return

    def __initializeItem(self, item):
        item.initialize()
        item.onCardChange += self._onCardChangeHandler

    @staticmethod
    def __getItems():
        allItems = battle_selector_items.getItems().allItems
        return {nameItem.getData():nameItem for nameItem in allItems}
