# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/maps_training/maps_training_selected_map_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.maps_training.maps_training_minimap_point import MapsTrainingMinimapPoint
from gui.impl.gen.view_models.views.lobby.maps_training.maps_training_scenario_model import MapsTrainingScenarioModel

class MapsTrainingSelectedMapModel(ViewModel):
    __slots__ = ()
    MINIMAP_SIZE_DEFAULT = 570
    MINIMAP_SIZE_SMALL = 332

    def __init__(self, properties=10, commands=0):
        super(MapsTrainingSelectedMapModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getImage(self):
        return self._getResource(1)

    def setImage(self, value):
        self._setResource(1, value)

    def getScenarioImage(self):
        return self._getResource(2)

    def setScenarioImage(self, value):
        self._setResource(2, value)

    def getSelectedScenario(self):
        return self._getNumber(3)

    def setSelectedScenario(self, value):
        self._setNumber(3, value)

    def getVehicleName(self):
        return self._getString(4)

    def setVehicleName(self, value):
        self._setString(4, value)

    def getGroupId(self):
        return self._getNumber(5)

    def setGroupId(self, value):
        self._setNumber(5, value)

    def getIsShowCompleteAnimation(self):
        return self._getBool(6)

    def setIsShowCompleteAnimation(self, value):
        self._setBool(6, value)

    def getPoints(self):
        return self._getArray(7)

    def setPoints(self, value):
        self._setArray(7, value)

    @staticmethod
    def getPointsType():
        return MapsTrainingMinimapPoint

    def getScenarios(self):
        return self._getArray(8)

    def setScenarios(self, value):
        self._setArray(8, value)

    @staticmethod
    def getScenariosType():
        return MapsTrainingScenarioModel

    def getRewards(self):
        return self._getArray(9)

    def setRewards(self, value):
        self._setArray(9, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def _initialize(self):
        super(MapsTrainingSelectedMapModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addResourceProperty('image', R.invalid())
        self._addResourceProperty('scenarioImage', R.invalid())
        self._addNumberProperty('selectedScenario', 0)
        self._addStringProperty('vehicleName', '')
        self._addNumberProperty('groupId', 0)
        self._addBoolProperty('isShowCompleteAnimation', False)
        self._addArrayProperty('points', Array())
        self._addArrayProperty('scenarios', Array())
        self._addArrayProperty('rewards', Array())
