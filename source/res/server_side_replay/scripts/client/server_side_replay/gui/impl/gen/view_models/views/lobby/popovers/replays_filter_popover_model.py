# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/impl/gen/view_models/views/lobby/popovers/replays_filter_popover_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array, ViewModel
from server_side_replay.gui.impl.gen.view_models.views.lobby.filter_toggle_group_model import FilterToggleGroupModel
from server_side_replay.gui.impl.gen.view_models.views.lobby.popovers.filter_popover_vehicle_model import FilterPopoverVehicleModel

class VehicleSortColumn(Enum):
    NAME = 'name'
    TIER = 'tier'
    TYPE = 'type'


class Checkboxes(IntEnum):
    PRIMETIME = 0


class ReplaysFilterPopoverModel(ViewModel):
    __slots__ = ('onCheckboxSelect', 'onLastDaysOptionSelect', 'onUpdateFilter', 'onSelectVehicle', 'onResetFilter', 'onApplyFilter', 'onSortVehiclesByColumn')

    def __init__(self, properties=8, commands=7):
        super(ReplaysFilterPopoverModel, self).__init__(properties=properties, commands=commands)

    def getFilterGroups(self):
        return self._getArray(0)

    def setFilterGroups(self, value):
        self._setArray(0, value)

    @staticmethod
    def getFilterGroupsType():
        return FilterToggleGroupModel

    def getVehicles(self):
        return self._getArray(1)

    def setVehicles(self, value):
        self._setArray(1, value)

    @staticmethod
    def getVehiclesType():
        return FilterPopoverVehicleModel

    def getVehicleSortColumn(self):
        return VehicleSortColumn(self._getString(2))

    def setVehicleSortColumn(self, value):
        self._setString(2, value.value)

    def getIsVehicleSortAscending(self):
        return self._getBool(3)

    def setIsVehicleSortAscending(self, value):
        self._setBool(3, value)

    def getCanResetFilter(self):
        return self._getBool(4)

    def setCanResetFilter(self, value):
        self._setBool(4, value)

    def getCanApplyFilter(self):
        return self._getBool(5)

    def setCanApplyFilter(self, value):
        self._setBool(5, value)

    def getIsPrimeTime(self):
        return self._getBool(6)

    def setIsPrimeTime(self, value):
        self._setBool(6, value)

    def getSelectedLastDays(self):
        return self._getNumber(7)

    def setSelectedLastDays(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(ReplaysFilterPopoverModel, self)._initialize()
        self._addArrayProperty('filterGroups', Array())
        self._addArrayProperty('vehicles', Array())
        self._addStringProperty('vehicleSortColumn')
        self._addBoolProperty('isVehicleSortAscending', True)
        self._addBoolProperty('canResetFilter', False)
        self._addBoolProperty('canApplyFilter', True)
        self._addBoolProperty('isPrimeTime', False)
        self._addNumberProperty('selectedLastDays', 14)
        self.onCheckboxSelect = self._addCommand('onCheckboxSelect')
        self.onLastDaysOptionSelect = self._addCommand('onLastDaysOptionSelect')
        self.onUpdateFilter = self._addCommand('onUpdateFilter')
        self.onSelectVehicle = self._addCommand('onSelectVehicle')
        self.onResetFilter = self._addCommand('onResetFilter')
        self.onApplyFilter = self._addCommand('onApplyFilter')
        self.onSortVehiclesByColumn = self._addCommand('onSortVehiclesByColumn')
