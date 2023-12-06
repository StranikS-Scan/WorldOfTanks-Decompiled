# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/lootbox_entry_point/ny_lootbox_entry_point_view.py
from account_helpers.AccountSettings import LOOT_BOXES_VIEWED_COUNT
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.loot_box_entry_point_model import LootBoxEntryPointModel
from gui.impl.pub import ViewImpl
from gui.impl.lobby.new_year.popovers.ny_loot_box_popover import NyLootBoxPopoverView
from gui.limited_ui.lui_rules_storage import LuiRules
from helpers import dependency
from skeletons.gui.game_control import IGuiLootBoxesController, ILimitedUIController
from skeletons.gui.hangar import ICarouselEventEntry
from skeletons.new_year import INewYearController
_ENABLED_PRE_QUEUES = (QUEUE_TYPE.RANDOMS, QUEUE_TYPE.WINBACK, QUEUE_TYPE.VERSUS_AI)

class NyLootBoxesEntryPoint(ViewImpl, ICarouselEventEntry):
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)

    def __init__(self):
        super(NyLootBoxesEntryPoint, self).__init__(ViewSettings(R.views.lobby.new_year.loot_box.LootBoxEntryView(), ViewFlags.VIEW, LootBoxEntryPointModel()))

    @property
    def viewModel(self):
        return super(NyLootBoxesEntryPoint, self).getViewModel()

    @staticmethod
    def getIsActive(state):
        nyController = dependency.instance(INewYearController)
        limitedUIController = dependency.instance(ILimitedUIController)
        guiLootBoxes = dependency.instance(IGuiLootBoxesController)
        isLootboxEnabled = guiLootBoxes is not None and guiLootBoxes.isEnabled()
        isRuleCompleted = limitedUIController.isRuleCompleted(LuiRules.GUI_LOOTBOXES_ENTRY_POINT)
        return isLootboxEnabled and isRuleCompleted and nyController.isEnabled() and (any((state.isInPreQueue(preQueue) for preQueue in _ENABLED_PRE_QUEUES)) or state.isInUnit(PREBATTLE_TYPE.SQUAD))

    def createPopOverContent(self, event):
        return NyLootBoxPopoverView() if event.contentID == R.views.lobby.new_year.popovers.NyLootBoxPopover() else super(NyLootBoxesEntryPoint, self).createPopOverContent(event)

    def _onLoading(self, *args, **kwargs):
        super(NyLootBoxesEntryPoint, self)._onLoading(*args, **kwargs)
        self.viewModel.setIsLootBoxesEnabled(self.__guiLootBoxes.isLootBoxesAvailable())
        self.__updateBoxesCount(self.__guiLootBoxes.getBoxesCount())

    def _getEvents(self):
        return ((self.__guiLootBoxes.onBoxesCountChange, self.__updateBoxesCount), (self.__guiLootBoxes.onAvailabilityChange, self.__onAvailabilityChange))

    def __updateBoxesCount(self, count, *_):
        lastViewed = self.__guiLootBoxes.getSetting(LOOT_BOXES_VIEWED_COUNT)
        with self.viewModel.transaction() as model:
            model.setBoxesCount(count)
            model.setHasNew(count > lastViewed)

    def __onAvailabilityChange(self, *_):
        self.viewModel.setIsLootBoxesEnabled(self.__guiLootBoxes.isLootBoxesAvailable())
