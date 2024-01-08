# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/whats_new_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.comp7.schedule_info_model import ScheduleInfoModel

class WhatsNewViewModel(ViewModel):
    __slots__ = ('onClose', 'onVideoOpen')

    def __init__(self, properties=7, commands=2):
        super(WhatsNewViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def scheduleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getScheduleInfoType():
        return ScheduleInfoModel

    def getVehicleHealth(self):
        return self._getNumber(1)

    def setVehicleHealth(self, value):
        self._setNumber(1, value)

    def getEquipmentCooldown(self):
        return self._getNumber(2)

    def setEquipmentCooldown(self, value):
        self._setNumber(2, value)

    def getShotDispersionRadius(self):
        return self._getReal(3)

    def setShotDispersionRadius(self, value):
        self._setReal(3, value)

    def getVisionTime(self):
        return self._getNumber(4)

    def setVisionTime(self, value):
        self._setNumber(4, value)

    def getVisionMinRadius(self):
        return self._getNumber(5)

    def setVisionMinRadius(self, value):
        self._setNumber(5, value)

    def getVehicles(self):
        return self._getArray(6)

    def setVehicles(self, value):
        self._setArray(6, value)

    @staticmethod
    def getVehiclesType():
        return VehicleModel

    def _initialize(self):
        super(WhatsNewViewModel, self)._initialize()
        self._addViewModelProperty('scheduleInfo', ScheduleInfoModel())
        self._addNumberProperty('vehicleHealth', 125)
        self._addNumberProperty('equipmentCooldown', 45)
        self._addRealProperty('shotDispersionRadius', 50)
        self._addNumberProperty('visionTime', 3)
        self._addNumberProperty('visionMinRadius', 25)
        self._addArrayProperty('vehicles', Array())
        self.onClose = self._addCommand('onClose')
        self.onVideoOpen = self._addCommand('onVideoOpen')
