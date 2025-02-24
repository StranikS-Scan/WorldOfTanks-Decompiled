# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/impl/lobby/popovers/replays_filter_popover_view.py
import typing
import Event
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from server_side_replay.gui.impl.gen.view_models.views.lobby.filter_toggle_group_model import FilterToggleGroupModel
from server_side_replay.gui.impl.gen.view_models.views.lobby.popovers.filter_popover_vehicle_model import FilterPopoverVehicleModel
from server_side_replay.gui.impl.gen.view_models.views.lobby.popovers.replays_filter_popover_model import ReplaysFilterPopoverModel, VehicleSortColumn, Checkboxes
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from server_side_replay.gui.impl.lobby.sort_helpers import SortHeap
from server_side_replay.gui.impl.lobby.filter import VEHICLE_FILTER
from server_side_replay.gui.impl.lobby.utils import buildPopoverTankKeySortCriteria
from server_side_replay.gui.impl.lobby.filter.state import FilterState
from server_side_replay.gui.impl.lobby.utils import buildPopoverTankFilterCriteria
from gui.impl.pub import PopOverViewImpl
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from server_side_replay.gui.impl.lobby.filter import FilterGroupSettings as GroupSettings
    from typing import Iterable, Optional, Callable
    FilterGroups = Iterable[GroupSettings]

class ReplaysFilterPopoverView(PopOverViewImpl):
    __slots__ = ('__groupSettings', '__onStateUpdated', '__state', '__hasVehicleFilter', '__vehiclesSortColum', '__isVehicleSortAscending', '__canResetCallback', 'onTooltipCreated')
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, groupSettings, onStateUpdated, state=None, hasVehicleFilter=False, canResetCallback=None):
        settings = ViewSettings(layoutID=R.views.server_side_replay.lobby.popovers.ReplaysFilterPopover(), model=ReplaysFilterPopoverModel())
        super(ReplaysFilterPopoverView, self).__init__(settings)
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
        return super(ReplaysFilterPopoverView, self).getViewModel()

    def updateGroupSettings(self, groupSettings):
        self.__groupSettings = groupSettings
        self.__fillModel()

    def createToolTip(self, event):
        result = super(ReplaysFilterPopoverView, self).createToolTip(event)
        self.onTooltipCreated(event, result)
        return result

    def _getEvents(self):
        return ((self.viewModel.onUpdateFilter, self.__onUpdateFilter),
         (self.viewModel.onResetFilter, self.__onResetFilter),
         (self.viewModel.onApplyFilter, self.__onApplyFilter),
         (self.viewModel.onSortVehiclesByColumn, self.__onSortVehiclesByColumn),
         (self.viewModel.onSelectVehicle, self.__onSelectVehicle),
         (self.viewModel.onLastDaysOptionSelect, self.__onSelectVehicleLastDays),
         (self.viewModel.onCheckboxSelect, self.__onCheckboxSelect))

    def _onLoading(self, *args, **kwargs):
        super(ReplaysFilterPopoverView, self)._onLoading(*args, **kwargs)
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

    @args2params(int)
    def __onSelectVehicleLastDays(self, count):
        self.__state.lastDays = count
        self.__fillModel(updateVehicles=False)

    @args2params(int)
    def __onCheckboxSelect(self, checkboxId):
        if checkboxId == Checkboxes.PRIMETIME:
            self.__state.isPrimeTime = not self.__state.isPrimeTime
            self.__fillModel(updateVehicles=False)

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
        self.__fillModel()

    def __onResetFilter(self):
        self.__state.clear()
        self.__fillModel()

    def __onApplyFilter(self):
        self.__onStateUpdated()

    def __fillModel(self, updateVehicles=True):
        with self.viewModel.transaction() as tx:
            if self.__canResetCallback is not None:
                tx.setCanResetFilter(self.__canResetCallback())
            groups = tx.getFilterGroups()
            groups.clear()
            groups.invalidate()
            for settingGroup in self.__groupSettings:
                vm = FilterToggleGroupModel()
                settingGroup.pack(vm, self.__state)
                groups.addViewModel(vm)

            if self.__hasVehicleFilter and updateVehicles:
                self.__fillVehicleList(tx)
            tx.setSelectedLastDays(self.__state.lastDays)
            tx.setIsPrimeTime(self.__state.isPrimeTime)
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
