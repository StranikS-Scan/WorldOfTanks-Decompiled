# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_break_filter_popover.py
from frameworks.wulf.gui_constants import ViewFlags
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.new_year.views.new_year_break_filter_popover_model import NewYearBreakFilterPopoverModel
from gui.impl.gen.view_models.ui_kit.button_model import ButtonModel
from gui.impl.pub import PopOverViewImpl
from helpers import int2roman
from items import ny19
from items.components.ny_constants import TOY_TYPES, TOY_TYPE_IDS_BY_NAME
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events

class NewYearBreakFilterPopover(PopOverViewImpl):
    __slots__ = ('__toysFilterInfo',)

    def __init__(self, toysFilterInfo):
        super(NewYearBreakFilterPopover, self).__init__(R.views.newYearBreakFilterPopover, ViewFlags.VIEW, NewYearBreakFilterPopoverModel)
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
        with self.viewModel.transaction() as model:
            levels = model.levelBtns.getItems()
            for idx in xrange(ny19.CONSTS.MAX_COLLECTION_LEVEL):
                level = ButtonModel()
                level.setRawLabel(int2roman(idx + 1))
                levels.addViewModel(level)

            typeDecorations = model.typeDecorationBtns.getItems()
            for decorationType in TOY_TYPES:
                typeDecoration = ButtonModel()
                typeDecoration.setIcon(R.images.gui.maps.icons.new_year.decorationTypes.filter.dyn(decorationType))
                typeDecorations.addViewModel(typeDecoration)

            toyTypes = self.__toysFilterInfo.toyTypes
            if toyTypes is not None:
                decorationTypeIndices = model.typeDecorationBtns.getSelectedIndices()
                for toyType in toyTypes:
                    decorationTypeIndices.addNumber(TOY_TYPE_IDS_BY_NAME[toyType])

                decorationTypeIndices.invalidate()
            toysRanks = self.__toysFilterInfo.toyRanks
            if toysRanks is not None:
                ranksIndices = model.levelBtns.getSelectedIndices()
                for toyRank in toysRanks:
                    ranksIndices.addNumber(toyRank - 1)

                ranksIndices.invalidate()
        return

    def _finalize(self):
        self.viewModel.levelBtns.onSelectionChanged -= self.__onFilterLevelsChanged
        self.viewModel.typeDecorationBtns.onSelectionChanged -= self.__onFilterTypesChanged

    def __onFilterLevelsChanged(self, _=None):
        self.__onFilterChanged()

    def __onFilterTypesChanged(self, _=None):
        self.__onFilterChanged()

    def __onFilterChanged(self):
        toysTypes = [ TOY_TYPES[i] for i in self.viewModel.typeDecorationBtns.getSelectedIndices() ]
        toysRanks = [ i + 1 for i in self.viewModel.levelBtns.getSelectedIndices() ]
        g_eventBus.handleEvent(events.NewYearEvent(events.NewYearEvent.ON_BREAK_TOYS_FILTER_APPLIED, ctx={'toysTypes': toysTypes,
         'toysRanks': toysRanks}), scope=EVENT_BUS_SCOPE.LOBBY)
