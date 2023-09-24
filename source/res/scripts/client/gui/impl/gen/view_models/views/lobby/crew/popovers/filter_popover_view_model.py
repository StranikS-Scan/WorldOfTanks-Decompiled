# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/popovers/filter_popover_view_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.filter_toggle_group_model import FilterToggleGroupModel
from gui.impl.gen.view_models.views.lobby.crew.popovers.filter_popover_vehicle_model import FilterPopoverVehicleModel

class VehicleSortColumn(Enum):
    NAME = 'name'
    TIER = 'tier'
    TYPE = 'type'


class FilterPopoverViewModel(ViewModel):
    __slots__ = ('onUpdateFilter', 'onSelectVehicle', 'onResetFilter', 'onSortVehiclesByColumn')

    def __init__(self, properties=7, commands=4):
        super(FilterPopoverViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getFilterGroups(self):
        return self._getArray(1)

    def setFilterGroups(self, value):
        self._setArray(1, value)

    @staticmethod
    def getFilterGroupsType():
        return FilterToggleGroupModel

    def getVehicles(self):
        return self._getArray(2)

    def setVehicles(self, value):
        self._setArray(2, value)

    @staticmethod
    def getVehiclesType():
        return FilterPopoverVehicleModel

    def getVehicleSortColumn(self):
        return VehicleSortColumn(self._getString(3))

    def setVehicleSortColumn(self, value):
        self._setString(3, value.value)

    def getIsVehicleSortAscending(self):
        return self._getBool(4)

    def setIsVehicleSortAscending(self, value):
        self._setBool(4, value)

    def getHasVehicleFilter(self):
        return self._getBool(5)

    def setHasVehicleFilter(self, value):
        self._setBool(5, value)

    def getCanResetFilter(self):
        return self._getBool(6)

    def setCanResetFilter(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(FilterPopoverViewModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addArrayProperty('filterGroups', Array())
        self._addArrayProperty('vehicles', Array())
        self._addStringProperty('vehicleSortColumn')
        self._addBoolProperty('isVehicleSortAscending', True)
        self._addBoolProperty('hasVehicleFilter', False)
        self._addBoolProperty('canResetFilter', False)
        self.onUpdateFilter = self._addCommand('onUpdateFilter')
        self.onSelectVehicle = self._addCommand('onSelectVehicle')
        self.onResetFilter = self._addCommand('onResetFilter')
        self.onSortVehiclesByColumn = self._addCommand('onSortVehiclesByColumn')
