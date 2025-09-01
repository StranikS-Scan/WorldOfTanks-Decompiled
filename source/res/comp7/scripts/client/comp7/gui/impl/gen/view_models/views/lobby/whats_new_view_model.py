# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/whats_new_view_model.py
from frameworks.wulf import Array, ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.schedule_info_model import ScheduleInfoModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class WhatsNewViewModel(ViewModel):
    __slots__ = ('onClose', 'onVideoOpen')

    def __init__(self, properties=4, commands=2):
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

    def getNewAvailableVehicles(self):
        return self._getArray(2)

    def setNewAvailableVehicles(self, value):
        self._setArray(2, value)

    @staticmethod
    def getNewAvailableVehiclesType():
        return VehicleModel

    def getTopPercentage(self):
        return self._getNumber(3)

    def setTopPercentage(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(WhatsNewViewModel, self)._initialize()
        self._addViewModelProperty('scheduleInfo', ScheduleInfoModel())
        self._addArrayProperty('vehicles', Array())
        self._addArrayProperty('newAvailableVehicles', Array())
        self._addNumberProperty('topPercentage', 0)
        self.onClose = self._addCommand('onClose')
        self.onVideoOpen = self._addCommand('onVideoOpen')
