# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/sub_models/veh_skill_tree/alternate_configuration_dialog_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree.alternate_configuration_dialog_loadout_model import AlternateConfigurationDialogLoadoutModel

class AlternateConfigurationDialogModel(ViewModel):
    __slots__ = ('onClose', 'onAffirmate')

    def __init__(self, properties=3, commands=2):
        super(AlternateConfigurationDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    def getLoadouts(self):
        return self._getArray(1)

    def setLoadouts(self, value):
        self._setArray(1, value)

    @staticmethod
    def getLoadoutsType():
        return AlternateConfigurationDialogLoadoutModel

    def getNodeID(self):
        return self._getNumber(2)

    def setNodeID(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(AlternateConfigurationDialogModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addArrayProperty('loadouts', Array())
        self._addNumberProperty('nodeID', 0)
        self.onClose = self._addCommand('onClose')
        self.onAffirmate = self._addCommand('onAffirmate')
