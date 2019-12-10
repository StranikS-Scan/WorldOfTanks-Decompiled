# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_break_filter_popover.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.ui_kit.button_model import ButtonModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_break_filter_popover_model import NewYearBreakFilterPopoverModel
from gui.impl.pub import PopOverViewImpl
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from helpers import int2roman
from items import new_year
from items.components.ny_constants import ToyTypes
_USUAL_TOY_TYPES_ORDER = (ToyTypes.TOP,
 ToyTypes.GARLAND,
 ToyTypes.BALL,
 ToyTypes.FLOOR,
 ToyTypes.TABLE,
 ToyTypes.KITCHEN,
 ToyTypes.TENT,
 ToyTypes.SCULPTURE,
 ToyTypes.DECORATION,
 ToyTypes.SNOW_ITEM,
 ToyTypes.TREES,
 ToyTypes.GROUND_LIGHT,
 ToyTypes.PYRO)

class NewYearBreakFilterPopover(PopOverViewImpl):
    __slots__ = ('__toysFilterInfo',)

    def __init__(self, toysFilterInfo):
        super(NewYearBreakFilterPopover, self).__init__(ViewSettings(R.views.lobby.new_year.views.new_year_break_filter_popover.NewYearBreakFilterPopover(), flags=ViewFlags.VIEW, model=NewYearBreakFilterPopoverModel()))
        self.__toysFilterInfo = toysFilterInfo

    @property
    def viewModel(self):
        return super(NewYearBreakFilterPopover, self).getViewModel()

    @property
    def isCloseBtnVisible(self):
        return True

    def _initialize(self, *args, **kwargs):
        self.viewModel.levelBtns.onSelectionChanged += self.__onFilterLevelsChanged
        self.viewModel.typeDecorationBtns.onSelectionChanged += self.__onFilterTypesChanged
        self.viewModel.megaDecorationBtn.onSelectionChanged += self.__onFilterMegaChanged
        with self.viewModel.transaction() as model:
            levels = model.levelBtns
            toyTypes = self.__toysFilterInfo.toyTypes
            for idx in xrange(new_year.CONSTS.MAX_COLLECTION_LEVEL):
                level = ButtonModel()
                level.setRawLabel(int2roman(idx + 1))
                selected = self.__toysFilterInfo.toyRanks is not None and idx + 1 in self.__toysFilterInfo.toyRanks
                levels.addViewModel(level, selected)

            typeDecorations = model.typeDecorationBtns
            for decorationType in _USUAL_TOY_TYPES_ORDER:
                typeDecoration = ButtonModel()
                typeDecoration.setIcon(R.images.gui.maps.icons.new_year.decorationTypes.filter.dyn(decorationType)())
                typeDecoration.setLabel(R.strings.ny.decorationTypes.dyn(decorationType)())
                selected = toyTypes is not None and decorationType in toyTypes
                typeDecorations.addViewModel(typeDecoration, selected)

            megaDecoration = ButtonModel()
            megaDecoration.setIcon(R.images.gui.maps.icons.new_year.decorationTypes.filter.mega())
            selected = toyTypes is not None and reduce(lambda prev, cur: prev and cur, [ t in toyTypes for t in ToyTypes.MEGA ])
            model.megaDecorationBtn.addViewModel(megaDecoration, selected)
        return

    def _finalize(self):
        self.viewModel.levelBtns.onSelectionChanged -= self.__onFilterLevelsChanged
        self.viewModel.megaDecorationBtn.onSelectionChanged -= self.__onFilterMegaChanged
        self.viewModel.typeDecorationBtns.onSelectionChanged -= self.__onFilterTypesChanged

    def __onFilterLevelsChanged(self, _=None):
        self.__onFilterChanged()

    def __onFilterTypesChanged(self, _=None):
        self.__onFilterChanged()

    def __onFilterMegaChanged(self, _=None):
        self.__onFilterChanged()

    def __onFilterChanged(self):
        toysTypes = [ _USUAL_TOY_TYPES_ORDER[i] for i in self.viewModel.typeDecorationBtns.getSelectedIndices() ] + (list(ToyTypes.MEGA) if self.viewModel.megaDecorationBtn.getSelectedIndices() else [])
        toysRanks = [ i + 1 for i in self.viewModel.levelBtns.getSelectedIndices() ]
        g_eventBus.handleEvent(events.NewYearEvent(events.NewYearEvent.ON_BREAK_TOYS_FILTER_APPLIED, ctx={'toysTypes': toysTypes,
         'toysRanks': toysRanks}), scope=EVENT_BUS_SCOPE.LOBBY)
