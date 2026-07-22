# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/birthday/lootbox_entry_point.py
from account_helpers.AccountSettings import LOOT_BOXES_VIEWED_COUNT, LOOT_BOXES_KEY_VIEWED_COUNT, LOOT_BOXES_VIEWED_HAS_INFINITE
from helpers import dependency
from skeletons.gui.game_control import IGuiLootBoxesController

class LootBoxesEntryPointWidget(object):
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)

    def __init__(self, model):
        super(LootBoxesEntryPointWidget, self).__init__()
        self.viewModel = model

    def onLoading(self):
        self.viewModel.setIsLootBoxesEnabled(self.__guiLootBoxes.isLootBoxesAvailable())
        self.__updateModel(self.__guiLootBoxes.getBoxesCount())

    def getEvents(self):
        return ((self.__guiLootBoxes.onBoxesCountChange, self.__updateBoxesCount),
         (self.__guiLootBoxes.onAvailabilityChange, self.__onAvailabilityChange),
         (self.viewModel.onOpenStorage, self.__onOpenStorage),
         (self.__guiLootBoxes.onKeysUpdate, self.__onKeysUpdate))

    def __onOpenStorage(self):
        from gui_lootboxes.gui.shared.event_dispatcher import showStorageView
        from gui_lootboxes.gui.storage_context.context import ReturnPlaces
        if self.__guiLootBoxes.isLootBoxesAvailable():
            showStorageView(returnPlace=ReturnPlaces.TO_BIRTHDAY)
            self.viewModel.setHasNew(False)
            self.__guiLootBoxes.setSetting(LOOT_BOXES_VIEWED_COUNT, self.__guiLootBoxes.getBoxesCount())
            self.__guiLootBoxes.setSetting(LOOT_BOXES_KEY_VIEWED_COUNT, self.__guiLootBoxes.getBoxKeysCount())
            self.__guiLootBoxes.setSetting(LOOT_BOXES_VIEWED_HAS_INFINITE, self.__guiLootBoxes.hasInfiniteLootboxes())

    def __updateBoxesCount(self, count, *_):
        self.__updateModel(count)

    def __onKeysUpdate(self, *_):
        self.__updateModel(self.__guiLootBoxes.getBoxesCount())

    def __updateModel(self, boxCount):
        lastBoxesViewed = self.__guiLootBoxes.getSetting(LOOT_BOXES_VIEWED_COUNT)
        lastKeysViewed = self.__guiLootBoxes.getSetting(LOOT_BOXES_KEY_VIEWED_COUNT)
        isViewedHasInfinite = self.__guiLootBoxes.getSetting(LOOT_BOXES_VIEWED_HAS_INFINITE)
        keyCount = self.__guiLootBoxes.getBoxKeysCount()
        hasInfinite = self.__guiLootBoxes.hasInfiniteLootboxes()
        hasNew = boxCount > lastBoxesViewed or keyCount > lastKeysViewed or hasInfinite and hasInfinite != isViewedHasInfinite
        with self.viewModel.transaction() as model:
            model.setBoxesCount(boxCount)
            model.setHasNew(hasNew)
            model.setHasInfinite(hasInfinite)

    def __onAvailabilityChange(self, *_):
        self.viewModel.setIsLootBoxesEnabled(self.__guiLootBoxes.isLootBoxesAvailable())
