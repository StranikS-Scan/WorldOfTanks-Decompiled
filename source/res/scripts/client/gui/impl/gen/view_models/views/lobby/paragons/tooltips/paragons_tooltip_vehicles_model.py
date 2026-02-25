# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/tooltips/paragons_tooltip_vehicles_model.py
from frameworks.wulf import ViewModel

class ParagonsTooltipVehiclesModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(ParagonsTooltipVehiclesModel, self).__init__(properties=properties, commands=commands)

    def getVehicleName(self):
        return self._getString(0)

    def setVehicleName(self, value):
        self._setString(0, value)

    def getVehicleNation(self):
        return self._getString(1)

    def setVehicleNation(self, value):
        self._setString(1, value)

    def getVehicleLvl(self):
        return self._getNumber(2)

    def setVehicleLvl(self, value):
        self._setNumber(2, value)

    def getVehicleUnlockPoints(self):
        return self._getNumber(3)

    def setVehicleUnlockPoints(self, value):
        self._setNumber(3, value)

    def getProgressionPoints(self):
        return self._getNumber(4)

    def setProgressionPoints(self, value):
        self._setNumber(4, value)

    def getVehicleType(self):
        return self._getString(5)

    def setVehicleType(self, value):
        self._setString(5, value)

    def getNeedRepair(self):
        return self._getBool(6)

    def setNeedRepair(self, value):
        self._setBool(6, value)

    def getIsInBattle(self):
        return self._getBool(7)

    def setIsInBattle(self, value):
        self._setBool(7, value)

    def getIsInPlatoonFormation(self):
        return self._getBool(8)

    def setIsInPlatoonFormation(self, value):
        self._setBool(8, value)

    def getNeedResearch(self):
        return self._getBool(9)

    def setNeedResearch(self, value):
        self._setBool(9, value)

    def getHasProgressionPoints(self):
        return self._getBool(10)

    def setHasProgressionPoints(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(ParagonsTooltipVehiclesModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleNation', '')
        self._addNumberProperty('vehicleLvl', 10)
        self._addNumberProperty('vehicleUnlockPoints', 0)
        self._addNumberProperty('progressionPoints', 0)
        self._addStringProperty('vehicleType', '')
        self._addBoolProperty('needRepair', True)
        self._addBoolProperty('isInBattle', True)
        self._addBoolProperty('isInPlatoonFormation', True)
        self._addBoolProperty('needResearch', True)
        self._addBoolProperty('hasProgressionPoints', True)
