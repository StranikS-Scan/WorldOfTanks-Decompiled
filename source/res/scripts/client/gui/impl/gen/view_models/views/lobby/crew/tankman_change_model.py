# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tankman_change_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class TankmanChangeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(TankmanChangeModel, self).__init__(properties=properties, commands=commands)

    def getNationName(self):
        return self._getString(0)

    def setNationName(self, value):
        self._setString(0, value)

    def getNationID(self):
        return self._getString(1)

    def setNationID(self, value):
        self._setString(1, value)

    def getNameID(self):
        return self._getString(2)

    def setNameID(self, value):
        self._setString(2, value)

    def getNameText(self):
        return self._getString(3)

    def setNameText(self, value):
        self._setString(3, value)

    def getSurnameID(self):
        return self._getString(4)

    def setSurnameID(self, value):
        self._setString(4, value)

    def getSurnameText(self):
        return self._getString(5)

    def setSurnameText(self, value):
        self._setString(5, value)

    def getIcon(self):
        return self._getResource(6)

    def setIcon(self, value):
        self._setResource(6, value)

    def getIsFemale(self):
        return self._getBool(7)

    def setIsFemale(self, value):
        self._setBool(7, value)

    def getVehType(self):
        return self._getString(8)

    def setVehType(self, value):
        self._setString(8, value)

    def getVehicleID(self):
        return self._getString(9)

    def setVehicleID(self, value):
        self._setString(9, value)

    def getVehicleName(self):
        return self._getString(10)

    def setVehicleName(self, value):
        self._setString(10, value)

    def getVehicleLevel(self):
        return self._getNumber(11)

    def setVehicleLevel(self, value):
        self._setNumber(11, value)

    def getSpecialty(self):
        return self._getString(12)

    def setSpecialty(self, value):
        self._setString(12, value)

    def getVehicleIcon(self):
        return self._getResource(13)

    def setVehicleIcon(self, value):
        self._setResource(13, value)

    def getIsEliteVehicle(self):
        return self._getBool(14)

    def setIsEliteVehicle(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(TankmanChangeModel, self)._initialize()
        self._addStringProperty('nationName', '')
        self._addStringProperty('nationID', '')
        self._addStringProperty('nameID', '')
        self._addStringProperty('nameText', '')
        self._addStringProperty('surnameID', '')
        self._addStringProperty('surnameText', '')
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('isFemale', False)
        self._addStringProperty('vehType', '')
        self._addStringProperty('vehicleID', '')
        self._addStringProperty('vehicleName', '')
        self._addNumberProperty('vehicleLevel', 0)
        self._addStringProperty('specialty', '')
        self._addResourceProperty('vehicleIcon', R.invalid())
        self._addBoolProperty('isEliteVehicle', False)
