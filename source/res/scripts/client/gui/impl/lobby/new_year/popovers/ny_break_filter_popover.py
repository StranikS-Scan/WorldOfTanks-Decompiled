# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/popovers/ny_break_filter_popover.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_break_filter_button_model import NyBreakFilterButtonModel
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_break_filter_popover_model import NyBreakFilterPopoverModel
from gui.impl.pub import PopOverViewImpl
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from helpers import dependency
from items.components.ny_constants import MAX_TOY_RANK
from items.components.ny_constants import ToySettings, ToyTypes
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from typing import List, Tuple, Union
    from frameworks.wulf import Array
    from gui.impl.lobby.new_year.break_decorations.ny_break_decorations_view import SelectedToyFilters
_TOY_TYPES_ORDER = (ToyTypes.TOP,
 ToyTypes.GARLAND_FIR,
 ToyTypes.BALL,
 ToyTypes.FLOOR)
_TOY_COLLECTIONS_ORDER = (ToySettings.CHRISTMAS,
 ToySettings.FAIRYTALE,
 ToySettings.NEW_YEAR,
 ToySettings.ORIENTAL)

class NyBreakFilterPopoverView(PopOverViewImpl):
    __lobbyCtx = dependency.descriptor(ILobbyContext)
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, selectedToyFilters):
        settings = ViewSettings(R.views.lobby.new_year.popovers.NyBreakFilterPopover())
        settings.model = NyBreakFilterPopoverModel()
        super(NyBreakFilterPopoverView, self).__init__(settings)
        self.__selectedToyFilters = selectedToyFilters

    @property
    def viewModel(self):
        return super(NyBreakFilterPopoverView, self).getViewModel()

    @property
    def isCloseBtnVisible(self):
        return True

    def _onLoading(self, *args, **kwargs):
        self.viewModel.onToyTypeSelected += self.__onToyTypeSelected
        self.viewModel.onToyRankSelected += self.__onToyRankSelected
        self.viewModel.onCollectionTypeSelected += self.__onCollectionTypeSelected
        with self.viewModel.transaction() as model:
            self._fillCollectionTypes(model)
            self._fillToyRanks(model)
            self._fillToyTypes(model)

    def _initialize(self, *args, **kwargs):
        g_eventBus.addListener(events.NewYearEvent.ON_BREAK_TOYS_ANIMATION_COMPLETED, self.__onBreakToysAnimationCompleted, scope=EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        self.viewModel.onToyTypeSelected -= self.__onToyTypeSelected
        self.viewModel.onToyRankSelected -= self.__onToyRankSelected
        self.viewModel.onCollectionTypeSelected -= self.__onCollectionTypeSelected
        g_eventBus.removeListener(events.NewYearEvent.ON_BREAK_TOYS_ANIMATION_COMPLETED, self.__onBreakToysAnimationCompleted, scope=EVENT_BUS_SCOPE.LOBBY)

    def _fillToyRanks(self, model):
        self._fillTypesArrays([ str(p) for p in self.__getSortedRankPoints() ], [ str(p) for p in self.__selectedToyFilters.toyRanks ], model.getToyRanks())

    def _fillToyTypes(self, model):
        self._fillTypesArrays(_TOY_TYPES_ORDER, self.__selectedToyFilters.toyTypes, model.getToyTypes())

    def _fillCollectionTypes(self, model):
        self._fillTypesArrays(_TOY_COLLECTIONS_ORDER, self.__selectedToyFilters.collectionTypes, model.getCollectionTypes())

    @staticmethod
    def _fillTypesArrays(orderedTypes, selectedTypes, buttons):
        hasSelected = selectedTypes is not None
        for toyType in orderedTypes:
            toyTypeFilterBtn = NyBreakFilterButtonModel()
            toyTypeFilterBtn.setLabel(toyType)
            buttons.addViewModel(toyTypeFilterBtn)
            if hasSelected and toyType in selectedTypes:
                toyTypeFilterBtn.setIsSelected(True)

        buttons.invalidate()
        return

    @staticmethod
    def _updateSelections(buttons, selectedIndex):
        button = buttons.getValue(selectedIndex)
        button.setIsSelected(not button.getIsSelected())

    def __onToyRankSelected(self, args):
        selectedIndex = int(args['index'])
        with self.viewModel.transaction() as tx:
            self._updateSelections(tx.getToyRanks(), selectedIndex)
        self.__onFilterChanged()

    def __onToyTypeSelected(self, args):
        selectedIndex = int(args['index'])
        with self.viewModel.transaction() as tx:
            self._updateSelections(tx.getToyTypes(), selectedIndex)
        self.__onFilterChanged()

    def __onCollectionTypeSelected(self, args):
        selectedIndex = int(args['index'])
        with self.viewModel.transaction() as tx:
            self._updateSelections(tx.getCollectionTypes(), selectedIndex)
        self.__onFilterChanged()

    def __onFilterChanged(self):
        toysTypes = self.__getSelectedToyFilters(_TOY_TYPES_ORDER, self.viewModel.getToyTypes())
        collectionsTypes = self.__getSelectedToyFilters(_TOY_COLLECTIONS_ORDER, self.viewModel.getCollectionTypes())
        toyRanks = self.__getSelectedToyFilters(self.__getSortedRankPoints(), self.viewModel.getToyRanks())
        g_eventBus.handleEvent(events.NewYearEvent(events.NewYearEvent.ON_BREAK_TOYS_FILTER_APPLIED, ctx={'toyRanks': toyRanks,
         'toyTypes': toysTypes,
         'collectionTypes': collectionsTypes}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __getSortedRankPoints(self):
        return [ i + 1 for i in range(0, MAX_TOY_RANK) ]

    def __onBreakToysAnimationCompleted(self, event):
        if event.ctx['totalToyCount'] == 0:
            self.destroyWindow()

    @staticmethod
    def __getSelectedToyFilters(order, buttons):
        return [ order[i] for i, b in enumerate(buttons) if b.getIsSelected() ]
