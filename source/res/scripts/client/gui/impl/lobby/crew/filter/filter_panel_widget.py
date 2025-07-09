# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/filter/filter_panel_widget.py
import typing
import Event
import weakref
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer, ViewStatus
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.filter_toggle_group_model import ToggleGroupType
from gui.impl.gen.view_models.views.lobby.crew.filter_panel_widget_model import FilterPanelWidgetModel, FilterPanelType
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanKind
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.crew.filter.state import FilterState
from gui.impl.lobby.crew.popovers.filter_popover_view import FilterPopoverView
from gui.impl.pub import ViewImpl, PopOverWindow
from uilogging.crew.loggers import CrewViewLogger
from uilogging.crew.logging_constants import CrewViewKeys
if typing.TYPE_CHECKING:
    from gui.impl.lobby.crew.filter import FilterGroupSettings as GroupSettings
    from typing import Iterable, Callable, Dict, Union
    OnUpdateState = Callable[[Dict[str, set], str], None]
    FilterGroups = Union[Iterable[GroupSettings], None]

class FilterPanelWidget(ViewImpl):
    LAYOUT_ID = R.views.lobby.crew.widgets.FilterPanelWidget
    __slots__ = ('__state', '__mainFilterSettings', '__popoverTitle', '__isSearchEnabled', '__hasVehicleFilter', '__searchString', '__popoverGroupSettings', '__amountInfo', '__title', '__panelType', '__popoverTooltipHeader', '__popoverTooltipBody', '__searchTooltipBody', '__searchTooltipHeader', '__searchPlaceholder', '__hasDiscountAlert', '__popoverView', 'onPopoverTooltipCreated', '__isSelectedMode', 'onSelectedModeChange', 'onResetSelection', 'onUpdateToggle', '__uiLogger')

    def __init__(self, mainFilterSettings, popoverGroupSettings, popoverTitle, state, **kwargs):
        settings = ViewSettings(self.LAYOUT_ID(), flags=ViewFlags.LOBBY_SUB_VIEW, model=FilterPanelWidgetModel())
        self.__state = state
        self.__isSearchEnabled = kwargs.get('isSearchEnabled', False)
        self.__hasVehicleFilter = kwargs.get('hasVehicleFilter', False)
        self.__mainFilterSettings = mainFilterSettings
        self.__popoverGroupSettings = popoverGroupSettings
        self.__popoverTitle = popoverTitle
        self.__amountInfo = (0, 0)
        self.__title = kwargs.get('title', R.strings.crew.filter.title())
        self.__panelType = kwargs.get('panelType', FilterPanelType.DEFAULT)
        self.__popoverTooltipHeader = kwargs.get('popoverTooltipHeader', R.invalid())
        self.__popoverTooltipBody = kwargs.get('popoverTooltipBody', R.invalid())
        self.__searchPlaceholder = kwargs.get('searchPlaceholder', R.strings.crew.filter.search.placeholder())
        self.__searchTooltipHeader = kwargs.get('searchTooltipHeader', R.strings.crew.filter.search.tooltip.header())
        self.__searchTooltipBody = kwargs.get('searchTooltipBody', '')
        self.__hasDiscountAlert = kwargs.get('hasDiscountAlert', False)
        self.__popoverView = None
        self.onPopoverTooltipCreated = Event.Event()
        self.__isSelectedMode = False
        self.onSelectedModeChange = Event.Event()
        self.onResetSelection = Event.Event()
        self.onUpdateToggle = Event.Event()
        self.__uiLogger = CrewViewLogger(weakref.proxy(self), CrewViewKeys.BARRACKS)
        super(FilterPanelWidget, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(FilterPanelWidget, self).getViewModel()

    def _finalize(self):
        self.__uiLogger.finalize()
        super(FilterPanelWidget, self)._finalize()

    def resetState(self):
        self.__state.clear()

    def resetPopoverFilter(self):
        self.__state.resetPopoverFilter(self.__panelType)
        self.applyStateToModel()

    def updateHasDiscountAlert(self, hasDiscountAlert):
        self.__hasDiscountAlert = hasDiscountAlert

    def updatePopoverGroupSettings(self, popoverGroupSettings):
        self.__popoverGroupSettings = popoverGroupSettings
        if self.__popoverView:
            self.__popoverView.updateGroupSettings(self.__popoverGroupSettings)

    def updateAmountInfo(self, filteredAmount, totalAmount):
        self.__amountInfo = (filteredAmount, totalAmount)
        self.refreshAmountInfo()

    def refreshAmountInfo(self):
        with self.viewModel.transaction() as tx:
            filteredAmount, totalAmount = self.__amountInfo
            tx.amountInfo.setFrom(filteredAmount)
            tx.amountInfo.setTo(totalAmount)

    def applyStateToModel(self):
        if self.__panelType == FilterPanelType.BARRACKS:
            self.__fillBarracksModel()
        self.__fillModel()

    def hasAppliedFilters(self):
        ignoredKey = FilterState.GROUPS.TANKMANKIND.value if self.__panelType == FilterPanelType.BARRACKS else FilterState.GROUPS.LOCATION.value
        for groupID in self.__state:
            if groupID == ignoredKey:
                continue
            if self.__state[groupID]:
                return True

        return len(self.__state.searchString) > 0

    def updateFilterToggleCounter(self, filterId, count):
        with self.viewModel.transaction() as tx:
            filters = tx.filter.getFilters()
            for filterModel in filters:
                if filterModel.getId() == filterId:
                    filterModel.setCounter(count)
                    filters.invalidate()
                    break

        for toggle in self.__mainFilterSettings.toggles:
            if toggle.id == filterId:
                toggle.counter = count
                break

    def createPopOver(self, event):
        if event.contentID == R.views.lobby.crew.popovers.FilterPopoverView():
            content = FilterPopoverView(self.__popoverTitle, self.__popoverGroupSettings, self.__onPopoverStateUpdated, self.__state, self.__hasVehicleFilter, self.hasAppliedFilters, self.__panelType)
            window = PopOverWindow(event, content, self.getParentWindow(), WindowLayer.TOP_WINDOW)
            window.onStatusChanged += self.__onPopoverStatusChanged
            window.load()
            self.__popoverView = content
            self.__popoverView.onTooltipCreated += self.onPopoverTooltipCreated
            return window
        super(FilterPanelWidget, self).createPopOver(event)

    def _getEvents(self):
        return ((self.viewModel.onSearch, self.__onSearch),
         (self.viewModel.onUpdateFilter, self.__onUpdateFilter),
         (self.viewModel.onResetFilter, self.__onResetFilter),
         (self.viewModel.onSelectedModeChange, self.__onSelectedModeChange),
         (self.viewModel.onCancelSelection, self.__onSelectedModeChange))

    def _onLoading(self, *args, **kwargs):
        super(FilterPanelWidget, self)._onLoading(*args, **kwargs)
        self.__fillModel(True)

    def __onPopoverStatusChanged(self, status):
        if status == ViewStatus.DESTROYED:
            self.__popoverView.onTooltipCreated -= self.onPopoverTooltipCreated
            self.__popoverView = None
        return

    @args2params(unicode)
    def __onSearch(self, value):
        self.__state.searchString = value
        self.applyStateToModel()

    @args2params(str, str)
    def __onUpdateFilter(self, groupID, toggleID):
        if self.__panelType == FilterPanelType.BARRACKS:
            filterUpdated = self.__state.updateBarracks(groupID, toggleID)
            if filterUpdated:
                self.__isSelectedMode = False
                self.onSelectedModeChange(self.__isSelectedMode)
                self.onUpdateToggle(toggleID == TankmanKind.TANKMAN.value)
                self.applyStateToModel()
        else:
            self.__state.updateMemberChange(groupID, toggleID)
            self.applyStateToModel()

    def __onResetFilter(self):
        if self.__isSelectedMode:
            self.onResetSelection()
        else:
            self.resetPopoverFilter()

    def __onPopoverStateUpdated(self):
        self.applyStateToModel()

    def __onSelectedModeChange(self):
        self.__isSelectedMode = not self.__isSelectedMode
        self.onSelectedModeChange(self.__isSelectedMode)
        self.applyStateToModel()

    def __fillModel(self, initial=False):
        with self.viewModel.transaction() as tx:
            if initial:
                tx.setTitle(self.__title)
                tx.setPopoverTooltipHeader(self.__popoverTooltipHeader)
                tx.setPopoverTooltipBody(self.__popoverTooltipBody)
                tx.setSearchPlaceholder(self.__searchPlaceholder)
                tx.setSearchTooltipHeader(self.__searchTooltipHeader)
                tx.setSearchTooltipBody(self.__searchTooltipBody)
                tx.setPanelType(self.__panelType)
                tx.setIsSearchEnabled(self.__isSearchEnabled)
                tx.setIsSelectButtonVisible(False)
            tx.setSearchString(self.__state.searchString)
            tx.setHasDiscountAlert(self.__hasDiscountAlert)
            tx.setIsPopoverHighlighted(False)
            filterState = self.__isSelectedMode if self.__isSelectedMode else self.hasAppliedFilters()
            tx.setHasAppliedFilters(filterState)
            self.refreshAmountInfo()
            self.__mainFilterSettings.pack(tx.filter, self.__state)
            if self.__popoverGroupSettings is None:
                tx.setIsPopoverEnabled(False)
                return
            for group in self.__popoverGroupSettings:
                if group.id in self.__state and self.__state[group.id]:
                    tx.setIsPopoverHighlighted(True)
                    break

        return

    def __fillBarracksModel(self):
        with self.viewModel.transaction() as tx:
            tx.setTitle(R.strings.crew.tankmanList.selected.title() if self.__isSelectedMode else self.__title)
            tx.setIsSelectButtonVisible(self.__getActiveFilterState() in {TankmanKind.TANKMAN.value, TankmanKind.UNIQUE.value, TankmanKind.DISMISSED.value})
            tx.setIsSelectedMode(self.__isSelectedMode)

    def enableSelectionButton(self, enable):
        with self.viewModel.transaction() as tx:
            tx.setIsSelectButtonActive(enable)

    def setSelectedLimitReached(self, reached):
        with self.viewModel.transaction() as tx:
            tx.setIsSelectedLimitReached(reached)

    def isSelectedMode(self):
        return self.__isSelectedMode

    def disableSelectedMode(self):
        self.__isSelectedMode = False
        self.applyStateToModel()

    def getActiveFilterTitle(self):
        activeFilter = self.__getActiveFilterState()
        for toggle in self.__mainFilterSettings.toggles:
            if toggle.id == activeFilter:
                return backport.text(toggle.tooltipHeader)

    def __getActiveFilterState(self):
        activeFilters = self.__state[ToggleGroupType.TANKMANKIND.value]
        return next(iter(activeFilters), None) if isinstance(activeFilters, set) else activeFilters
