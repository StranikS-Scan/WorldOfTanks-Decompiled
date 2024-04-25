# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/progression/progression_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.battle_quests_model import BattleQuestsModel
from historical_battles.gui.impl.gen.view_models.views.lobby.progression.progress_level_model import ProgressLevelModel

class ProgressionState(Enum):
    INPROGRESS = 'inProgress'
    COMPLETED = 'completed'


class ProgressionViewModel(ViewModel):
    __slots__ = ('onClose', 'onAboutClicked', 'onPreviewClicked', 'onVehicleBuyClicked')

    def __init__(self, properties=8, commands=4):
        super(ProgressionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def battleQuests(self):
        return self._getViewModel(0)

    @staticmethod
    def getBattleQuestsType():
        return BattleQuestsModel

    def getState(self):
        return ProgressionState(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getCurProgressPoints(self):
        return self._getNumber(2)

    def setCurProgressPoints(self, value):
        self._setNumber(2, value)

    def getPrevProgressPoints(self):
        return self._getNumber(3)

    def setPrevProgressPoints(self, value):
        self._setNumber(3, value)

    def getVehicleDiscount(self):
        return self._getNumber(4)

    def setVehicleDiscount(self, value):
        self._setNumber(4, value)

    def getHasVehicle(self):
        return self._getBool(5)

    def setHasVehicle(self, value):
        self._setBool(5, value)

    def getPointsForLevel(self):
        return self._getArray(6)

    def setPointsForLevel(self, value):
        self._setArray(6, value)

    @staticmethod
    def getPointsForLevelType():
        return int

    def getProgressLevels(self):
        return self._getArray(7)

    def setProgressLevels(self, value):
        self._setArray(7, value)

    @staticmethod
    def getProgressLevelsType():
        return ProgressLevelModel

    def _initialize(self):
        super(ProgressionViewModel, self)._initialize()
        self._addViewModelProperty('battleQuests', BattleQuestsModel())
        self._addStringProperty('state')
        self._addNumberProperty('curProgressPoints', 0)
        self._addNumberProperty('prevProgressPoints', 0)
        self._addNumberProperty('vehicleDiscount', 0)
        self._addBoolProperty('hasVehicle', False)
        self._addArrayProperty('pointsForLevel', Array())
        self._addArrayProperty('progressLevels', Array())
        self.onClose = self._addCommand('onClose')
        self.onAboutClicked = self._addCommand('onAboutClicked')
        self.onPreviewClicked = self._addCommand('onPreviewClicked')
        self.onVehicleBuyClicked = self._addCommand('onVehicleBuyClicked')
