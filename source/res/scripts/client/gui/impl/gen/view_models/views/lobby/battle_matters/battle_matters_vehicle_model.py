# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_matters/battle_matters_vehicle_model.py
from frameworks.wulf import ViewModel

class BattleMattersVehicleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(BattleMattersVehicleModel, self).__init__(properties=properties, commands=commands)

    def getIndex(self):
        return self._getNumber(0)

    def setIndex(self, value):
        self._setNumber(0, value)

    def getIsElite(self):
        return self._getBool(1)

    def setIsElite(self, value):
        self._setBool(1, value)

    def getIsInHangar(self):
        return self._getBool(2)

    def setIsInHangar(self, value):
        self._setBool(2, value)

    def getVehCD(self):
        return self._getNumber(3)

    def setVehCD(self, value):
        self._setNumber(3, value)

    def getRentLength(self):
        return self._getNumber(4)

    def setRentLength(self, value):
        self._setNumber(4, value)

    def getLevel(self):
        return self._getNumber(5)

    def setLevel(self, value):
        self._setNumber(5, value)

    def getVehType(self):
        return self._getString(6)

    def setVehType(self, value):
        self._setString(6, value)

    def getVehName(self):
        return self._getString(7)

    def setVehName(self, value):
        self._setString(7, value)

    def getUserName(self):
        return self._getString(8)

    def setUserName(self, value):
        self._setString(8, value)

    def getNation(self):
        return self._getString(9)

    def setNation(self, value):
        self._setString(9, value)

    def getTooltipId(self):
        return self._getString(10)

    def setTooltipId(self, value):
        self._setString(10, value)

    def getTooltipContentId(self):
        return self._getString(11)

    def setTooltipContentId(self, value):
        self._setString(11, value)

    def _initialize(self):
        super(BattleMattersVehicleModel, self)._initialize()
        self._addNumberProperty('index', 0)
        self._addBoolProperty('isElite', False)
        self._addBoolProperty('isInHangar', False)
        self._addNumberProperty('vehCD', 0)
        self._addNumberProperty('rentLength', 0)
        self._addNumberProperty('level', 0)
        self._addStringProperty('vehType', '')
        self._addStringProperty('vehName', '')
        self._addStringProperty('userName', '')
        self._addStringProperty('nation', '')
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('tooltipContentId', '')
