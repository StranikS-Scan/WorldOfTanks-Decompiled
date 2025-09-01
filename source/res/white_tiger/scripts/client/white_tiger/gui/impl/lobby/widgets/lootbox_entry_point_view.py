# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/widgets/lootbox_entry_point_view.py
from gui.impl.gen import R
from gui.impl.lobby.lootbox_system.base.tooltips.entry_point_tooltip import EntryPointTooltip
from gui.impl.pub.view_component import ViewComponent
from gui.lootbox_system.base.common import Views, ViewID
from helpers import dependency
from skeletons.gui.game_control import ILootBoxSystemController
from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.lootbox_entry_point_view_model import LootboxEntryPointViewModel

class LootboxEntryView(ViewComponent[LootboxEntryPointViewModel]):
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self, layoutID=R.aliases.white_tiger.shared.LootboxEntryPoint(), **kwargs):
        super(LootboxEntryView, self).__init__(layoutID=layoutID, model=LootboxEntryPointViewModel)

    @property
    def viewModel(self):
        return super(LootboxEntryView, self).getViewModel()

    @property
    def _lootBoxesEvent(self):
        return self.__lootBoxes.mainEntryPoint

    @property
    def _isLootBoxesAvailable(self):
        return self.__lootBoxes.isAvailable(self._lootBoxesEvent)

    def createToolTipContent(self, event, contentID):
        return EntryPointTooltip(self._lootBoxesEvent) if contentID == R.views.mono.lootbox.tooltips.entry_point() else super(LootboxEntryView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(LootboxEntryView, self)._onLoading(*args, **kwargs)
        self._fillEventInfo()

    def _getEvents(self):
        return ((self.__lootBoxes.onBoxesCountChanged, self._updateBoxesCount),
         (self.__lootBoxes.onStatusChanged, self._onLootBoxesStatusChanged),
         (self.__lootBoxes.onBoxesInfoUpdated, self._onLootBoxesStatusChanged),
         (self.__lootBoxes.onBoxesAvailabilityChanged, self._onAvailabilityChanged),
         (self.viewModel.onEntryClick, self._onEntryClick))

    def _fillEventInfo(self):
        with self.viewModel.transaction() as vmTx:
            vmTx.setIsEnabled(self._isLootBoxesAvailable)
            vmTx.setEventName(self._lootBoxesEvent)
            self._updateBoxesCount()

    def _onLootBoxesStatusChanged(self):
        self._fillEventInfo()

    def _onAvailabilityChanged(self):
        self.viewModel.setIsEnabled(self._isLootBoxesAvailable)

    def _updateBoxesCount(self):
        self.viewModel.setBoxesCount(self.__lootBoxes.getBoxesCount(self._lootBoxesEvent))

    def _onEntryClick(self):
        if self._isLootBoxesAvailable:
            Views.load(ViewID.MAIN, eventName=self._lootBoxesEvent)
