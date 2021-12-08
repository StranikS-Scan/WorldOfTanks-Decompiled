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
from items.components.ny_constants import TOY_SLOT_USAGE
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
 ToyTypes.FLOOR,
 ToyTypes.KITCHEN,
 ToyTypes.ATTRACTION,
 ToyTypes.PAVILION,
 ToyTypes.GARLAND_FAIR,
 ToyTypes.SCULPTURE,
 ToyTypes.SCULPTURE_LIGHT,
 ToyTypes.KIOSK,
 ToyTypes.PYRO,
 ToyTypes.GARLAND_INSTALLATION)
_TOY_COLLECTIONS_ORDER = ToySettings.MEGA + ToySettings.NEW

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
        self.viewModel.onCollectionTypeSelected += self.__onCollectionTypeSelected
        self.viewModel.onAtmosphereBonusSelected += self.__onAtmosphereBonusSelected
        with self.viewModel.transaction() as model:
            self._fillCollectionTypes(model)
            self._fillToyTypes(model)
            self._fillAtmosphereBonuses(model)

    def _initialize(self, *args, **kwargs):
        g_eventBus.addListener(events.NewYearEvent.ON_BREAK_TOYS_ANIMATION_COMPLETED, self.__onBreakToysAnimationCompleted, scope=EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        self.viewModel.onToyTypeSelected -= self.__onToyTypeSelected
        self.viewModel.onCollectionTypeSelected -= self.__onCollectionTypeSelected
        self.viewModel.onAtmosphereBonusSelected -= self.__onAtmosphereBonusSelected
        g_eventBus.removeListener(events.NewYearEvent.ON_BREAK_TOYS_ANIMATION_COMPLETED, self.__onBreakToysAnimationCompleted, scope=EVENT_BUS_SCOPE.LOBBY)

    def _fillToyTypes(self, model):
        self._fillTypesArrays(_TOY_TYPES_ORDER, self.__selectedToyFilters.toyTypes, model.getToyTypes())

    def _fillCollectionTypes(self, model):
        self._fillTypesArrays(_TOY_COLLECTIONS_ORDER, self.__selectedToyFilters.collectionTypes, model.getCollectionTypes())

    def _fillAtmosphereBonuses(self, model):
        if not self.__nyController.isMaxAtmosphereLevel():
            self._fillTypesArrays([ str(p) for p in self.__getSortedAtmPoints() ], [ str(p) for p in self.__selectedToyFilters.atmosphereBonuses ], model.getAtmosphereBonuses())

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

    def __onAtmosphereBonusSelected(self, args):
        selectedIndex = int(args['index'])
        with self.viewModel.transaction() as tx:
            self._updateSelections(tx.getAtmosphereBonuses(), selectedIndex)
        self.__onFilterChanged()

    def __onFilterChanged(self):
        toysTypes = self.__getSelectedToyFilters(_TOY_TYPES_ORDER, self.viewModel.getToyTypes())
        collectionsTypes = self.__getSelectedToyFilters(_TOY_COLLECTIONS_ORDER, self.viewModel.getCollectionTypes())
        atmosphereBonuses = self.__getSelectedToyFilters(self.__getSortedAtmPoints(), self.viewModel.getAtmosphereBonuses())
        g_eventBus.handleEvent(events.NewYearEvent(events.NewYearEvent.ON_BREAK_TOYS_FILTER_APPLIED, ctx={'toyTypes': toysTypes,
         'collectionTypes': collectionsTypes,
         'atmosphereBonuses': atmosphereBonuses}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __getSortedAtmPoints(self):
        config = self.__lobbyCtx.getServerSettings().getNewYearGeneralConfig()
        points = set()
        for isMega in (True, False):
            for toyUsage in (TOY_SLOT_USAGE.PURE, TOY_SLOT_USAGE.USED):
                for slotUsage in (TOY_SLOT_USAGE.PURE, TOY_SLOT_USAGE.USED):
                    value = config.getAtmPointsConfigValue(isMega, toyUsage, slotUsage)
                    if value != TOY_SLOT_USAGE.POINTS_MARK_FORBIDDEN:
                        points.add(value)

        return sorted(points)

    def __onBreakToysAnimationCompleted(self, event):
        if event.ctx['totalToyCount'] == 0:
            self.destroyWindow()

    @staticmethod
    def __getSelectedToyFilters(order, buttons):
        return [ order[i] for i, b in enumerate(buttons) if b.getIsSelected() ]
