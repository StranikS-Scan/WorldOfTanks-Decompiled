# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/vehicle_info_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class VehicleInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(VehicleInfoModel, self).__init__(properties=properties, commands=commands)

    def getIsElite(self):
        return self._getBool(0)

    def setIsElite(self, value):
        self._setBool(0, value)

    def getVehicleName(self):
        return self._getString(1)

    def setVehicleName(self, value):
        self._setString(1, value)

    def getVehicleShortName(self):
        return self._getString(2)

    def setVehicleShortName(self, value):
        self._setString(2, value)

    def getVehicleNation(self):
        return self._getString(3)

    def setVehicleNation(self, value):
        self._setString(3, value)

    def getVehicleType(self):
        return self._getString(4)

    def setVehicleType(self, value):
        self._setString(4, value)

    def getVehicleLvl(self):
        return self._getNumber(5)

    def setVehicleLvl(self, value):
        self._setNumber(5, value)

    def getIsPremiumIGR(self):
        return self._getBool(6)

    def setIsPremiumIGR(self, value):
        self._setBool(6, value)

    def getTags(self):
        return self._getArray(7)

    def setTags(self, value):
        self._setArray(7, value)

    @staticmethod
    def getTagsType():
        return unicode

    def getVehicleTechName(self):
        return self._getString(8)

    def setVehicleTechName(self, value):
        self._setString(8, value)

    def getVehicleCD(self):
        return self._getNumber(9)

    def setVehicleCD(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(VehicleInfoModel, self)._initialize()
        self._addBoolProperty('isElite', True)
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleShortName', '')
        self._addStringProperty('vehicleNation', '')
        self._addStringProperty('vehicleType', '')
        self._addNumberProperty('vehicleLvl', 0)
        self._addBoolProperty('isPremiumIGR', False)
        self._addArrayProperty('tags', Array())
        self._addStringProperty('vehicleTechName', '')
        self._addNumberProperty('vehicleCD', 0)
