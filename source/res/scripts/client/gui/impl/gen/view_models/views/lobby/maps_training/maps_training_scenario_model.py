# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/maps_training/maps_training_scenario_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class MapsTrainingScenarioModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(MapsTrainingScenarioModel, self).__init__(properties=properties, commands=commands)

    def getTeam(self):
        return self._getNumber(0)

    def setTeam(self, value):
        self._setNumber(0, value)

    def getScenarioNum(self):
        return self._getNumber(1)

    def setScenarioNum(self, value):
        self._setNumber(1, value)

    def getVehicleType(self):
        return self._getString(2)

    def setVehicleType(self, value):
        self._setString(2, value)

    def getIsComplete(self):
        return self._getBool(3)

    def setIsComplete(self, value):
        self._setBool(3, value)

    def getRewards(self):
        return self._getArray(4)

    def setRewards(self, value):
        self._setArray(4, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def _initialize(self):
        super(MapsTrainingScenarioModel, self)._initialize()
        self._addNumberProperty('team', 0)
        self._addNumberProperty('scenarioNum', 0)
        self._addStringProperty('vehicleType', '')
        self._addBoolProperty('isComplete', False)
        self._addArrayProperty('rewards', Array())
