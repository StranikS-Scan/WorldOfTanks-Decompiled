# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/widgets/lootbox_entry.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.lootbox_entry_view_model import LootboxEntryViewModel
from gui.impl.lobby.lootbox_system.base.tooltips.entry_point_tooltip import EntryPointTooltip
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency
from last_stand.gui.shared.event_dispatcher import showLootBoxMainView
from skeletons.gui.game_control import ILootBoxSystemController
from last_stand.skeletons.ls_controller import ILSController

class LootBoxEntryView(ViewImpl):
    lsCtrl = dependency.descriptor(ILSController)
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self):
        super(LootBoxEntryView, self).__init__(ViewSettings(R.views.last_stand.lobby.virtual_res.LootboxEntryView(), ViewFlags.VIEW, LootboxEntryViewModel()))

    @property
    def viewModel(self):
        return super(LootBoxEntryView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return EntryPointTooltip(self._lootBoxesEvent) if contentID == R.views.lobby.lootbox_system.tooltips.EntryPointTooltip() else super(LootBoxEntryView, self).createToolTipContent(event, contentID)

    @property
    def _lootBoxesEvent(self):
        return self.lsCtrl.lootBoxesEvent

    @property
    def _isLootBoxesAvailable(self):
        return self.__lootBoxes.isAvailable(self._lootBoxesEvent)

    def _onLoading(self, *args, **kwargs):
        super(LootBoxEntryView, self)._onLoading(*args, **kwargs)
        self.__fillEventInfo()

    def _getEvents(self):
        return ((self.__lootBoxes.onBoxesCountChanged, self.__updateBoxesCount),
         (self.__lootBoxes.onStatusChanged, self.__onLootBoxesStatusChanged),
         (self.__lootBoxes.onBoxesAvailabilityChanged, self.__onAvailabilityChanged),
         (self.viewModel.onEntryClick, self.__onEntryClick))

    def __fillEventInfo(self):
        with self.viewModel.transaction() as vmTx:
            vmTx.setIsEnabled(self._isLootBoxesAvailable)
            self.__updateBoxesCount(model=vmTx)

    def __onLootBoxesStatusChanged(self):
        self.__fillEventInfo()

    def __onAvailabilityChanged(self):
        self.viewModel.setIsEnabled(self._isLootBoxesAvailable)

    @replaceNoneKwargsModel
    def __updateBoxesCount(self, model=None):
        model.setBoxesCount(self.__lootBoxes.getBoxesCount(self._lootBoxesEvent))

    def __onEntryClick(self):
        showLootBoxMainView(self._lootBoxesEvent)
