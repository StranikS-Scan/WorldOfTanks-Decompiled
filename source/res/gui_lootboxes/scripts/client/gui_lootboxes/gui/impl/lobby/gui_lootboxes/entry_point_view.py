# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/entry_point_view.py
from account_helpers.AccountSettings import LOOT_BOXES_VIEWED_COUNT, LOOT_BOXES_KEY_VIEWED_COUNT, LOOT_BOXES_VIEWED_HAS_INFINITE
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui_lootboxes.gui.shared.event_dispatcher import showStorageView
from gui.impl.gen import R
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.entry_point_view_model import EntryPointViewModel
from gui.impl.pub import ViewImpl
from gui.limited_ui.lui_rules_storage import LuiRules
from helpers import dependency
from skeletons.gui.game_control import IGuiLootBoxesController, ILimitedUIController
from skeletons.gui.hangar import ICarouselEventEntry
_ENABLED_PRE_QUEUES = (QUEUE_TYPE.RANDOMS, QUEUE_TYPE.VERSUS_AI)

class LootBoxesEntryPointWidget(ViewImpl, ICarouselEventEntry):
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)

    def __init__(self):
        super(LootBoxesEntryPointWidget, self).__init__(ViewSettings(R.views.gui_lootboxes.lobby.gui_lootboxes.EntryPointView(), ViewFlags.VIEW, EntryPointViewModel()))

    @property
    def viewModel(self):
        return super(LootBoxesEntryPointWidget, self).getViewModel()

    @staticmethod
    def getIsActive(state):
        limitedUIController = dependency.instance(ILimitedUIController)
        guiLootBoxes = dependency.instance(IGuiLootBoxesController)
        isEnabled = guiLootBoxes is not None and guiLootBoxes.isEnabled()
        isRuleCompleted = limitedUIController.isRuleCompleted(LuiRules.GUI_LOOTBOXES_ENTRY_POINT)
        return isEnabled and isRuleCompleted and (any((state.isInPreQueue(preQueue) for preQueue in _ENABLED_PRE_QUEUES)) or state.isInUnit(PREBATTLE_TYPE.SQUAD))

    def _onLoading(self, *args, **kwargs):
        super(LootBoxesEntryPointWidget, self)._onLoading(*args, **kwargs)
        self.viewModel.setIsLootBoxesEnabled(self.__guiLootBoxes.isLootBoxesAvailable())
        self.__updateModel(self.__guiLootBoxes.getBoxesCount())

    def _getEvents(self):
        return ((self.__guiLootBoxes.onBoxesCountChange, self.__updateBoxesCount),
         (self.__guiLootBoxes.onAvailabilityChange, self.__onAvailabilityChange),
         (self.viewModel.onOpenStorage, self.__onOpenStorage),
         (self.__guiLootBoxes.onKeysUpdate, self.__onKeysUpdate))

    def __onOpenStorage(self):
        if self.__guiLootBoxes.isLootBoxesAvailable():
            showStorageView()
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
