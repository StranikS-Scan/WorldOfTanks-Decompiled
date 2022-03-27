# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/roster_view/roster_vehicle_specs_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_vehicle_ammunition_view_model import RosterVehicleAmmunitionViewModel
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_vehicle_crew_member_view_model import RosterVehicleCrewMemberViewModel
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_vehicle_equipment_view_model import RosterVehicleEquipmentViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_parameters.vehicle_parameters_view_model import VehicleParametersViewModel

class RosterVehicleSpecsViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(RosterVehicleSpecsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def parameters(self):
        return self._getViewModel(0)

    def getEquipment(self):
        return self._getArray(1)

    def setEquipment(self, value):
        self._setArray(1, value)

    def getConsumables(self):
        return self._getArray(2)

    def setConsumables(self, value):
        self._setArray(2, value)

    def getAmmunition(self):
        return self._getArray(3)

    def setAmmunition(self, value):
        self._setArray(3, value)

    def getCrew(self):
        return self._getArray(4)

    def setCrew(self, value):
        self._setArray(4, value)

    def _initialize(self):
        super(RosterVehicleSpecsViewModel, self)._initialize()
        self._addViewModelProperty('parameters', VehicleParametersViewModel())
        self._addArrayProperty('equipment', Array())
        self._addArrayProperty('consumables', Array())
        self._addArrayProperty('ammunition', Array())
        self._addArrayProperty('crew', Array())
