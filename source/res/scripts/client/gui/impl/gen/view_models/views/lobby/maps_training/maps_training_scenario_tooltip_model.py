# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/maps_training/maps_training_scenario_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class MapsTrainingScenarioTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(MapsTrainingScenarioTooltipModel, self).__init__(properties=properties, commands=commands)

    def getVehicleType(self):
        return self._getString(0)

    def setVehicleType(self, value):
        self._setString(0, value)

    def getTeam(self):
        return self._getNumber(1)

    def setTeam(self, value):
        self._setNumber(1, value)

    def getScenarioNum(self):
        return self._getNumber(2)

    def setScenarioNum(self, value):
        self._setNumber(2, value)

    def getMapId(self):
        return self._getString(3)

    def setMapId(self, value):
        self._setString(3, value)

    def getTargets(self):
        return self._getArray(4)

    def setTargets(self, value):
        self._setArray(4, value)

    @staticmethod
    def getTargetsType():
        return str

    def getVehicleName(self):
        return self._getString(5)

    def setVehicleName(self, value):
        self._setString(5, value)

    def getIsComplete(self):
        return self._getBool(6)

    def setIsComplete(self, value):
        self._setBool(6, value)

    def getRewards(self):
        return self._getArray(7)

    def setRewards(self, value):
        self._setArray(7, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def _initialize(self):
        super(MapsTrainingScenarioTooltipModel, self)._initialize()
        self._addStringProperty('vehicleType', '')
        self._addNumberProperty('team', 0)
        self._addNumberProperty('scenarioNum', 0)
        self._addStringProperty('mapId', '')
        self._addArrayProperty('targets', Array())
        self._addStringProperty('vehicleName', '')
        self._addBoolProperty('isComplete', False)
        self._addArrayProperty('rewards', Array())
