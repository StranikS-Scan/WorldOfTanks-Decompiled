# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/popovers/filter_popover_view.py
import typing
import Event
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.filter_toggle_group_model import FilterToggleGroupModel
from gui.impl.gen.view_models.views.lobby.crew.popovers.filter_popover_vehicle_model import FilterPopoverVehicleModel
from gui.impl.gen.view_models.views.lobby.crew.popovers.filter_popover_view_model import FilterPopoverViewModel, VehicleSortColumn
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.crew.crew_helpers.sort_helpers import SortHeap
from gui.impl.lobby.crew.filter import VEHICLE_FILTER
from gui.impl.lobby.crew.filter.state import FilterState
from gui.impl.lobby.crew.tooltips.dismissed_toggle_tooltip import DismissedToggleTooltip
from gui.impl.lobby.crew.utils import buildPopoverTankFilterCriteria, buildPopoverTankKeySortCriteria
from gui.impl.pub import PopOverViewImpl
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.impl.lobby.crew.filter import FilterGroupSettings as GroupSettings
    from typing import Iterable, Optional, Callable
    FilterGroups = Iterable[GroupSettings]

class FilterPopoverView(PopOverViewImpl):
    __slots__ = ('__title', '__groupSettings', '__onStateUpdated', '__state', '__hasVehicleFilter', '__vehiclesSortColum', '__isVehicleSortAscending', '__canResetCallback', 'onTooltipCreated')
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, title, groupSettings, onStateUpdated, state=None, hasVehicleFilter=False, canResetCallback=None):
        settings = ViewSettings(layoutID=R.views.lobby.crew.popovers.FilterPopoverView(), model=FilterPopoverViewModel())
        super(FilterPopoverView, self).__init__(settings)
        self.__title = title
        self.__groupSettings = groupSettings
        self.__onStateUpdated = onStateUpdated
        self.__state = state
        self.__hasVehicleFilter = hasVehicleFilter
        self.__vehiclesSortColum = VehicleSortColumn.TIER.value
        self.__isVehicleSortAscending = False
        self.__canResetCallback = canResetCallback
        self.onTooltipCreated = Event.Event()

    @property
    def viewModel(self):
        return super(FilterPopoverView, self).getViewModel()

    def updateGroupSettings(self, groupSettings):
        self.__groupSettings = groupSettings
        self.__fillModel()

    def createToolTip(self, event):
        result = super(FilterPopoverView, self).createToolTip(event)
        self.onTooltipCreated(event, result)
        return result

    def createToolTipContent(self, event, contentID):
        return DismissedToggleTooltip() if contentID == R.views.lobby.crew.tooltips.DismissedToggleTooltip() else super(FilterPopoverView, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((self.viewModel.onUpdateFilter, self.__onUpdateFilter),
         (self.viewModel.onResetFilter, self.__onResetFilter),
         (self.viewModel.onSortVehiclesByColumn, self.__onSortVehiclesByColumn),
         (self.viewModel.onSelectVehicle, self.__onSelectVehicle))

    def _onLoading(self, *args, **kwargs):
        super(FilterPopoverView, self)._onLoading(*args, **kwargs)
        self.__fillModel()

    @args2params(str, str)
    def __onUpdateFilter(self, groupID, toggleID):
        self.__state.update(groupID, toggleID)
        if self.__hasVehicleFilter and self.__state[VEHICLE_FILTER]:
            criteria = buildPopoverTankFilterCriteria(self.__state.state)
            criteria |= REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(self.__state[VEHICLE_FILTER])
            if not self.itemsCache.items.getVehicles(criteria):
                self.__state[VEHICLE_FILTER].clear()
        self.__fillModel()
        self.__onStateUpdated()

    @args2params(str)
    def __onSortVehiclesByColumn(self, column):
        if self.__vehiclesSortColum == column:
            self.__isVehicleSortAscending = not self.__isVehicleSortAscending
        else:
            self.__isVehicleSortAscending = column == VehicleSortColumn.NAME.value
        self.__vehiclesSortColum = column
        with self.viewModel.transaction() as tx:
            self.__fillVehicleList(tx)

    @args2params(int)
    def __onSelectVehicle(self, vehicleCD):
        if vehicleCD not in self.__state[VEHICLE_FILTER]:
            self.__state[VEHICLE_FILTER].clear()
        self.__state.update(VEHICLE_FILTER, vehicleCD)
        with self.viewModel.transaction() as tx:
            self.__fillVehicleList(tx)
        self.__onStateUpdated()

    def __onResetFilter(self):
        self.__state.clear()
        self.__fillModel()
        self.__onStateUpdated()

    def __fillModel(self):
        with self.viewModel.transaction() as tx:
            tx.setTitle(self.__title)
            if self.__canResetCallback is not None:
                tx.setCanResetFilter(self.__canResetCallback())
            groups = tx.getFilterGroups()
            groups.clear()
            groups.invalidate()
            for settingGroup in self.__groupSettings:
                vm = FilterToggleGroupModel()
                settingGroup.pack(vm, self.__state)
                groups.addViewModel(vm)

            if self.__hasVehicleFilter:
                tx.setHasVehicleFilter(True)
                self.__fillVehicleList(tx)
        return

    def __fillVehicleList(self, model):
        model.setIsVehicleSortAscending(self.__isVehicleSortAscending)
        model.setVehicleSortColumn(VehicleSortColumn(self.__vehiclesSortColum))
        vehicles = model.getVehicles()
        vehicles.clear()
        vehicles.invalidate()
        filteredVehicles = self.itemsCache.items.getVehicles(buildPopoverTankFilterCriteria(self.__state.state))
        vehicleSortHeap = SortHeap(items=filteredVehicles.values(), keys=buildPopoverTankKeySortCriteria(self.__vehiclesSortColum))
        vehicleList = vehicleSortHeap.getSortedList()
        if not self.__isVehicleSortAscending:
            vehicleList.reverse()
        for vehicle in vehicleList:
            vm = FilterPopoverVehicleModel()
            fillVehicleModel(vm, vehicle)
            vm.setIsSelected(vehicle.compactDescr in self.__state[VEHICLE_FILTER])
            vehicles.addViewModel(vm)
