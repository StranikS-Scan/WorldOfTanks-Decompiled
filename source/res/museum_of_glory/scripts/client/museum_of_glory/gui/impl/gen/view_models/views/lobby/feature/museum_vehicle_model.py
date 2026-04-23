# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: museum_of_glory/scripts/client/museum_of_glory/gui/impl/gen/view_models/views/lobby/feature/museum_vehicle_model.py
from frameworks.wulf import Array
from museum_of_glory.gui.impl.gen.view_models.views.lobby.feature.museum_vehicle_characteristics import MuseumVehicleCharacteristics
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class MuseumVehicleModel(VehicleModel):
    __slots__ = ()

    def __init__(self, properties=16, commands=0):
        super(MuseumVehicleModel, self).__init__(properties=properties, commands=commands)

    def getYear(self):
        return self._getNumber(9)

    def setYear(self, value):
        self._setNumber(9, value)

    def getVehicleType(self):
        return self._getString(10)

    def setVehicleType(self, value):
        self._setString(10, value)

    def getNation(self):
        return self._getString(11)

    def setNation(self, value):
        self._setString(11, value)

    def getHistoricalText(self):
        return self._getString(12)

    def setHistoricalText(self, value):
        self._setString(12, value)

    def getTime(self):
        return self._getNumber(13)

    def setTime(self, value):
        self._setNumber(13, value)

    def getIsLoaded(self):
        return self._getBool(14)

    def setIsLoaded(self, value):
        self._setBool(14, value)

    def getCharacteristics(self):
        return self._getArray(15)

    def setCharacteristics(self, value):
        self._setArray(15, value)

    @staticmethod
    def getCharacteristicsType():
        return MuseumVehicleCharacteristics

    def _initialize(self):
        super(MuseumVehicleModel, self)._initialize()
        self._addNumberProperty('year', 0)
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('nation', '')
        self._addStringProperty('historicalText', '')
        self._addNumberProperty('time', 0)
        self._addBoolProperty('isLoaded', True)
        self._addArrayProperty('characteristics', Array())
