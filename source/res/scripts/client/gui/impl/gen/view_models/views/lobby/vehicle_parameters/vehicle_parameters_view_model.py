# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_parameters/vehicle_parameters_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_parameters.vehicle_parameter_group_view_model import VehicleParameterGroupViewModel

class VehicleParametersViewModel(ViewModel):
    __slots__ = ('onParameterGroupClick',)

    def __init__(self, properties=1, commands=1):
        super(VehicleParametersViewModel, self).__init__(properties=properties, commands=commands)

    def getGroups(self):
        return self._getArray(0)

    def setGroups(self, value):
        self._setArray(0, value)

    def _initialize(self):
        super(VehicleParametersViewModel, self)._initialize()
        self._addArrayProperty('groups', Array())
        self.onParameterGroupClick = self._addCommand('onParameterGroupClick')
