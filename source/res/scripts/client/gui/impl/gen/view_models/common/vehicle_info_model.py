# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/vehicle_info_model.py
from frameworks.wulf import ViewModel

class VehicleInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=17, commands=0):
        super(VehicleInfoModel, self).__init__(properties=properties, commands=commands)

    def getVehicleId(self):
        return self._getNumber(0)

    def setVehicleId(self, value):
        self._setNumber(0, value)

    def getInventoryId(self):
        return self._getNumber(1)

    def setInventoryId(self, value):
        self._setNumber(1, value)

    def getIsElite(self):
        return self._getBool(2)

    def setIsElite(self, value):
        self._setBool(2, value)

    def getIsPremium(self):
        return self._getBool(3)

    def setIsPremium(self, value):
        self._setBool(3, value)

    def getVehicleName(self):
        return self._getString(4)

    def setVehicleName(self, value):
        self._setString(4, value)

    def getVehicleShortName(self):
        return self._getString(5)

    def setVehicleShortName(self, value):
        self._setString(5, value)

    def getVehicleLongName(self):
        return self._getString(6)

    def setVehicleLongName(self, value):
        self._setString(6, value)

    def getVehicleNation(self):
        return self._getString(7)

    def setVehicleNation(self, value):
        self._setString(7, value)

    def getVehicleType(self):
        return self._getString(8)

    def setVehicleType(self, value):
        self._setString(8, value)

    def getVehicleRole(self):
        return self._getNumber(9)

    def setVehicleRole(self, value):
        self._setNumber(9, value)

    def getVehicleLvl(self):
        return self._getNumber(10)

    def setVehicleLvl(self, value):
        self._setNumber(10, value)

    def getTags(self):
        return self._getString(11)

    def setTags(self, value):
        self._setString(11, value)

    def getRentLeftTime(self):
        return self._getNumber(12)

    def setRentLeftTime(self, value):
        self._setNumber(12, value)

    def getRentLeftBattles(self):
        return self._getNumber(13)

    def setRentLeftBattles(self, value):
        self._setNumber(13, value)

    def getRentLeftWins(self):
        return self._getNumber(14)

    def setRentLeftWins(self, value):
        self._setNumber(14, value)

    def getState(self):
        return self._getString(15)

    def setState(self, value):
        self._setString(15, value)

    def getFromWotPlus(self):
        return self._getBool(16)

    def setFromWotPlus(self, value):
        self._setBool(16, value)

    def _initialize(self):
        super(VehicleInfoModel, self)._initialize()
        self._addNumberProperty('vehicleId', 0)
        self._addNumberProperty('inventoryId', 0)
        self._addBoolProperty('isElite', True)
        self._addBoolProperty('isPremium', False)
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleShortName', '')
        self._addStringProperty('vehicleLongName', '')
        self._addStringProperty('vehicleNation', '')
        self._addStringProperty('vehicleType', '')
        self._addNumberProperty('vehicleRole', 0)
        self._addNumberProperty('vehicleLvl', 0)
        self._addStringProperty('tags', '')
        self._addNumberProperty('rentLeftTime', 0)
        self._addNumberProperty('rentLeftBattles', 0)
        self._addNumberProperty('rentLeftWins', 0)
        self._addStringProperty('state', '')
        self._addBoolProperty('fromWotPlus', False)
