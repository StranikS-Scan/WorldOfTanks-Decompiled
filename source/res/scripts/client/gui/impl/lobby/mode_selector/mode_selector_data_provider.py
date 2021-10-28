# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/mode_selector_data_provider.py
import logging
from collections import defaultdict
import typing
from Event import SafeEvent
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.bootcamp_mode_selector_item import BootcampModeSelectorItem
from gui.impl.lobby.mode_selector.items.epic_mode_selector_item import EpicModeSelectorItem
from gui.impl.lobby.mode_selector.items.event_battle_mode_selector_item import EventModeSelectorItem
from gui.impl.lobby.mode_selector.items.mapbox_mode_selector_item import MapboxModeSelectorItem
from gui.impl.lobby.mode_selector.items.random_mode_selector_item import RandomModeSelectorItem
from gui.impl.lobby.mode_selector.items.ranked_mode_selector_item import RankedModeSelectorItem
from gui.impl.lobby.mode_selector.items.spec_mode_selector_item import SpecModeSelectorItem
from gui.impl.lobby.mode_selector.items.strongholds_mode_selector_item import StrongholdsModeSelectorItem
from gui.impl.lobby.mode_selector.items.trainings_mode_selector_item import TrainingsModeSelectorItem
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
if typing.TYPE_CHECKING:
    from typing import Dict, Type, List, Optional
    from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import _SelectorItem, _BattleSelectorItems
    from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorItem
_logger = logging.getLogger(__name__)
_modeSelectorLegacyItemByModeName = {PREBATTLE_ACTION_NAME.RANDOM: RandomModeSelectorItem,
 PREBATTLE_ACTION_NAME.RANKED: RankedModeSelectorItem,
 PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST: StrongholdsModeSelectorItem,
 PREBATTLE_ACTION_NAME.SPEC_BATTLES_LIST: SpecModeSelectorItem,
 PREBATTLE_ACTION_NAME.TRAININGS_LIST: TrainingsModeSelectorItem,
 PREBATTLE_ACTION_NAME.MAPBOX: MapboxModeSelectorItem,
 PREBATTLE_ACTION_NAME.EPIC: EpicModeSelectorItem,
 PREBATTLE_ACTION_NAME.EVENT_BATTLE: EventModeSelectorItem}

def _getModeSelectorLegacyItem(selectorItem):
    modeName = selectorItem.getData()
    if not selectorItem.isVisible():
        return None
    else:
        return _modeSelectorLegacyItemByModeName.get(modeName)(selectorItem) if modeName in _modeSelectorLegacyItemByModeName else ModeSelectorLegacyItem(selectorItem)


def _getModeSelectorItems():
    modeSelectorItemList = [BootcampModeSelectorItem()]
    itemList = battle_selector_items.getItems()
    modeSelectorItemList.extend([ _getModeSelectorLegacyItem(item) for item in itemList.allItems ])
    return [ item for item in modeSelectorItemList if item ]


class ModeSelectorDataProvider(IGlobalListener):
    __slots__ = ('onListChanged', '__items')
    MAX_COLUMN_SIZE = 6

    def __init__(self):
        super(ModeSelectorDataProvider, self).__init__()
        self.onListChanged = SafeEvent()
        self.__items = []
        self.updateItems(_getModeSelectorItems())
        self.startGlobalListening()

    @property
    def itemList(self):
        return self.__items

    @property
    def isDemonstrator(self):
        return battle_selector_items.getItems().isDemonstrator

    @property
    def hasNewIndicator(self):
        return battle_selector_items.getItems().hasNewVisible()

    @property
    def isDemoButtonEnabled(self):
        return battle_selector_items.getItems().isDemoButtonEnabled

    @staticmethod
    def select(modeName):
        items = battle_selector_items.getItems()
        items.select(modeName)

    def dispose(self):
        self.stopGlobalListening()
        self.updateItems([])

    def refreshItems(self):
        self.updateItems(_getModeSelectorItems())

    def updateItems(self, newList):
        self._setItems(newList)
        self._updateItemsPosition()
        self._updateSelection()
        self.onListChanged()

    def getItemByIndex(self, index):
        return self.__items[index] if len(self.__items) > index else None

    def onPrbEntitySwitched(self):
        self.updateItems(_getModeSelectorItems())

    def _setItems(self, newList):
        for item in self.__items:
            if item not in newList:
                item.dispose()

        for item in newList:
            if item not in self.__items:
                item.initialize()

        self.__items = newList

    def _updateSelection(self):
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher:
            state = prbDispatcher.getFunctionalState()
            selected = battle_selector_items.getItems().update(state)
            for idx, item in enumerate(self.__items):
                item.viewModel.setIndex(idx)
                if item.isSelectable:
                    isSelected = item.modeName == selected.getData()
                    item.viewModel.setIsSelected(isSelected)

    def _updateItemsPosition(self):
        for item in self.__items:
            item.viewModel.hold()

        counts = defaultdict(int)
        self.__items.sort(key=lambda x: x.priority, reverse=True)
        for item in self.__items:
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

        for item in self.__items:
            item.viewModel.commit()
