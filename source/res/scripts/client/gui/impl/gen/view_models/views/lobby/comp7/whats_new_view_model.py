# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/whats_new_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.comp7.schedule_info_model import ScheduleInfoModel

class WhatsNewViewModel(ViewModel):
    __slots__ = ('onClose', 'onVideoOpen')

    def __init__(self, properties=3, commands=2):
        super(WhatsNewViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def scheduleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getScheduleInfoType():
        return ScheduleInfoModel

    def getVehicles(self):
        return self._getArray(1)

    def setVehicles(self, value):
        self._setArray(1, value)

    @staticmethod
    def getVehiclesType():
        return VehicleModel

    def getReconFlightDelay(self):
        return self._getReal(2)

    def setReconFlightDelay(self, value):
        self._setReal(2, value)

    def _initialize(self):
        super(WhatsNewViewModel, self)._initialize()
        self._addViewModelProperty('scheduleInfo', ScheduleInfoModel())
        self._addArrayProperty('vehicles', Array())
        self._addRealProperty('reconFlightDelay', 0.0)
        self.onClose = self._addCommand('onClose')
        self.onVideoOpen = self._addCommand('onVideoOpen')
