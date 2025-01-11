# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/personal_missions_vehicle_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_vehicle_model import Pm3VehicleModel

class PersonalMissionsVehicleViewModel(ViewModel):
    __slots__ = ('onCompare', 'onShowVehiclePreview', 'onShowInHangar', 'onBackToHangar', 'onMoveSpace', 'onStartMoving', 'onRestoreVehicle')
    ARG_VEHICLE_CD = 'vehicleCD'

    def __init__(self, properties=3, commands=7):
        super(PersonalMissionsVehicleViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleType():
        return Pm3VehicleModel

    def getCurrentVehicleCD(self):
        return self._getNumber(1)

    def setCurrentVehicleCD(self, value):
        self._setNumber(1, value)

    def getOperationName(self):
        return self._getString(2)

    def setOperationName(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(PersonalMissionsVehicleViewModel, self)._initialize()
        self._addViewModelProperty('vehicle', Pm3VehicleModel())
        self._addNumberProperty('currentVehicleCD', 0)
        self._addStringProperty('operationName', '')
        self.onCompare = self._addCommand('onCompare')
        self.onShowVehiclePreview = self._addCommand('onShowVehiclePreview')
        self.onShowInHangar = self._addCommand('onShowInHangar')
        self.onBackToHangar = self._addCommand('onBackToHangar')
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onStartMoving = self._addCommand('onStartMoving')
        self.onRestoreVehicle = self._addCommand('onRestoreVehicle')
