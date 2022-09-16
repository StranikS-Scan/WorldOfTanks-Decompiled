# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/views/no_vehicles_screen_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.schedule_info_model import ScheduleInfoModel

class ErrorReason(Enum):
    DEFAULT = 'vehicleUnavailable'
    NOT_BOUGHT_VEHICLES = 'vehicleAvailableForBuy'
    CAN_RECOVER_VEHICLES = 'vehicleAvailableForRestore'


class NoVehiclesScreenModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=3, commands=1):
        super(NoVehiclesScreenModel, self).__init__(properties=properties, commands=commands)

    @property
    def scheduleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getScheduleInfoType():
        return ScheduleInfoModel

    def getVehicleLevels(self):
        return self._getArray(1)

    def setVehicleLevels(self, value):
        self._setArray(1, value)

    @staticmethod
    def getVehicleLevelsType():
        return int

    def getErrorReason(self):
        return ErrorReason(self._getString(2))

    def setErrorReason(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(NoVehiclesScreenModel, self)._initialize()
        self._addViewModelProperty('scheduleInfo', ScheduleInfoModel())
        self._addArrayProperty('vehicleLevels', Array())
        self._addStringProperty('errorReason')
        self.onClose = self._addCommand('onClose')
