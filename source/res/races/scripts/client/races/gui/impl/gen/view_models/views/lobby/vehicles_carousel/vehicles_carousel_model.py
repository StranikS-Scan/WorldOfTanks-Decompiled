# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/lobby/vehicles_carousel/vehicles_carousel_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from races.gui.impl.gen.view_models.views.lobby.vehicles_carousel.races_vehicle_info_model import RacesVehicleInfoModel

class VehiclesCarouselModel(ViewModel):
    __slots__ = ('onVehicleSelect',)

    def __init__(self, properties=3, commands=1):
        super(VehiclesCarouselModel, self).__init__(properties=properties, commands=commands)

    def getVehicleName(self):
        return self._getString(0)

    def setVehicleName(self, value):
        self._setString(0, value)

    def getVehicleUserName(self):
        return self._getString(1)

    def setVehicleUserName(self, value):
        self._setString(1, value)

    def getVehiclesInfo(self):
        return self._getArray(2)

    def setVehiclesInfo(self, value):
        self._setArray(2, value)

    @staticmethod
    def getVehiclesInfoType():
        return RacesVehicleInfoModel

    def _initialize(self):
        super(VehiclesCarouselModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleUserName', '')
        self._addArrayProperty('vehiclesInfo', Array())
        self.onVehicleSelect = self._addCommand('onVehicleSelect')
