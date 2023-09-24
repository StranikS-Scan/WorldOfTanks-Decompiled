# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/sub_views/vehicle_params_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.hangar.sub_views.vehicle_param_group_view_model import VehicleParamGroupViewModel

class VehicleParamsViewModel(ViewModel):
    __slots__ = ('onGroupClick',)

    def __init__(self, properties=1, commands=1):
        super(VehicleParamsViewModel, self).__init__(properties=properties, commands=commands)

    def getGroups(self):
        return self._getArray(0)

    def setGroups(self, value):
        self._setArray(0, value)

    @staticmethod
    def getGroupsType():
        return VehicleParamGroupViewModel

    def _initialize(self):
        super(VehicleParamsViewModel, self)._initialize()
        self._addArrayProperty('groups', Array())
        self.onGroupClick = self._addCommand('onGroupClick')
