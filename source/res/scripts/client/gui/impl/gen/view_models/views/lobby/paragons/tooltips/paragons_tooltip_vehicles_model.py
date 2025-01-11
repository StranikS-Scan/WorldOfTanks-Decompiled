# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/tooltips/paragons_tooltip_vehicles_model.py
from frameworks.wulf import ViewModel

class ParagonsTooltipVehiclesModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
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

    def getVehicleType(self):
        return self._getString(3)

    def setVehicleType(self, value):
        self._setString(3, value)

    def getHasProgressionPoints(self):
        return self._getBool(4)

    def setHasProgressionPoints(self, value):
        self._setBool(4, value)

    def getNeedRepair(self):
        return self._getBool(5)

    def setNeedRepair(self, value):
        self._setBool(5, value)

    def getIsInBattle(self):
        return self._getBool(6)

    def setIsInBattle(self, value):
        self._setBool(6, value)

    def getIsInPlatoonFormation(self):
        return self._getBool(7)

    def setIsInPlatoonFormation(self, value):
        self._setBool(7, value)

    def getNeedResearch(self):
        return self._getBool(8)

    def setNeedResearch(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(ParagonsTooltipVehiclesModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleNation', '')
        self._addNumberProperty('vehicleLvl', 10)
        self._addStringProperty('vehicleType', '')
        self._addBoolProperty('hasProgressionPoints', True)
        self._addBoolProperty('needRepair', True)
        self._addBoolProperty('isInBattle', True)
        self._addBoolProperty('isInPlatoonFormation', True)
        self._addBoolProperty('needResearch', True)
