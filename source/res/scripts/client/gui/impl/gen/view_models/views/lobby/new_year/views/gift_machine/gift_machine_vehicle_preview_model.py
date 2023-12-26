# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/gift_machine/gift_machine_vehicle_preview_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class GiftMachineVehiclePreviewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(GiftMachineVehiclePreviewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    def getRentDays(self):
        return self._getNumber(1)

    def setRentDays(self, value):
        self._setNumber(1, value)

    def getRentBattles(self):
        return self._getNumber(2)

    def setRentBattles(self, value):
        self._setNumber(2, value)

    def getVehIntCD(self):
        return self._getNumber(3)

    def setVehIntCD(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(GiftMachineVehiclePreviewModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addNumberProperty('rentDays', 0)
        self._addNumberProperty('rentBattles', 0)
        self._addNumberProperty('vehIntCD', 0)
