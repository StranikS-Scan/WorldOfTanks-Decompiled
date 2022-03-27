# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_parameters/vehicle_parameters.py
import typing
from helpers import dependency
from gui.impl.gui_decorators import args2params
from gui.shared.items_parameters import RELATIVE_PARAMS
from gui.shared.items_parameters.params_helper import getParameters, PARAMS_GROUPS, idealCrewComparator
from skeletons.gui.shared import IItemsCache
from account_helpers.AccountSettings import AccountSettings
from gui.impl.gen.view_models.views.lobby.vehicle_parameters.vehicle_parameters_view_model import VehicleParametersViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_parameters.vehicle_parameter_group_view_model import VehicleParameterGroupViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_parameters.vehicle_parameter_view_model import VehicleParameterViewModel
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.shared.items_parameters.comparator import VehiclesComparator, _ParameterInfo

class VehicleParameters(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, model):
        self._vehicle = None
        self._comparator = None
        self._stockVehicle = None
        self._model = model
        if self._model:
            self._model.onParameterGroupClick += self.toggleGroup
        return

    def __del__(self):
        if self._model:
            self._model.onParameterGroupClick -= self.toggleGroup

    def setVehicle(self, vehicle, forceUpdate=False):
        self._vehicle = vehicle
        if self._vehicle:
            self._comparator = self._getComparator(self._vehicle)
            self._stockVehicle = self._getStockVehicle(self._vehicle.intCD)
        else:
            self._comparator = None
            self._stockVehicle = None
        if forceUpdate:
            self.updateViewModel()
        return

    def getParameterGroups(self):
        return RELATIVE_PARAMS

    def getParametersForGroup(self, groupName):
        return PARAMS_GROUPS.get(groupName, tuple())

    def updateViewModel(self):
        groupNames = self.getParameterGroups()
        with self._model.transaction() as vm:
            groupsArray = vm.getGroups()
            groupsArray.clear()
            if self._vehicle:
                groupsArray.reserve(len(groupNames))
                for groupName in groupNames:
                    group = self._comparator.getExtendedData(groupName)
                    groupEntry = self._createGroup(group)
                    items = groupEntry.getItems()
                    for paramName in self.getParametersForGroup(groupName):
                        param = self._comparator.getExtendedData(paramName)
                        paramEntry = self._createParameter(param)
                        if paramEntry:
                            items.addViewModel(paramEntry)

                    groupsArray.addViewModel(groupEntry)

            groupsArray.invalidate()
            return vm

    @args2params(str)
    def toggleGroup(self, groupName):
        newState = self._toggleGroupExpandedState(groupName)
        groupsArray = self._model.getGroups()
        for group in groupsArray:
            if group.getName() == groupName:
                group.setIsExpanded(newState)
                groupsArray.invalidate()
                break

        return self._model

    def _getComparator(self, vehicle):
        return idealCrewComparator(vehicle)

    def _getStockVehicle(self, vehicleIntCd):
        return self.itemsCache.items.getStockVehicle(vehicleIntCd)

    def _isGroupExpanded(self, groupName):
        return AccountSettings.getSettings(groupName)

    def _toggleGroupExpandedState(self, groupName):
        newState = not bool(self._isGroupExpanded(groupName))
        AccountSettings.setSettings(groupName, newState)
        return newState

    def _getParameterValues(self, param):
        return (param.value,) if not isinstance(param.value, (tuple, list)) else param.value

    def _createParameter(self, param):
        if not param.value:
            return None
        else:
            paramModel = VehicleParameterViewModel()
            paramModel.setName(param.name)
            modelValue = paramModel.getParameterValues()
            for value in self._getParameterValues(param):
                modelValue.addReal(value)

            return paramModel

    def _createGroup(self, group):
        stockParams = getParameters(self._stockVehicle)
        groupModel = VehicleParameterGroupViewModel()
        groupModel.setName(group.name)
        groupModel.setCurrentValue(group.value)
        groupModel.setOriginalValue(stockParams[group.name])
        groupModel.setIsExpanded(self._isGroupExpanded(group.name))
        return groupModel
